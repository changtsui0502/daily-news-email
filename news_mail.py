import os
import requests
import feedparser

from datetime import datetime, timedelta
import pytz

from openai import OpenAI


# ======================
# 环境变量
# ======================

DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
MAIL_TO = os.environ["MAIL_TO"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]



# ======================
# DeepSeek
# ======================

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)



# ======================
# 获取北京时间昨天日期
# ======================

def get_yesterday():

    tz = pytz.timezone(
        "Asia/Shanghai"
    )

    now = datetime.now(tz)

    yesterday = now - timedelta(days=1)

    return yesterday.strftime(
        "%Y-%m-%d"
    )




# ======================
# RSS真实新闻源
# ======================


RSS_SOURCES = {


"美国":
[
"https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml",
"https://www.reuters.com/rssFeed/worldNews"
],


"中国":
[
"https://feeds.bbci.co.uk/news/world/asia/rss.xml"
],


"欧洲":
[
"https://feeds.bbci.co.uk/news/world/europe/rss.xml"
],


"国际":
[
"https://feeds.bbci.co.uk/news/world/rss.xml"
]

}




# ======================
# 获取真实新闻
# ======================

def get_real_news():


    news_text = ""


    for region, feeds in RSS_SOURCES.items():

        news_text += "\n\n"
        news_text += "【"+region+"】\n"


        count = 0


        for url in feeds:


            try:

                feed = feedparser.parse(url)


                for item in feed.entries:


                    if count >= 10:
                        break


                    title = item.title

                    summary = (
                        item.get(
                            "summary",
                            ""
                        )
                    )


                    news_text += (

                        "\n标题:"
                        + title

                        + "\n摘要:"
                        + summary[:300]

                        + "\n"

                    )


                    count += 1



            except Exception as e:

                print(
                    "RSS错误:",
                    e
                )


    return news_text





# ======================
# DeepSeek整理
# ======================

def summarize_news(news):


    date = get_yesterday()


    prompt = f"""

你是一名国际新闻编辑。

下面提供的是新闻RSS抓取的真实新闻。

请整理成：
{date} 全球新闻日报


要求：

一、美国热点10条

二、中国热点10条

三、欧洲热点10条

四、其他国际新闻10条


每条格式：

【新闻标题】

摘要：
2-3句话


另外增加：

黄金价格：
WTI原油价格：
布伦特原油价格：


要求：

1. 只能根据提供新闻整理
2. 不允许虚构新闻
3. 标明日期 {date}
4. 中文输出
5. 适合邮件阅读


新闻数据：

{news}

"""


    response = client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {
                "role":"user",
                "content":prompt
            }

        ],

        temperature=0.2

    )


    return response.choices[0].message.content





# ======================
# 生成新闻
# ======================

def create_news():


    print(
        "正在抓取真实新闻..."
    )


    raw_news = get_real_news()


    print(
        "新闻抓取完成"
    )


    return summarize_news(
        raw_news
    )





# ======================
# 邮件发送
# ======================

def send_email(content):


    url = (
        "https://api.resend.com/emails"
    )


    headers = {

        "Authorization":
        f"Bearer {RESEND_API_KEY}",

        "Content-Type":
        "application/json"

    }


    data = {


        "from":

        "Daily News <onboarding@resend.dev>",


        "to":

        [
            MAIL_TO
        ],


        "subject":

        f"全球新闻日报 {get_yesterday()}",



        "html":

        f"""

<html>

<body>

<h2>
🌍 全球新闻日报
</h2>

<p>
日期：
{get_yesterday()}
</p>

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


    print(
        response.text
    )





# ======================
# 主程序
# ======================

if __name__ == "__main__":


    print(
        "开始生成昨日新闻"
    )


    news = create_news()


    send_email(news)


    print(
        "邮件发送完成"
    )