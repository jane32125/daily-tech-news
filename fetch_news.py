import feedparser
import datetime
import ssl
import re

# 解決 SSL 憑證驗證問題
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# 設定四個目標新聞來源與辨識色
feeds_config = [
    {"name": "TechNews 科技新報", "url": "https://technews.tw/feed/", "color": "blue"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "color": "green"},
    {"name": "PanSci 泛科學", "url": "https://pansci.asia/feed/", "color": "orange"},
    {"name": "iThome 新聞", "url": "https://www.ithome.com.tw/rss", "color": "red"}
]

def get_thumbnail(entry):
    """嘗試從不同標籤中提取新聞縮圖"""
    # 1. 嘗試從 media_content 提取
    if 'media_content' in entry and entry.media_content:
        return entry.media_content[0]['url']
    
    # 2. 嘗試從 links (enclosures) 提取
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', ''):
                return link.get('href')
    
    # 3. 嘗試從 description/summary 中用正規表達式抓取 <img> 標籤
    content = entry.get('description', '') + entry.get('summary', '')
    img_match = re.search(r'<img [^>]*src="([^"]+)"', content)
    if img_match:
        return img_match.group(1)
        
    # 4. 沒找到則回傳佔位圖
    return "https://via.placeholder.com/400x225?text=No+Image"

def get_news_column(config):
    """抓取單一來源並生成一個欄位的 HTML"""
    name = config["name"]
    url = config["url"]
    color = config["color"]
    
    html = f'<div class="flex flex-col h-full bg-white rounded-2xl shadow-md border border-slate-100 overflow-hidden">'
    # 欄位標題
    html += f'<div class="bg-{color}-600 p-4 shadow-inner text-center font-black text-white tracking-widest uppercase">{name}</div>'
    html += '<div class="p-4 flex-1 space-y-6 overflow-y-auto">'
    
    try:
        print(f"正在抓取 {name}...")
        feed = feedparser.parse(url)
        
        if not feed.entries:
            html += '<p class="text-slate-400 text-sm text-center py-10">暫時無法取得新聞...</p>'
        else:
            for entry in feed.entries[:6]: # 每個來源取前 6 則
                thumb = get_thumbnail(entry)
                # 簡單過濾摘要內容
                summary = entry.get('summary', entry.get('description', ''))
                if '<' in summary:
                    summary = re.sub(r'<[^>]+>', '', summary) # 移除所有 HTML 標籤
                summary = summary.strip()[:45] + "..."
                
                html += f"""
                <div class="group flex flex-col space-y-2">
                    <div class="overflow-hidden rounded-xl bg-slate-100 aspect-video">
                        <img src="{thumb}" alt="thumbnail" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" onerror="this.src='https://via.placeholder.com/400x225?text=News'">
                    </div>
                    <div class="space-y-1">
                        <a href="{entry.link}" target="_blank" class="block text-slate-800 font-bold leading-snug hover:text-{color}-600 transition-colors line-clamp-2">
                            {entry.title}
                        </a>
                        <p class="text-slate-500 text-xs leading-relaxed">{summary}</p>
                    </div>
                </div>
                <hr class="border-slate-50">
                """
    except Exception as e:
        print(f"錯誤：{name} 抓取失敗: {e}")
        html += f'<p class="text-red-400 text-sm text-center">抓取發生錯誤</p>'
    
    html += '</div></div>'
    return html

def main():
    # 取得台灣時間 (UTC+8)
    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    
    columns_html = "".join([get_news_column(cfg) for cfg in feeds_config])

    # 完整 HTML 模板
    template = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>科技資訊監測站 PRO</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Noto+Sans+TC:wght@400;700;900&display=swap');
            body {{ font-family: 'Inter', 'Noto Sans TC', sans-serif; background-color: #f1f5f9; }}
            .line-clamp-2 {{ display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
        </style>
        <!-- 確保 Tailwind 動態顏色類別不被過濾 -->
        <div class="hidden bg-blue-600 bg-green-600 bg-orange-600 bg-red-600 text-blue-600 text-green-600 text-orange-600 text-red-600"></div>
    </head>
    <body class="min-h-screen p-4 md:p-8">
        <div class="max-w-[1600px] mx-auto">
            <header class="flex flex-col lg:flex-row justify-between items-center mb-10 gap-6">
                <div class="text-center lg:text-left">
                    <h1 class="text-4xl font-black text-slate-900 tracking-tighter">TECH MONITOR <span class="text-blue-600 italic">DASHBOARD</span></h1>
                    <p class="text-slate-500 font-medium">即時科技情報匯整系統</p>
                </div>
                <div class="flex items-center gap-4 bg-white p-2 pl-6 rounded-full shadow-md border border-slate-200">
                    <div class="flex flex-col items-end">
                        <span class="text-[10px] text-slate-400 font-black uppercase tracking-widest">System Status: Online</span>
                        <span class="text-slate-700 font-mono font-bold">{now} (UTC+8)</span>
                    </div>
                    <div class="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center animate-pulse">
                        <div class="w-4 h-4 bg-white rounded-full"></div>
                    </div>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                {columns_html}
            </div>

            <footer class="mt-20 text-center border-t border-slate-200 pt-10 text-slate-400 text-sm">
                <div class="flex justify-center gap-6 mb-4">
                    <div class="flex items-center gap-2"><span class="w-3 h-3 bg-blue-600 rounded-full"></span> TechNews</div>
                    <div class="flex items-center gap-2"><span class="w-3 h-3 bg-green-600 rounded-full"></span> TechCrunch</div>
                    <div class="flex items-center gap-2"><span class="w-3 h-3 bg-orange-600 rounded-full"></span> PanSci</div>
                    <div class="flex items-center gap-2"><span class="w-3 h-3 bg-red-600 rounded-full"></span> iThome</div>
                </div>
                <p>© 2026 科技新聞自動化計畫 | 由 GitHub Actions & Python 驅動</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template)
    print("--- 縮圖與版面優化完成 ---")

if __name__ == "__main__":
    main()
