import streamlit as st
from utils.api import call_ai
from utils.prompt import check_question_relevant, build_prompt

# 页面配置
st.set_page_config(page_title="小航AI助手", page_icon="✈️", layout="wide")

# 标题
st.title("✈️ 小航AI助手 - 郑航校园智能咨询")
st.markdown("---")

# 侧边栏 校园黄页
with st.sidebar:
    st.header("📑 校园黄页")
    st.markdown("""
    **校区地址**
    - 东校区：金水区文苑西路平安大道
    - 大学路校区：二七区大学中路2号
    
    **作息时间**
    - 周日-周四 23:00断电
    - 周五-周六 23:30断电
    
    **常用入口**
    - 教务系统：jwc.zua.edu.cn
    - 图书馆：8:00-22:00开放
    """)
    st.markdown("---")
    st.caption("郑州航空工业管理学院 认知实习项目")

# 常见问题推荐
st.subheader("💡 常见问题 一键提问")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("教务处在哪？"):
        st.session_state.user_input = "教务处在哪？"
with col2:
    if st.button("宿舍几点断电？"):
        st.session_state.user_input = "宿舍几点断电？"
with col3:
    if st.button("怎么查课表？"):
        st.session_state.user_input = "怎么查课表？"
with col4:
    if st.button("图书馆开放时间？"):
        st.session_state.user_input = "图书馆开放时间？"

st.markdown("---")

# 聊天对话区
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好呀！我是小航，有任何校园问题都可以问我~"}
    ]

# 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 用户输入
user_input = st.chat_input("输入你的校园问题...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("小航正在查询..."):
            if not check_question_relevant(user_input):
                reply = "抱歉呀，我只能解答郑航校园相关的问题哦~ 换个校园问题试试吧。"
            else:
                final_prompt = build_prompt(user_input)
                reply = call_ai(final_prompt)
        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})