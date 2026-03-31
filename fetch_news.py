import feedparser
import datetime
import ssl

# 解決部分環境下 SSL 憑證驗證失敗的問題
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# 設定新聞來源
feeds = {
    "TechNews 科技新報": "https://technews.tw/feed/",
    "TechCrunch": "https://techcrunch.com/feed/",
    "泛科學": "https://pansci.asia/feed/"
    "iThome": "https://www.ithome.com.tw/rss"
}

def fetch_content():
    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    news_items_html = ""

    for name, url in feeds.items():
        try:
            print(f"正在抓取 {name}...")
            feed = feedparser.parse(url)
            
            # 檢查是否抓取成功
            if not feed.entries:
                print(f"警告：{name} 沒有抓到任何文章")
                continue

            for entry in feed.entries[:5]: # 每個來源取前 5 則
                # 取得時間 (簡單處理)
                published = entry.get('published', '剛剛')
                summary = entry.get('summary', '點擊連結閱讀更多內容...').split('<')[0][:100] + "..."
                
                news_items_html += f"""
                <div class="news-card bg-white p-6 rounded-2xl border border-slate-100 shadow-sm mb-4">
                    <div class="flex items-center gap-2 mb-2">
                        <span class="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded">{name}</span>
                        <span class="text-slate-400 text-xs">{published}</span>
                    </div>
                    <a href="{entry.link}" target="_blank" class="text-xl font-bold text-slate-800 hover:text-blue-600 transition-colors">
                        {entry.title}
                    </a>
                    <p class="mt-2 text-slate-600 text-sm line-clamp-2">
                        {summary}
                    </p>
                </div>
                """
        except Exception as e:
            print(f"錯誤：抓取 {name} 時發生問題: {e}")

    # 如果完全沒抓到新聞，給個提示
    if not news_items_html:
        news_items_html = "<p class='text-center text-slate-500'>暫時沒有新聞更新，請稍後再試。</p>"

    return now, news_items_html

# HTML 模板
template = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>我的科技新聞摘要</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&display=swap');
        body {{ font-family: 'Noto Sans TC', sans-serif; background-color: #f8fafc; }}
        .news-card {{ transition: transform 0.2s ease, box-shadow 0.2s ease; }}
        .news-card:hover {{ transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }}
    </style>
</head>
<body class="min-h-screen p-4 md:p-8">
    <div class="max-w-3xl mx-auto">
        <header class="mb-10 text-center">
            <h1 class="text-3xl md:text-4xl font-bold text-slate-800 mb-2">🚀 每日科技新聞摘要</h1>
            <p class="text-slate-500">最後更新：{now} (UTC+8)</p>
        </header>
        <div class="space-y-4">
            {content}
        </div>
        <footer class="mt-12 text-center text-slate-400 text-sm">
            <p>© 2026 科技新聞自動化計畫 | 由 GitHub Actions & Python 驅動</p>
        </footer>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    update_time, news_content = fetch_content()
    final_html = template.format(now=update_time, content=news_content)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    print("網頁生成成功！")
