import os
import smtplib
from email.mime.text import MIMEText
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

email_to = os.environ["MAIL_TO"]

def create_news():

    prompt = """
请生成今天的全球热点新闻日报。

格式：

一、美国热点新闻（10条）
二、中国热点新闻（10条）
三、欧洲热点新闻（10条）
四、其他国际热点新闻（10条）

另外加入：
1. 国际现货黄金价格
2. WTI原油价格
3. 布伦特原油价格

要求：
中文输出，简洁，每条包含标题和一句摘要。
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text


def send_mail(content):

    sender = os.environ["MAIL_TO"]

    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = "每日全球热点新闻"
    msg["From"] = sender
    msg["To"] = email_to

    # 后续配置邮件发送服务
    print(content)


if __name__ == "__main__":
    news = create_news()
    send_mail(news)
