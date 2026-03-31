import feedparser
import datetime
import ssl
import re
import socket

# 設定全局連線超時為 10 秒
socket.setdefaulttimeout(10)

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

def get_news_column(config):
    """抓取單一來源並生成純文字欄位的 HTML"""
    name = config["name"]
    url = config["url"]
    color = config["color"]
    
    # 建立欄位容器
    html = f'<div class="flex flex-col h-full bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">'
    # 欄位標題欄
    html += f'<div class="bg-{color}-600 p-4 border-b border-{color}-700"><h2 class="text-white font-bold text-center tracking-widest">{name}</h2></div>'
    html += '<div class="p-4 flex-1 space-y-5 overflow-y-auto bg-slate-50/30">'
    
    try:
        print(f"正在抓取 {name}...")
        feed = feedparser.parse(url)
        
        if not feed.entries:
            html += '<p class="text-slate-400 text-sm text-center py-10">暫無內容</p>'
        else:
            for entry in feed.entries[:8]: # 純文字版可以顯示更多則新聞 (改為 8 則)
                # 取得時間 (若無則顯示近期)
                published = entry.get('published', entry.get('updated', '近期'))
                
                # 處理摘要 (移除所有標籤)
                summary = entry.get('summary', entry.get('description', ''))
                summary = re.sub(r'<[^>]+>', '', summary).strip()
                summary = summary[:60] + "..." # 稍微加長摘要長度
                
                html += f"""
                <div class="group">
                    <div class="flex items-center gap-2 mb-1">
                        <span class="w-1.5 h-1.5 rounded-full bg-{color}-500"></span>
                        <span class="text-[10px] text-slate-400 font-medium uppercase">{published}</span>
                    </div>
                    <a href="{entry.link}" target="_blank" class="block text-slate-800 font-bold leading-tight hover:text-{color}-600 transition-colors mb-1">
                        {entry.title}
                    </a>
                    <p class="text-slate-500 text-xs leading-relaxed line-clamp-2">{summary}</p>
                    <hr class="mt-4 border-slate-100">
                </div>
                """
            print(f"  ✅ {name} 抓取完成")
    except Exception as e:
        print(f"  ❌ {name} 失敗: {e}")
        html += f'<p class="text-red-400 text-sm text-center py-10">連線逾時</p>'
    
    html += '</div></div>'
    return html

def main():
    # 取得台灣時間
    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    
    columns_html = "".join([get_news_column(cfg) for cfg in feeds_config])

    template = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>科技資訊監測站 (純文字版)</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+TC:wght@400;700;900&display=swap');
            body {{ font-family: 'Inter', 'Noto Sans TC', sans-serif; background-color: #f8fafc; }}
            .line-clamp-2 {{ display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
        </style>
        <div class="hidden bg-blue-600 bg-green-600 bg-orange-600 bg-red-600 text-blue-500 text-green-500 text-orange-500 text-red-500"></div>
    </head>
    <body class="min-h-screen p-4 md:p-8">
        <div class="max-w-[1600px] mx-auto">
            <header class="flex flex-col md:flex-row justify-between items-end mb-10 border-l-4 border-blue-600 pl-6 gap-4">
                <div>
                    <h1 class="text-3xl font-black text-slate-900 tracking-tight">TECH MONITOR <span class="text-blue-600">LITE</span></h1>
                    <p class="text-slate-500 font-medium">高效能科技情報監測系統</p>
                </div>
                <div class="text-right">
                    <p class="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">Last System Sync</p>
                    <p class="text-slate-700 font-mono font-bold bg-white px-3 py-1 rounded-md shadow-sm border border-slate-200">{now} (UTC+8)</p>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {columns_html}
            </div>

            <footer class="mt-16 text-center text-slate-400 text-xs border-t border-slate-200 pt-8">
                <p>© 2026 科技新聞自動化計畫 | 極簡效能優化版</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template)
    print("--- 任務執行成功 (純文字模式) ---")

if __name__ == "__main__":
    main()
