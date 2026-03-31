import feedparser
import datetime
import ssl
import re
import socket

# 設定全局連線超時為 10 秒，防止腳本卡死
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

def get_thumbnail(entry):
    """高效提取縮圖：優先從結構化標籤讀取，最後才使用正則掃描"""
    # 1. 嘗試從 media_content 提取
    try:
        if 'media_content' in entry and entry.media_content:
            return entry.media_content[0]['url']
        
        # 2. 嘗試從 links (enclosures) 提取
        if 'links' in entry:
            for link in entry.links:
                if 'image' in link.get('type', ''):
                    return link.get('href')
    except Exception:
        pass
    
    # 3. 嘗試從內容中快速掃描第一個 img 標籤 (限制掃描長度以提升速度)
    content = (entry.get('description', '') + entry.get('summary', ''))[:2000]
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
    html += f'<div class="bg-{color}-600 p-4 shadow-inner text-center font-black text-white tracking-widest uppercase">{name}</div>'
    html += '<div class="p-4 flex-1 space-y-6 overflow-y-auto">'
    
    try:
        print(f"正在連線並解析 {name}...")
        # 使用 feedparser 解析
        feed = feedparser.parse(url)
        
        if not feed.entries:
            html += '<p class="text-slate-400 text-sm text-center py-10">無法讀取內容</p>'
        else:
            for entry in feed.entries[:6]: # 限制 6 則
                thumb = get_thumbnail(entry)
                summary = entry.get('summary', entry.get('description', ''))
                # 快速移除 HTML 標籤
                summary = re.sub(r'<[^>]+>', '', summary).strip()[:45] + "..."
                
                # 加入 loading="lazy" 優化瀏覽器載入效能
                html += f"""
                <div class="group flex flex-col space-y-2">
                    <div class="overflow-hidden rounded-xl bg-slate-100 aspect-video">
                        <img src="{thumb}" 
                             alt="thumbnail" 
                             loading="lazy" 
                             class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" 
                             onerror="this.src='https://via.placeholder.com/400x225?text=News'">
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
            print(f"  ✅ {name} 處理完成")
    except Exception as e:
        print(f"  ❌ {name} 逾時或失敗: {e}")
        html += f'<p class="text-red-400 text-sm text-center">連線超時</p>'
    
    html += '</div></div>'
    return html

def main():
    now = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    print(f"任務開始執行時間：{now}")
    
    columns_html = "".join([get_news_column(cfg) for cfg in feeds_config])

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
        <div class="hidden bg-blue-600 bg-green-600 bg-orange-600 bg-red-600 text-blue-600 text-green-600 text-orange-600 text-red-600"></div>
    </head>
    <body class="min-h-screen p-4 md:p-8">
        <div class="max-w-[1600px] mx-auto">
            <header class="flex flex-col lg:flex-row justify-between items-center mb-10 gap-6">
                <div class="text-center lg:text-left">
                    <h1 class="text-4xl font-black text-slate-900 tracking-tighter">TECH MONITOR <span class="text-blue-600 italic">DASHBOARD</span></h1>
                    <p class="text-slate-500 font-medium tracking-wide">AI 自動化情報匯整系統</p>
                </div>
                <div class="flex items-center gap-4 bg-white p-2 pl-6 rounded-full shadow-md border border-slate-200">
                    <div class="flex flex-col items-end">
                        <span class="text-[10px] text-slate-400 font-black uppercase tracking-widest">Auto-Refresh Enabled</span>
                        <span class="text-slate-700 font-mono font-bold">{now}</span>
                    </div>
                    <div class="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center shadow-lg">
                        <div class="w-2 h-2 bg-white rounded-full animate-ping"></div>
                    </div>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                {columns_html}
            </div>

            <footer class="mt-20 text-center border-t border-slate-200 pt-10 text-slate-400 text-sm">
                <p>© 2026 科技新聞自動化計畫 | 效能優化版本</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(template)
    print("--- 任務執行完畢 ---")

if __name__ == "__main__":
    main()
