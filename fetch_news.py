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

# 設定四個目標新聞來源與辨識色、網站網域（用於抓取 Logo）
feeds_config = [
    {"name": "TechNews 科技新報", "url": "https://technews.tw/feed/", "color": "blue", "domain": "technews.tw"},
    {"name": "TechCrunch", "url": "https://techcrunch.com/feed/", "color": "green", "domain": "techcrunch.com"},
    {"name": "PanSci 泛科學", "url": "https://pansci.asia/feed/", "color": "orange", "domain": "pansci.asia"},
    {"name": "iThome 新聞", "url": "https://www.ithome.com.tw/rss", "color": "red", "domain": "ithome.com.tw"}
]

def get_news_column(config):
    """抓取單一來源並生成 2x2 區塊的 HTML"""
    name = config["name"]
    url = config["url"]
    color = config["color"]
    domain = config["domain"]
    
    # 使用 Google Favicon 服務抓取高品質 Logo
    logo_url = f"https://www.google.com/s2/favicons?sz=64&domain={domain}"
    
    # 建立欄位容器
    html = f'<div class="flex flex-col h-full bg-white rounded-3xl shadow-lg border border-slate-100 overflow-hidden hover:shadow-xl transition-shadow duration-300">'
    
    # 欄位標題欄 (加入 Logo)
    html += f"""
    <div class="bg-white p-6 border-b border-slate-50 flex items-center gap-4">
        <div class="w-12 h-12 rounded-2xl bg-slate-50 flex items-center justify-center border border-slate-100 p-2">
            <img src="{logo_url}" alt="{name} logo" class="w-full h-full object-contain">
        </div>
        <div>
            <h2 class="text-slate-800 font-black text-xl tracking-tight">{name}</h2>
            <div class="h-1 w-12 bg-{color}-500 rounded-full mt-1"></div>
        </div>
    </div>
    """
    
    html += '<div class="p-6 flex-1 space-y-6 bg-white">'
    
    try:
        print(f"正在抓取 {name}...")
        feed = feedparser.parse(url)
        
        if not feed.entries:
            html += '<p class="text-slate-400 text-sm text-center py-10">目前無更新內容</p>'
        else:
            # 限制 4 則新聞，資訊更精簡
            for entry in feed.entries[:4]: 
                published = entry.get('published', entry.get('updated', '近期'))
                # 簡單格式化時間 (只取日期部分)
                if len(published) > 16:
                    published = published[:16]
                
                # 處理摘要
                summary = entry.get('summary', entry.get('description', ''))
                summary = re.sub(r'<[^>]+>', '', summary).strip()
                summary = summary[:55] + "..." 
                
                html += f"""
                <div class="group cursor-pointer">
                    <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-1">{published}</p>
                    <a href="{entry.link}" target="_blank" class="block text-slate-800 font-bold text-lg leading-snug group-hover:text-{color}-600 transition-colors mb-2">
                        {entry.title}
                    </a>
                    <p class="text-slate-500 text-sm leading-relaxed line-clamp-2">{summary}</p>
                </div>
                """
            print(f"  ✅ {name} 抓取完成")
    except Exception as e:
        print(f"  ❌ {name} 失敗: {e}")
        html += f'<p class="text-red-400 text-sm text-center py-10">資料獲取失敗</p>'
    
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
        <title>每日科技新聞</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&family=Noto+Sans+TC:wght@400;700;900&display=swap');
            body {{ 
                font-family: 'Plus Jakarta Sans', 'Noto Sans TC', sans-serif; 
                background-color: #f8fafc;
                background-image: radial-gradient(#e2e8f0 1px, transparent 1px);
                background-size: 20px 20px;
            }}
            .line-clamp-2 {{ display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
        </style>
        <!-- 確保 Tailwind 動態顏色類別存在 -->
        <div class="hidden bg-blue-500 bg-green-500 bg-orange-500 bg-red-500 text-blue-600 text-green-600 text-orange-600 text-red-600"></div>
    </head>
    <body class="min-h-screen p-6 md:p-12">
        <div class="max-w-[1200px] mx-auto">
            <header class="flex flex-col md:flex-row justify-between items-center mb-12 gap-6">
                <div class="text-center md:text-left">
                    <h1 class="text-4xl font-extrabold text-slate-900 tracking-tight">每日科技新聞</h1>
                    <p class="text-slate-500 font-medium">精選科技情報</p>
                </div>
                <div class="bg-white/80 backdrop-blur-sm px-6 py-3 rounded-2xl shadow-sm border border-slate-200 text-right">
                    <p class="text-[10px] text-slate-400 font-black uppercase tracking-widest mb-1">Last Updated</p>
                    <p class="text-slate-800 font-mono font-bold text-lg">{now}</p>
                </div>
            </header>

            <!-- 2x2 網格佈局 -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {columns_html}
            </div>

            <footer class="mt-20 text-center text-slate-400 text-sm">
                <div class="flex justify-center gap-4 mb-4 opacity-50">
                    <div class="w-2 h-2 rounded-full bg-blue-500"></div>
                    <div class="w-2 h-2 rounded-full bg-green-500"></div>
                    <div class="w-2 h-2 rounded-full bg-orange-500"></div>
                    <div class="w-2 h-2 rounded-full bg-red-500"></div>
                </div>
                <p>© 2026 科技新聞自動化計畫 | 2x2 精簡佈局優化版</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template)
    print("--- 2x2 佈局優化完成 ---")

if __name__ == "__main__":
    main()
