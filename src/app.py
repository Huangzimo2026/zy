import streamlit as st
from datetime import datetime
from api import call_ai
from prompt import check_question_relevant, build_user_prompt, get_system_prompt_by_role
from knowledge import search_knowledge, load_all_knowledge

# 页面配置
st.set_page_config(page_title="小航AI助手", page_icon="✈️", layout="wide")

# ========== 隐藏右上角 Deploy 按钮 ==========
hide_deploy_css = """
<style>
header button[aria-label*="Deploy"],
header button[data-testid="baseButton-secondary"],
.stApp header button:first-child,
div[role="banner"] button:first-of-type {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    pointer-events: none !important;
}
</style>
"""
st.markdown(hide_deploy_css, unsafe_allow_html=True)

# ========== 初始化 session_state ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好呀！我是小航，有任何校园问题都可以问我~"}
    ]
if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "role" not in st.session_state:
    st.session_state.role = "新生"

# 标题
st.title("✈️ 小航AI助手 - 郑航校园智能咨询")
st.markdown("---")

# ========== 侧边栏 ==========
with st.sidebar:
    st.header("📑 校园黄页")
    st.markdown("""
    **校区地址**
    - 龙子湖校区：郑州市郑东新区文苑西路15号
    - 大学路校区：郑州市二七区大学中路2号

    **作息时间**
    - 周日-周四 23:00断电（空调持续供电）
    - 周五-周六 23:30断电（空调持续供电）

    **常用入口**
    - 教务系统：通过学校官网或企业微信进入
    - 图书馆：8:00-22:00开放
    """)
    st.markdown("---")
    st.caption("郑州航空工业管理学院 认知实习项目")

    st.markdown("---")
    st.subheader("📜 对话历史")
    if st.session_state.history:
        for idx, item in enumerate(reversed(st.session_state.history)):
            display_time = item.get('time', '')
            display_role = item.get('role', '未知身份')
            display_question = item.get('question', '')
            display_answer = item.get('answer', '')
            title = f"[{display_time}] {display_role} 提问：{display_question[:30]}{'...' if len(display_question) > 30 else ''}"
            with st.expander(title):
                st.markdown(f"**完整问题：** {display_question}")
                st.markdown(f"**回答：** {display_answer}")
    else:
        st.caption("暂无对话记录，提问后自动保存")

    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("重置聊天", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "你好呀！我是小航，有任何校园问题都可以问我~"}
            ]
            st.rerun()
    with col_btn2:
        if st.button("清空历史", use_container_width=True):
            st.session_state.history = []
            st.rerun()

# ========== 身份选择 ==========
role = st.selectbox("请选择你的身份：", ["新生", "在校生", "教师"], index=0, key="role_selector")
st.session_state.role = role

# ========== 推荐问题（12个） ==========
st.subheader("💡 常见问题 一键提问")

if role == "新生":
    questions = ["报到那天先去哪？", "学费什么时候交？", "宿舍是4人间还是6人间？", "有人冒充辅导员要钱怎么办？"]
elif role == "在校生":
    questions = ["怎么开在读证明？", "校园卡丢了怎么补？", "转专业怎么转？", "图书馆几点关？"]
else:
    questions = ["差旅怎么报销？", "调课怎么申请？", "教室设备坏了找谁？", "科研项目去哪申报？"]

cols = st.columns(4)
for i, q in enumerate(questions):
    with cols[i]:
        if st.button(q):
            st.session_state.pending_question = q

st.markdown("---")

# ========== 渲染聊天消息 ==========
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ========== 输入框 ==========
user_input = st.chat_input("输入你的校园问题...")

# 处理推荐按钮触发（自动填入）
if st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = ""

# ========== 问答逻辑 ==========
if user_input:
    # 检测是否为追问
    is_followup = False
    if not check_question_relevant(user_input) and len(st.session_state.messages) >= 2:
        last_user_msg = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break
        if last_user_msg and check_question_relevant(last_user_msg):
            is_followup = True

    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("小航正在检索知识库并思考..."):
            try:
                if not check_question_relevant(user_input) and not is_followup:
                    reply = "抱歉呀，我只能解答郑航校园相关的问题哦~ 换个校园问题试试吧。"
                else:
                    match_answer = search_knowledge(user_input)
                    if match_answer:
                        reply = match_answer
                    else:
                        full_knowledge = load_all_knowledge()
                        system_rule = get_system_prompt_by_role(role)

                        recent = st.session_state.messages[-6:-1] if len(st.session_state.messages) > 1 else []
                        context_parts = []
                        for msg in recent:
                            if msg["role"] == "user":
                                context_parts.append(f"用户之前问：{msg['content']}")
                            elif msg["role"] == "assistant":
                                context_parts.append(f"小航之前答：{msg['content']}")
                        context_text = "\n".join(context_parts) if context_parts else ""

                        if context_text:
                            user_content = f"""【对话历史】
{context_text}

【当前问题】
{user_input}

【参考资料】
{full_knowledge}

请结合对话历史理解当前问题，然后根据参考资料回答。"""
                        else:
                            user_content = build_user_prompt(user_input, full_knowledge)

                        reply = call_ai(system_rule, user_content)
            except Exception as e:
                reply = f"系统暂时出了点小问题：{str(e)}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    # 保存历史记录
    now_time = datetime.now().strftime("%H:%M:%S")
    st.session_state.history.append({
        "time": now_time,
        "role": role,
        "question": user_input,
        "answer": reply
    })

# ========== 底部电话黄页（静态兜底） ==========
st.divider()
st.header("📞 电话黄页（静态兜底）")
st.caption("AI 答不上来时，可以直接查这里 — 不依赖API，永远可用")

yellow_page = """
| 部门 | 电话 |
|------|------|
| 校园24小时报警（保卫处） | 0371-61911110 ⚠️ 以官方为准 |
| 学校24小时总值班室 | 0371-61912000 ⚠️ 以官方为准 |
| 教务处综合服务窗口 | 0371-61912101 ⚠️ 以官方为准 |
| 学生资助管理中心 | 0371-61912301 ⚠️ 以官方为准 |
| 心理健康教育中心 | 0371-61912302 ⚠️ 以官方为准 |
| 后勤综合服务总台 | 0371-61912800 ⚠️ 以官方为准 |
| 24小时水电抢修 | 0371-61912801 ⚠️ 以官方为准 |
| 校园卡服务中心 | 0371-61912803 ⚠️ 以官方为准 |
| 图书馆前台 | 0371-61912700 ⚠️ 以官方为准 |
| 网络信息中心 | 0371-61912900 ⚠️ 以官方为准 |
| 校医院24小时急诊 | 0371-61912601 ⚠️ 以官方为准 |
| 招生办公室 | 0371-61912578 ⚠️ 以官方为准 |
"""
st.markdown(yellow_page)
st.caption("⚠️ 所有电话以学校官方最新公布为准，如有变动请拨打总值班室核实。")