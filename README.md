## 📊 專題簡報

[專題簡報連結](https://www.canva.com/design/DAG17lJkVuw/pG6HBjIm12TrmIcECQ6hnQ/edit?utm_content=DAG17lJkVuw&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)

# 🚀 1111 人力銀行職缺爬蟲專案

一個功能完整的 1111 人力銀行職缺爬蟲工具，支援多頁爬取、資料分析和 CSV 匯出功能。

## 📋 目錄結構

```
1111crawler_project/
├── venv/                    # 虛擬環境
├── src/                     # 原始碼
│   └── job_1111_crawler.py  # 主要爬蟲程式
├── data/                    # 資料檔案
│   └── *.csv               # 爬取的職缺資料
├── requirements.txt         # 套件需求
├── .gitignore              # Git 忽略檔案
├── settings.json           # 設定檔
└── README.md               # 專案說明
```

## ✨ 功能特色

- 🔍 **智慧搜尋**：支援關鍵字搜尋職缺
- 📄 **多頁爬取**：可設定爬取多個頁面
- 🛡️ **反爬蟲機制**：隨機延遲、User-Agent 輪換
- 📊 **資料分析**：職缺統計分析和相關度評分
- 💾 **資料匯出**：支援 CSV 格式匯出
- 🎨 **美化顯示**：終端機友善的資料呈現
- ⚙️ **設定檔支援**：可透過 JSON 檔案自訂設定

## 🛠️ 安裝說明

### 1. 複製專案

```bash
git clone <repository-url>
cd 1111crawler_project
```

### 2. 建立虛擬環境

```bash
# Windows
python -m venv venv
venv\\Scripts\\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安裝套件

```bash
pip install -r requirements.txt
```

### 4. 執行程式

```bash
python src/job_1111_crawler.py
```

## 📦 套件需求

- `requests` - HTTP 請求處理
- `pandas` - 資料處理和分析
- `beautifulsoup4` - HTML 解析
- `urllib3` - URL 處理工具

## 🚀 使用方法

### 基本使用

```python
from src.job_1111_crawler import Job1111Crawler

# 建立爬蟲實例
crawler = Job1111Crawler()

# 搜尋職缺
html_content = crawler.search_jobs("資料工程師")
jobs = crawler.parse_jobs(html_content)

# 顯示結果
crawler.display_jobs(jobs)

# 儲存到 CSV
crawler.save_to_csv(jobs, "data/jobs.csv")
```

### 多頁爬取

```python
# 爬取前 3 頁的職缺
jobs = crawler.crawl_multiple_pages("Python工程師", max_pages=3)
```

### 資料分析

```python
# 分析職缺統計資訊
crawler.analyze_jobs(jobs)
```

## ⚙️ 設定檔說明

`settings.json` 範例：

```json
{
  "default_keyword": "資料工程師",
  "max_pages": 3,
  "delay_range": [1, 3],
  "output_directory": "data/",
  "csv_encoding": "utf-8-sig",
  "user_agents": [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
  ]
}
```

## 📊 輸出資料格式

CSV 檔案包含以下欄位：

| 欄位名稱        | 說明       | 範例                            |
| --------------- | ---------- | ------------------------------- | ------------ |
| index           | 序號       | 1                               |
| title           | 職缺標題   | 資深資料工程師                  |
| company         | 公司名稱   | ABC 科技股份有限公司            |
| location        | 工作地點   | 台北市                          |
| salary          | 薪資範圍   | 月薪 50,000~80,000 元           |
| conditions      | 職缺條件   | 大學以上 \\                     | 3 年以上經驗 |
| publish_date    | 發布日期   | 2 天前                          |
| summary         | 職缺摘要   | 負責大數據平台開發...           |
| link            | 職缺連結   | https://www.1111.com.tw/job/... |
| relevance_score | 相關度評分 | 8                               |

## 🔧 進階功能

### 自訂搜尋參數

```python
# 自訂搜尋參數
crawler.search_jobs(
    keyword="機器學習工程師",
    page=1,
    delay=True
)
```

### 相關度評分機制

程式會根據以下關鍵字計算職缺相關度：

- 技術關鍵字：Python, SQL, Spark, Hadoop 等
- 領域關鍵字：資料分析、大數據、ETL 等
- 雲端平台：AWS, Azure, GCP 等

### 統計分析功能

- 📈 公司職缺分布統計
- 📍 工作地點分布分析
- ⭐ 職缺相關度評分
- 💰 薪資資訊完整度統計

## 🛡️ 反爬蟲策略

1. **隨機延遲**：請求間加入 1-3 秒隨機延遲
2. **User-Agent 輪換**：模擬不同瀏覽器
3. **Session 管理**：維持連線狀態
4. **錯誤處理**：完整的異常捕獲機制
5. **請求限制**：避免過於頻繁的請求

## 📝 使用範例

### 範例 1：搜尋特定職缺

```bash
請輸入搜尋關鍵字 (預設: 資料工程師): Python工程師
請輸入要爬取的頁數 (預設: 1): 2

🎯 開始搜尋 'Python工程師' 相關職缺...
🔍 搜尋關鍵字: Python工程師, 第 1 頁
✅ 成功獲取搜尋結果
📋 找到 20 個職缺卡片
```

### 範例 2：資料分析結果

```
📊 統計分析
==================================================
📈 公司分布 (前5名):
   科技公司A: 3 個職缺
   軟體公司B: 2 個職缺
   新創公司C: 2 個職缺

📍 地點分布:
   台北市: 15 個職缺
   新北市: 3 個職缺
   桃園市: 2 個職缺

⭐ 平均相關度: 6.25
   最高相關度: 12
   最低相關度: 2
```

## 🚨 注意事項

1. **合法使用**：請遵守 1111 人力銀行的使用條款
2. **頻率控制**：避免過於頻繁的請求，建議間隔 1-3 秒
3. **資料準確性**：網頁結構可能變更，如遇問題請更新程式
4. **網路連線**：確保網路連線穩定
5. **編碼問題**：CSV 檔案使用 UTF-8-BOM 編碼支援中文

## 🐛 常見問題

### Q1: 爬取失敗怎麼辦？

**A:** 檢查網路連線，確認 1111 網站是否正常運作，適當增加延遲時間。

### Q2: CSV 檔案中文亂碼？

**A:** 使用 Excel 開啟時選擇 UTF-8 編碼，或使用其他支援 UTF-8 的編輯器。

### Q3: 找不到職缺資料？

**A:** 可能是網頁結構變更，請檢查選擇器是否需要更新。

### Q4: 程式執行很慢？

**A:** 這是正常現象，為了避免被封鎖而加入的延遲機制。

## 🔄 更新日誌

### v1.0.0 (2025-10-29)

- ✨ 初始版本發布
- 🔍 基本搜尋功能
- 📄 多頁爬取支援
- 📊 資料分析功能
- 💾 CSV 匯出功能
