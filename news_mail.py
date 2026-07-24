import os
import requests
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

    tz = pytz.timezone("Asia/Shanghai")

    now = datetime.now(tz)

    yesterday = now - timedelta(days=1)

    return yesterday.strftime("%Y-%m-%d")



# ======================
# GDELT 新闻获取
# ======================

def get_news(keyword, country):

    date = get_yesterday()

    url = "https://api.gdeltproject.org/api/v2/doc/doc"


    params = {

        "query": f"{keyword} country:{country}",

        "mode": "artlist",

        "format": "json",

        "maxrecords": 10,

        "startdatetime":
            date.replace("-", "")
            + "000000",

        "enddatetime":
            date.replace("-", "")
            + "235959"
    }


    try:

        r = requests.get(
            url,
            params=params,
            timeout=20
        )

        data = r.json()


        articles = []


        for item in data.get("articles", []):

            articles.append(
                {
                    "title":
                        item.get("title"),

                    "url":
                        item.get("url")
                }
            )


        return articles


    except Exception as e:

        print(e)

        return []



# ======================
# DeepSeek整理新闻
# ======================

def summarize_news(news):


    prompt = f"""

你是一名国际新闻编辑。

请根据以下真实新闻资料，
整理昨天({get_yesterday()})全球热点日报。

要求：

1. 美国新闻10条
2. 中国新闻10条
3. 欧洲新闻10条
4. 其他国际新闻10条


每条格式：

【标题】

摘要：
2-3句话。


另外增加：

黄金价格：
WTI原油：
布伦特原油：


新闻必须注明日期：
{get_yesterday()}


新闻资料：

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

        temperature=0.3

    )


    return response.choices[0].message.content




# ======================
# 获取新闻
# ======================

def create_news():


    categories = {


        "美国":
        ("USA", "United States"),


        "中国":
        ("CHN", "China"),


        "欧洲":
        ("EUR", "Europe"),


        "其他":
        ("WORLD", "international")

    }


    all_news=""


    for name,(country,key) in categories.items():


        print("获取:",name)


        result=get_news(
            key,
            country
        )


        all_news += "\n\n"

        all_news += name

        all_news += "\n"


        for n in result:

            all_news += (
                "- "
                + str(n["title"])
                + "\n"
            )



    return summarize_news(all_news)





# ======================
# 发送邮件
# ======================

def send_email(content):


    url="https://api.resend.com/emails"


    headers={

        "Authorization":
        f"Bearer {RESEND_API_KEY}",

        "Content-Type":
        "application/json"

    }


    data={


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
🌍 全球热点新闻日报
</h2>

<p>
日期：
{get_yesterday()}
</p >


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


    r=requests.post(

        url,

        headers=headers,

        json=data

    )


    print(r.text)





# ======================
# 主程序
# ======================

if __name__=="__main__":


    print(
        "开始生成昨日新闻..."
    )


    news=create_news()


    print(
        "新闻生成完成"
    )


    send_email(news)


    print(
        "邮件发送完成"
    )
