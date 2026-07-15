# 电费相关关键词库
ELECTRIC_KEYWORDS = [
    "电费", "电价", "用电", "电表", "缴费", "欠费",
    "峰谷", "阶梯电价", "一度电", "电费黄页", "用电量"
]

def check_question_relevant(question):
    """判断用户问题是否和电费相关"""
    for keyword in ELECTRIC_KEYWORDS:
        if keyword in question:
            return True
    return False

def build_prompt(user_question, knowledge=""):
    """拼接知识库和用户问题，生成最终提问内容"""
    if knowledge:
        return f"""参考以下知识库内容回答用户问题：
知识库：
{knowledge}

用户问题：{user_question}
"""
    return user_question