import os
import requests
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

MAIL_TO = os.environ["MAIL_TO"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]


def create_news():

    prompt = """
请生成今天的全球热点新闻日报。

要求：

1. 美国热点新闻10条
2. 中国热点新闻10条
3. 欧洲热点新闻10条
4. 其他国际新闻10条

另外提供：

- 国际现货黄金价格
- WTI原油价格
- 布伦特原油价格

要求：
中文输出。
每条包含：
标题 + 简短摘要。

格式适合邮件阅读。
"""

    result = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return result.output_text


def send_email(content):

    url = "https://api.resend.com/emails"

    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "from": "Daily News <onboarding@resend.dev>",
        "to": [MAIL_TO],
        "subject": "每日全球热点新闻",
        "html": f"""
        <html>
        <body>
        <h2>每日全球热点新闻</h2>
        <pre>{content}</pre>
        </body>
        </html>
        """
    }

    r = requests.post(
        url,
        headers=headers,
        json=data
    )

    print(r.text)


if __name__ == "__main__":

    news = create_news()

    send_email(news)
