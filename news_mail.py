import os
import requests
from openai import OpenAI


# ======================
# 环境变量
# ======================

DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
MAIL_TO = os.environ["MAIL_TO"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]


# ======================
# DeepSeek 客户端
# ======================

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


# ======================
# 生成新闻
# ======================

def create_news():

    prompt = """
请生成今日全球热点新闻日报。

要求：

一、美国热点新闻 10 条
二、中国热点新闻 10 条
三、欧洲热点新闻 10 条
四、其他国际新闻 10 条

另外提供：

1. 国际现货黄金价格
2. WTI原油价格
3. 布伦特原油价格

格式：

【标题】
内容摘要（2-3句话）

要求：
- 中文输出
- 内容适合邮件阅读
- 简洁清晰
- 标注日期
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    return response.choices[0].message.content



# ======================
# 发送邮件
# ======================

def send_email(content):

    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }


    data = {

        "from": "Daily News <onboarding@resend.dev>",

        "to": [
            MAIL_TO
        ],

        "subject": "每日全球热点新闻",

        "html": f"""
        <html>
        <body>

        <h2>
        🌍 每日全球热点新闻
        </h2>

        <hr>

        <pre style="
        font-size:15px;
        white-space:pre-wrap;
        ">
{content}
        </pre>

        </body>
        </html>
        """
    }


    response = requests.post(
        url,
        headers=headers,
        json=data
    )


    print(response.text)


# ======================
# 主程序
# ======================

if __name__ == "__main__":

    print("开始生成新闻...")

    news = create_news()

    print("新闻生成完成")

    send_email(news)

    print("邮件发送完成")