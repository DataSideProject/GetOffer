import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time
import random
from collections import Counter
import urllib3
import warnings

# 忽略 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')


class Job1111Crawler:
    """1111 人力銀行職缺爬蟲類別"""
    
    def __init__(self):
        """初始化爬蟲"""
        self.base_url = "https://www.1111.com.tw"
        self.setup_session()
        print("🚀 1111 人力銀行爬蟲已初始化")
    
    def setup_session(self):
        """設定 HTTP session 和請求標頭"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.1111.com.tw/',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.verify = False
    
    def search_jobs(self, keyword="資料工程師", page=1, delay=True):
        """
        搜尋職缺
        
        Args:
            keyword (str): 搜尋關鍵字
            page (int): 頁數
            delay (bool): 是否加入隨機延遲
        
        Returns:
            str: HTML 內容，失敗時返回 None
        """
        params = {
            'ks': keyword,
            'page': page,
            'order': 1  # 1=最新, 2=相關度
        }
        
        try:
            if delay:
                # 隨機延遲避免被封鎖
                time.sleep(random.uniform(1, 3))
            
            print(f"🔍 搜尋關鍵字: {keyword}, 第 {page} 頁")
            
            response = self.session.get(
                f"{self.base_url}/search/job", 
                params=params, 
                timeout=15
            )
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                print(f"✅ 成功獲取搜尋結果")
                return response.text
            else:
                print(f"❌ 搜尋失敗，狀態碼: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("⏰ 請求超時")
            return None
        except requests.exceptions.ConnectionError:
            print("🌐 連線錯誤")
            return None
        except Exception as e:
            print(f"❌ 搜尋錯誤: {e}")
            return None
    
    def parse_jobs(self, html_content):
        """
        解析職缺資訊
        
        Args:
            html_content (str): HTML 內容
        
        Returns:
            list: 職缺資訊列表
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        jobs = []
        
        # 使用 .job-card 選擇器找到職缺卡片
        job_cards = soup.select('.job-card')
        print(f"📋 找到 {len(job_cards)} 個職缺卡片")
        
        for i, card in enumerate(job_cards):
            job_info = self.extract_job_from_card(card, i+1)
            if job_info:
                jobs.append(job_info)
        
        return jobs
    
    def extract_job_from_card(self, card, index):
        """
        從職缺卡片提取資訊
        
        Args:
            card: BeautifulSoup 職缺卡片元素
            index (int): 職缺編號
        
        Returns:
            dict: 職缺資訊字典
        """
        job_info = {'index': index}
        
        try:
            # 職缺標題和連結
            title_link = card.find('a', href=re.compile(r'/job/'))
            if title_link:
                job_info['title'] = title_link.get_text(strip=True)
                href = title_link.get('href', '')
                job_info['link'] = href if href.startswith('http') else self.base_url + href
            
            # 公司名稱
            company_elem = card.find(class_=re.compile(r'company', re.I))
            if not company_elem:
                # 嘗試從所有文字中尋找公司名稱
                all_text = card.get_text()
                company_match = re.search(r'([^｜\\n\\r\\t]+(?:股份有限公司|有限公司|公司))', all_text)
                if company_match:
                    job_info['company'] = company_match.group(1).strip()
                else:
                    # 提取卡片中的公司資訊
                    company_text = all_text.split('\\n')[0] if '\\n' in all_text else all_text[:50]
                    job_info['company'] = company_text.strip()
            else:
                job_info['company'] = company_elem.get_text(strip=True)
            
            # 工作地點
            location_patterns = [
                '台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', 
                '新竹市', '新竹縣', '基隆市', '宜蘭縣', '苗栗縣', '彰化縣',
                '南投縣', '雲林縣', '嘉義市', '嘉義縣', '屏東縣', '花蓮縣',
                '台東縣', '澎湖縣', '金門縣', '連江縣'
            ]
            
            card_text = card.get_text()
            for location in location_patterns:
                if location in card_text:
                    job_info['location'] = location
                    break
            
            # 薪資資訊
            salary_elem = card.find(class_=re.compile(r'salary|wage|pay', re.I))
            if salary_elem:
                job_info['salary'] = salary_elem.get_text(strip=True)
            else:
                # 從文字中尋找薪資模式
                salary_patterns = [
                    r'月薪\\s*(\\d+[,\\d]*\\s*[-~至]\\s*\\d+[,\\d]*|\\d+[,\\d]*)\\s*元',
                    r'年薪\\s*(\\d+[,\\d]*\\s*[-~至]\\s*\\d+[,\\d]*|\\d+[,\\d]*)\\s*元',
                    r'(\\d+[,\\d]*\\s*[-~至]\\s*\\d+[,\\d]*)\\s*元',
                    r'薪資\\s*(\\d+[,\\d]*\\s*[-~至]\\s*\\d+[,\\d]*)',
                    r'面議.*經常性薪資達(\\d+[,\\d]*)萬?元'
                ]
                
                for pattern in salary_patterns:
                    salary_match = re.search(pattern, card_text)
                    if salary_match:
                        job_info['salary'] = salary_match.group(0)
                        break
            
            # 職缺條件和要求
            conditions = card.select('.job-card-condition__text')
            if conditions:
                condition_texts = [cond.get_text(strip=True) for cond in conditions]
                job_info['conditions'] = ' | '.join(condition_texts)
            else:
                # 從卡片文字中提取條件資訊
                condition_match = re.search(r'([^|]*\\|[^|]*\\|[^|]*)', card_text)
                if condition_match:
                    job_info['conditions'] = condition_match.group(1).strip()
            
            # 發布時間
            time_patterns = [r'\\d+/\\d+', r'\\d+天前', r'昨天', r'今天', r'\\d+小時前']
            for pattern in time_patterns:
                time_match = re.search(pattern, card_text)
                if time_match:
                    job_info['publish_date'] = time_match.group(0)
                    break
            
            # 職缺摘要
            summary_elem = card.find(class_='job-summary')
            if summary_elem:
                job_info['summary'] = summary_elem.get_text(strip=True)[:200]
            else:
                # 提取卡片的部分文字作為摘要
                summary_text = card.get_text()[:200]
                job_info['summary'] = summary_text.replace('\\n', ' ').strip()
            
            # 計算相關度評分
            job_info['relevance_score'] = self.calculate_relevance_score(card_text)
            
            # 確保至少有標題才返回
            return job_info if job_info.get('title') else None
            
        except Exception as e:
            print(f"⚠️ 解析職缺卡片 {index} 時發生錯誤: {e}")
            return None
    
    def calculate_relevance_score(self, text):
        """
        計算職缺相關度評分
        
        Args:
            text (str): 職缺文字內容
        
        Returns:
            int: 相關度評分
        """
        text_lower = text.lower()
        
        # 資料工程相關關鍵字
        data_keywords = [
            '資料', 'data', '數據', '分析', 'analytics', 
            'etl', 'sql', 'python', 'spark', 'hadoop',
            'big data', '大數據', 'warehouse', '倉儲',
            'pipeline', '管道', 'kafka', 'airflow',
            'mongodb', 'mysql', 'postgresql', 'redis',
            'aws', 'azure', 'gcp', 'cloud', '雲端'
        ]
        
        score = 0
        for keyword in data_keywords:
            if keyword in text_lower:
                score += 1
        
        return score
    
    def display_jobs(self, jobs):
        """
        美化顯示職缺資訊
        
        Args:
            jobs (list): 職缺資訊列表
        """
        if not jobs:
            print("❌ 沒有找到職缺資料")
            return
        
        print(f"\\n🎯 成功爬取 {len(jobs)} 個職缺")
        print("=" * 80)
        
        for job in jobs:
            print(f"\\n📋 職缺 {job.get('index', 'N/A')}")
            print(f"🏢 標題: {job.get('title', 'N/A')}")
            print(f"🏪 公司: {job.get('company', 'N/A')}")
            print(f"📍 地點: {job.get('location', 'N/A')}")
            print(f"💰 薪資: {job.get('salary', 'N/A')}")
            print(f"📝 條件: {job.get('conditions', 'N/A')}")
            print(f"📅 發布: {job.get('publish_date', 'N/A')}")
            print(f"⭐ 相關度: {job.get('relevance_score', 'N/A')}")
            
            if job.get('summary'):
                summary = job['summary'][:100] + "..." if len(job['summary']) > 100 else job['summary']
                print(f"📄 摘要: {summary}")
            
            if job.get('link'):
                print(f"🔗 連結: {job['link']}")
            
            print("-" * 60)
    
    def save_to_csv(self, jobs, filename='1111_jobs.csv'):
        """
        儲存職缺資料到 CSV 檔案
        
        Args:
            jobs (list): 職缺資訊列表
            filename (str): 檔案名稱
        
        Returns:
            pandas.DataFrame: 職缺資料框
        """
        if not jobs:
            print("❌ 沒有職缺資料可儲存")
            return None
        
        df = pd.DataFrame(jobs)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ 已儲存 {len(jobs)} 筆職缺資料到 {filename}")
        return df
    
    def analyze_jobs(self, jobs):
        """
        分析職缺統計資訊
        
        Args:
            jobs (list): 職缺資訊列表
        """
        if not jobs:
            print("❌ 沒有職缺資料可分析")
            return
        
        print(f"\\n📊 統計分析")
        print("=" * 50)
        
        # 公司統計
        companies = [job.get('company') for job in jobs 
                    if job.get('company') and job.get('company') != 'N/A']
        if companies:
            company_counts = Counter(companies)
            print(f"📈 公司分布 (前5名):")
            for company, count in company_counts.most_common(5):
                print(f"   {company}: {count} 個職缺")
        
        # 地點統計
        locations = [job.get('location') for job in jobs 
                    if job.get('location') and job.get('location') != 'N/A']
        if locations:
            location_counts = Counter(locations)
            print(f"\\n📍 地點分布:")
            for location, count in location_counts.most_common():
                print(f"   {location}: {count} 個職缺")
        
        # 相關度統計
        relevance_scores = [job.get('relevance_score', 0) for job in jobs]
        if relevance_scores:
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            print(f"\\n⭐ 平均相關度: {avg_relevance:.2f}")
            print(f"   最高相關度: {max(relevance_scores)}")
            print(f"   最低相關度: {min(relevance_scores)}")
        
        # 薪資統計
        salaries = [job.get('salary') for job in jobs 
                   if job.get('salary') and job.get('salary') != 'N/A']
        print(f"\\n💰 有薪資資訊的職缺: {len(salaries)} 個 ({len(salaries)/len(jobs)*100:.1f}%)")
        
        # 發布時間統計
        publish_dates = [job.get('publish_date') for job in jobs 
                        if job.get('publish_date') and job.get('publish_date') != 'N/A']
        print(f"📅 有發布時間的職缺: {len(publish_dates)} 個 ({len(publish_dates)/len(jobs)*100:.1f}%)")
    
    def crawl_multiple_pages(self, keyword="資料工程師", max_pages=3):
        """
        爬取多頁職缺資料
        
        Args:
            keyword (str): 搜尋關鍵字
            max_pages (int): 最大頁數
        
        Returns:
            list: 所有職缺資訊列表
        """
        all_jobs = []
        
        for page in range(1, max_pages + 1):
            print(f"\\n🔄 正在爬取第 {page} 頁...")
            
            html_content = self.search_jobs(keyword, page)
            if html_content:
                jobs = self.parse_jobs(html_content)
                if jobs:
                    all_jobs.extend(jobs)
                    print(f"✅ 第 {page} 頁爬取完成，獲得 {len(jobs)} 個職缺")
                else:
                    print(f"⚠️ 第 {page} 頁沒有找到職缺")
                    break
            else:
                print(f"❌ 第 {page} 頁爬取失敗")
                break
            
            # 頁面間延遲
            if page < max_pages:
                time.sleep(random.uniform(2, 4))
        
        # 重新編號
        for i, job in enumerate(all_jobs):
            job['index'] = i + 1
        
        return all_jobs


def main():
    """主程式"""
    print("🚀 1111 人力銀行職缺爬蟲")
    print("=" * 50)
    
    # 建立爬蟲實例
    crawler = Job1111Crawler()
    
    # 設定搜尋參數
    keyword = input("請輸入搜尋關鍵字 (預設: 資料工程師): ").strip() or "資料工程師"
    
    try:
        max_pages = int(input("請輸入要爬取的頁數 (預設: 1): ").strip() or "1")
    except ValueError:
        max_pages = 1
    
    # 開始爬取
    print(f"\\n🎯 開始搜尋 '{keyword}' 相關職缺...")
    
    if max_pages == 1:
        # 單頁爬取
        html_content = crawler.search_jobs(keyword)
        if html_content:
            jobs = crawler.parse_jobs(html_content)
        else:
            jobs = []
    else:
        # 多頁爬取
        jobs = crawler.crawl_multiple_pages(keyword, max_pages)
    
    if jobs:
        # 顯示結果
        crawler.display_jobs(jobs)
        
        # 統計分析
        crawler.analyze_jobs(jobs)
        
        # 儲存檔案
        filename = f"/Users/txwu/project/data/GetOffer/data/1111_{keyword.replace(' ', '_')}_jobs.csv"
        df = crawler.save_to_csv(jobs, filename)
        
        print(f"\\n🎉 爬取完成！共獲得 {len(jobs)} 個職缺資料")
        
    else:
        print("❌ 沒有找到任何職缺資料")


if __name__ == "__main__":
    main()