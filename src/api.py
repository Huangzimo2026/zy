import requests
from config import API_URL, API_KEY, MODEL_NAME
def call_ai(system_prompt, user_prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=10)
        if response.status_code == 401:
            return "API密钥无效，请检查配置的API_KEY是否正确。"
        if response.status_code == 429:
            return "请求过于频繁，请稍后再试。"
        if response.status_code >= 500:
            return "服务器内部错误，请稍后重试。"
        response.raise_for_status()
        result = response.json()
        if "choices" not in result or not result["choices"]:
            return "返回数据格式异常，请稍后重试。"
        reply = result["choices"][0]["message"]["content"]
        # 兜底过滤（防止泄露 prompt 结构）
        if "参考资料" in reply or "用户问题" in reply or "规则" in reply:
            return "抱歉，这个问题我暂时还不清楚，建议咨询学校对应部门。"
        return reply
    except requests.exceptions.ConnectionError:
        return "网络连接失败，请检查网络连接后重试。"
    except requests.exceptions.Timeout:
        return "请求超时，请检查网络或稍后重试。"
    except requests.exceptions.RequestException as e:
        return f"请求异常：{str(e)}"
    except KeyError as e:
        return f"数据解析失败，缺少字段：{str(e)}"
    except Exception as e:
        return f"发生未知错误：{str(e)}"