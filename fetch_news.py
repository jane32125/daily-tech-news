import feedparser # 需要先 pip install feedparser
import datetime

# 設定新聞來源
feeds = {
    "TechNews 科技新報": "https://technews.tw/feed/",
    "Engadget 中文版": "https://chinese.engadget.com/rss.xml"
}

html_content = """
<html>
<head>
    <meta charset="utf-8">
    <title>我的科技新聞摘錄</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: auto; }
        .news-item { margin-bottom: 20px; border-bottom: 1px solid #eee; }
        .source { color: #888; font-size: 0.8em; }
    </style>
</head>
<body>
    <h1>每日科技新聞摘要</h1>
    <p>更新時間：{now}</p>
"""

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
content_list = []

for name, url in feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:5]: # 每個來源取前 5 則
        content_list.append(f'<div class="news-item"><span class="source">[{name}]</span><br>'
                            f'<a href="{entry.link}" target="_blank">{entry.title}</a></div>')

final_html = html_content.format(now=now) + "".join(content_list) + "</body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)
