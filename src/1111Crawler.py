import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import time
import random
from collections import Counter
import urllib3
import warnings
from datetime import datetime

# 忽略 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')


class Job1111Crawler:
    """1111 人力銀行職缺爬蟲類別"""
    
    def __init__(self):
        """初始化爬蟲"""
        self.base_url = "https://www.1111.com.tw"
        self.setup_session()
        print("1111 人力銀行爬蟲已初始化")
    
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
            
            print(f"搜尋關鍵字: {keyword}, 第 {page} 頁")
            
            response = self.session.get(
                f"{self.base_url}/search/job", 
                params=params, 
                timeout=15
            )
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                print(f"成功獲取搜尋結果")
                return response.text
            else:
                print(f"搜尋失敗，狀態碼: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("請求超時")
            return None
        except requests.exceptions.ConnectionError:
            print("連線錯誤")
            return None
        except Exception as e:
            print(f"搜尋錯誤: {e}")
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
        
        # 使用多種選擇器找到職缺卡片
        job_cards = soup.select('.job-card')
        if not job_cards:
            job_cards = soup.select('.job-list-item')
        if not job_cards:
            job_cards = soup.select('[class*="job"]')
        
        print(f"找到 {len(job_cards)} 個職缺卡片")
        
        for i, card in enumerate(job_cards):
            job_info = self.extract_job_from_card(card, i+1)
            if job_info:
                jobs.append(job_info)
        
        return jobs
    
    def extract_industry(self, card):
        """
        提取產業類別
        
        Args:
            card: BeautifulSoup 職缺卡片元素
        
        Returns:
            str: 產業類別
        """
        # 方法1: 尋找包含「產業」關鍵字的元素
        industry_elem = card.find(class_=re.compile(r'industry|category|type', re.I))
        if industry_elem:
            return industry_elem.get_text(strip=True)
        
        # 方法2: 尋找特定的產業標籤
        industry_tag = card.find('span', class_=re.compile(r'tag|label|badge', re.I))
        if industry_tag:
            text = industry_tag.get_text(strip=True)
            # 檢查是否為產業類別（通常包含「業」字）
            if '業' in text or '產業' in text:
                return text
        
        # 方法3: 從文字中提取產業資訊
        card_text = card.get_text()
        
        # 常見產業關鍵字模式
        industry_patterns = [
            r'產業[：:]\s*([^\n\|]+)',
            r'產業類別[：:]\s*([^\n\|]+)',
            r'(軟體.*?業|資訊.*?業|電子.*?業|製造.*?業|金融.*?業|服務.*?業|零售.*?業|醫療.*?業|教育.*?業|建築.*?業|運輸.*?業|餐飲.*?業|旅遊.*?業|媒體.*?業|通訊.*?業)',
            r'(網路相關業|電腦.*?相關業|半導體業|光電業|通信.*?業|顧問.*?業|人力.*?業|廣告.*?業|出版.*?業|娛樂.*?業)',
        ]
        
        for pattern in industry_patterns:
            match = re.search(pattern, card_text)
            if match:
                industry = match.group(1).strip()
                # 清理產業名稱
                industry = re.sub(r'\s+', ' ', industry)
                industry = industry.split('|')[0].strip()
                if len(industry) > 2 and len(industry) < 50:
                    return industry
        
        # 方法4: 從所有 span 標籤中尋找
        all_spans = card.find_all('span')
        for span in all_spans:
            text = span.get_text(strip=True)
            # 檢查是否符合產業類別特徵
            if ('業' in text or '產業' in text) and len(text) < 30 and len(text) > 3:
                # 排除一些非產業的文字
                exclude_keywords = ['職業', '專業', '畢業', '作業', '營業', '就業', '創業']
                if not any(keyword in text for keyword in exclude_keywords):
                    return text
        
        return 'N/A'
    
    def extract_requirements(self, card):
        """
        提取要求條件
        
        Args:
            card: BeautifulSoup 職缺卡片元素
        
        Returns:
            dict: 包含六種要求條件的字典
        """
        requirements = {
            'education': 'N/A',      # 學歷要求
            'department': 'N/A',     # 科系要求
            'experience': 'N/A',     # 工作經驗
            'language': 'N/A',       # 外語能力
            'skills': 'N/A',         # 工作技能
            'additional': 'N/A'      # 附加條件
        }
        
        card_text = card.get_text()
        
        # 1. 學歷要求
        education_patterns = [
            r'學歷要求[：:]\s*([^\n]+)',
            r'學歷[：:]\s*([^\n\|]+)',
            r'(大學|碩士|博士|專科|高中職|國中|不拘)(?:以上)?',
        ]
        for pattern in education_patterns:
            match = re.search(pattern, card_text)
            if match:
                edu = match.group(1).strip()
                # 清理學歷文字
                edu = re.sub(r'\s+', ' ', edu)
                if len(edu) < 50:
                    requirements['education'] = edu
                    break
        
        # 2. 科系要求
        department_patterns = [
            r'科系要求[：:]\s*([^\n]+)',
            r'科系[：:]\s*([^\n\|]+)',
            r'(?:相關)?科系[：:]?\s*([^\n\|]{2,30})',
        ]
        for pattern in department_patterns:
            match = re.search(pattern, card_text)
            if match:
                dept = match.group(1).strip()
                # 清理科系文字
                dept = re.sub(r'\s+', ' ', dept)
                if len(dept) < 100 and '不拘' not in dept:
                    requirements['department'] = dept
                    break
        
        # 如果找到「不拘」，則設為不拘
        if '科系不拘' in card_text or '科系：不拘' in card_text:
            requirements['department'] = '不拘'
        
        # 3. 工作經驗
        experience_patterns = [
            r'工作經驗[：:]\s*([^\n]+)',
            r'經驗[：:]\s*([^\n\|]+)',
            r'(\d+年以上|\d+年|\d+\s*[-~至]\s*\d+年|不拘|無經驗可|應屆畢業生)',
        ]
        for pattern in experience_patterns:
            match = re.search(pattern, card_text)
            if match:
                exp = match.group(1).strip()
                # 清理經驗文字
                exp = re.sub(r'\s+', ' ', exp)
                if len(exp) < 50:
                    requirements['experience'] = exp
                    break
        
        # 4. 外語能力
        language_patterns = [
            r'外語能力[：:]\s*([^\n]+)',
            r'語言[：:]\s*([^\n\|]+)',
            r'(英文|日文|韓文|法文|德文|西班牙文)[：:]?\s*([^\n\|]{2,30})',
            r'(TOEIC|多益|托福|雅思)\s*(\d+)(?:分)?(?:以上)?',
        ]
        for pattern in language_patterns:
            match = re.search(pattern, card_text)
            if match:
                lang = match.group(0).strip()
                # 清理語言文字
                lang = re.sub(r'\s+', ' ', lang)
                if len(lang) < 100:
                    requirements['language'] = lang
                    break
        
        # 如果找到「不拘」，則設為不拘
        if '語言不拘' in card_text or '外語：不拘' in card_text:
            requirements['language'] = '不拘'
        
        # 5. 工作技能
        skills_patterns = [
            r'工作技能[：:]\s*([^\n]+)',
            r'技能[：:]\s*([^\n\|]+)',
            r'擅長工具[：:]\s*([^\n]+)',
        ]
        
        # 常見技能關鍵字
        skill_keywords = [
            'Python', 'Java', 'SQL', 'JavaScript', 'C\+\+', 'C#', 'PHP', 'Ruby',
            'Spark', 'Hadoop', 'Kafka', 'Airflow', 'Docker', 'Kubernetes',
            'AWS', 'Azure', 'GCP', 'Linux', 'Git', 'ETL',
            'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'Tableau', 'Power BI', 'Excel', 'R語言'
        ]
        
        # 先嘗試從特定模式提取
        for pattern in skills_patterns:
            match = re.search(pattern, card_text)
            if match:
                skills = match.group(1).strip()
                # 清理技能文字
                skills = re.sub(r'\s+', ' ', skills)
                if len(skills) < 200:
                    requirements['skills'] = skills
                    break
        
        # 如果沒找到，則搜尋常見技能關鍵字
        if requirements['skills'] == 'N/A':
            found_skills = []
            for skill in skill_keywords:
                if re.search(skill, card_text, re.IGNORECASE):
                    found_skills.append(skill)
            
            if found_skills:
                requirements['skills'] = ', '.join(found_skills[:10])  # 最多列出10個
        
        # 6. 附加條件
        additional_patterns = [
            r'附加條件[：:]\s*([^\n]+)',
            r'其他條件[：:]\s*([^\n]+)',
            r'(需.*?證照|具.*?證照|持有.*?證照)',
            r'(可配合.*?|願意.*?|需.*?)',
        ]
        
        additional_items = []
        for pattern in additional_patterns:
            matches = re.finditer(pattern, card_text)
            for match in matches:
                item = match.group(1) if match.lastindex else match.group(0)
                item = item.strip()
                if len(item) < 100 and item not in additional_items:
                    additional_items.append(item)
        
        if additional_items:
            requirements['additional'] = ' | '.join(additional_items[:3])  # 最多列出3個
        
        return requirements
    
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
                company_match = re.search(r'([^｜\n\r\t]+(?:股份有限公司|有限公司|公司))', all_text)
                if company_match:
                    job_info['company'] = company_match.group(1).strip()
                else:
                    # 提取卡片中的公司資訊
                    company_text = all_text.split('\n')[0] if '\n' in all_text else all_text[:50]
                    job_info['company'] = company_text.strip()
            else:
                job_info['company'] = company_elem.get_text(strip=True)
            
            # 產業類別
            job_info['industry'] = self.extract_industry(card)
            
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
                    r'月薪\s*(\d+[,\d]*\s*[-~至]\s*\d+[,\d]*|\d+[,\d]*)\s*元',
                    r'年薪\s*(\d+[,\d]*\s*[-~至]\s*\d+[,\d]*|\d+[,\d]*)\s*元',
                    r'(\d+[,\d]*\s*[-~至]\s*\d+[,\d]*)\s*元',
                    r'薪資\s*(\d+[,\d]*\s*[-~至]\s*\d+[,\d]*)',
                    r'面議.*經常性薪資達(\d+[,\d]*)萬?元'
                ]
                
                for pattern in salary_patterns:
                    salary_match = re.search(pattern, card_text)
                    if salary_match:
                        job_info['salary'] = salary_match.group(0)
                        break
            
            # 提取要求條件（新增）
            requirements = self.extract_requirements(card)
            job_info['education'] = requirements['education']
            job_info['department'] = requirements['department']
            job_info['experience'] = requirements['experience']
            job_info['language'] = requirements['language']
            job_info['skills'] = requirements['skills']
            job_info['additional'] = requirements['additional']
            
            # 發布時間
            time_patterns = [r'\d+/\d+', r'\d+天前', r'昨天', r'今天', r'\d+小時前']
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
                job_info['summary'] = summary_text.replace('\n', ' ').strip()
            
            # 計算相關度評分
            job_info['relevance_score'] = self.calculate_relevance_score(card_text)
            
            # 確保至少有標題才返回
            return job_info if job_info.get('title') else None
            
        except Exception as e:
            print(f"解析職缺卡片 {index} 時發生錯誤: {e}")
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
    
    def save_to_csv(self, jobs, keyword='jobs'):
        """
        儲存職缺資料到 CSV 檔案（檔名包含日期時間）
        
        Args:
            jobs (list): 職缺資訊列表
            keyword (str): 搜尋關鍵字
        
        Returns:
            pandas.DataFrame: 職缺資料框
        """
        if not jobs:
            print("沒有職缺資料可儲存")
            return None
        
        df = pd.DataFrame(jobs)
        
        # 調整欄位順序，將要求條件放在前面
        column_order = [
            'index', 'title', 'company', 'industry', 'location', 'salary',
            'education', 'department', 'experience', 'language', 'skills', 'additional',
            'publish_date', 'relevance_score', 'summary', 'link'
        ]
        
        # 只保留存在的欄位
        column_order = [col for col in column_order if col in df.columns]
        df = df[column_order]
        
        # 生成包含日期時間的檔案名稱
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"/Users/txwu/project/data/GetOffer/data/1111_{keyword.replace(' ', '_')}_{timestamp}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"已儲存 {len(jobs)} 筆職缺資料到 {filename}")
        return df
    
    def analyze_jobs(self, jobs):
        """
        分析職缺統計資訊
        
        Args:
            jobs (list): 職缺資訊列表
        """
        if not jobs:
            print("沒有職缺資料可分析")
            return
        
        print(f"統計分析")
        print("=" * 50)
        
        # 公司統計
        companies = [job.get('company') for job in jobs 
                    if job.get('company') and job.get('company') != 'N/A']
        if companies:
            company_counts = Counter(companies)
            print(f"公司分布 (前5名):")
            for company, count in company_counts.most_common(5):
                print(f"   {company}: {count} 個職缺")
        
        # 產業統計
        industries = [job.get('industry') for job in jobs 
                     if job.get('industry') and job.get('industry') != 'N/A']
        if industries:
            industry_counts = Counter(industries)
            print(f"產業分布:")
            for industry, count in industry_counts.most_common():
                print(f"   {industry}: {count} 個職缺")
        
        # 地點統計
        locations = [job.get('location') for job in jobs 
                    if job.get('location') and job.get('location') != 'N/A']
        if locations:
            location_counts = Counter(locations)
            print(f"地點分布:")
            for location, count in location_counts.most_common():
                print(f"   {location}: {count} 個職缺")
        
        # 學歷要求統計
        educations = [job.get('education') for job in jobs 
                     if job.get('education') and job.get('education') != 'N/A']
        if educations:
            education_counts = Counter(educations)
            print(f"學歷要求分布:")
            for education, count in education_counts.most_common():
                print(f"   {education}: {count} 個職缺")
        
        # 工作經驗統計
        experiences = [job.get('experience') for job in jobs 
                      if job.get('experience') and job.get('experience') != 'N/A']
        if experiences:
            experience_counts = Counter(experiences)
            print(f"工作經驗要求分布:")
            for experience, count in experience_counts.most_common():
                print(f"   {experience}: {count} 個職缺")
        
        # 相關度統計
        relevance_scores = [job.get('relevance_score', 0) for job in jobs]
        if relevance_scores:
            avg_relevance = sum(relevance_scores) / len(relevance_scores)
            print(f"平均相關度: {avg_relevance:.2f}")
            print(f"   最高相關度: {max(relevance_scores)}")
            print(f"   最低相關度: {min(relevance_scores)}")
        
        # 各項資料完整度統計
        print(f"\n資料完整度:")
        print(f"   有薪資資訊: {len([j for j in jobs if j.get('salary') and j.get('salary') != 'N/A'])} 個 ({len([j for j in jobs if j.get('salary') and j.get('salary') != 'N/A'])/len(jobs)*100:.1f}%)")
        print(f"   有學歷要求: {len(educations)} 個 ({len(educations)/len(jobs)*100:.1f}%)")
        print(f"   有科系要求: {len([j for j in jobs if j.get('department') and j.get('department') != 'N/A'])} 個 ({len([j for j in jobs if j.get('department') and j.get('department') != 'N/A'])/len(jobs)*100:.1f}%)")
        print(f"   有經驗要求: {len(experiences)} 個 ({len(experiences)/len(jobs)*100:.1f}%)")
        print(f"   有外語要求: {len([j for j in jobs if j.get('language') and j.get('language') != 'N/A'])} 個 ({len([j for j in jobs if j.get('language') and j.get('language') != 'N/A'])/len(jobs)*100:.1f}%)")
        print(f"   有技能要求: {len([j for j in jobs if j.get('skills') and j.get('skills') != 'N/A'])} 個 ({len([j for j in jobs if j.get('skills') and j.get('skills') != 'N/A'])/len(jobs)*100:.1f}%)")
        print(f"   有附加條件: {len([j for j in jobs if j.get('additional') and j.get('additional') != 'N/A'])} 個 ({len([j for j in jobs if j.get('additional') and j.get('additional') != 'N/A'])/len(jobs)*100:.1f}%)")
    
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
            print(f"正在爬取第 {page} 頁...")
            
            html_content = self.search_jobs(keyword, page)
            if html_content:
                jobs = self.parse_jobs(html_content)
                if jobs:
                    all_jobs.extend(jobs)
                    print(f"第 {page} 頁爬取完成，獲得 {len(jobs)} 個職缺")
                else:
                    print(f"第 {page} 頁沒有找到職缺")
                    break
            else:
                print(f"第 {page} 頁爬取失敗")
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
    print("1111 人力銀行職缺爬蟲")
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
    print(f"開始搜尋 '{keyword}' 相關職缺...")
    
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
        # 統計分析
        crawler.analyze_jobs(jobs)
        
        # 儲存檔案（檔名包含日期時間）
        df = crawler.save_to_csv(jobs, keyword)
        
        print(f"爬取完成！共獲得 {len(jobs)} 個職缺資料")
        
    else:
        print("沒有找到任何職缺資料")


if __name__ == "__main__":
    main()
