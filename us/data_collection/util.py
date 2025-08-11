import requests
from bs4 import BeautifulSoup
import time
from random import randint
import requests
from requests.exceptions import SSLError, RequestException
import multiprocessing
from tqdm import tqdm  # Import tqdm for progress bars
import re
import json
import time
import brotli
import random

class ProxyManager:

    def __init__(self, proxy_url, file_path='proxies.txt',headers=None,proxy_num=50):
        self.proxy_url = proxy_url
        self.proxies = []
        self.headers = headers
        self.file_path = file_path
        self.load_proxies_from_file()
        self.proxy_num=proxy_num

    def save_proxies_to_file(self, proxies):
        """将代理保存到文本文件。"""
        with open(self.file_path, 'w') as file:
            for proxy in proxies:
                # file.write(f"{proxy['http']}|{proxy['https']}\n")
                file.write(f"{proxy['http']}\n")

    def load_proxies_from_file(self):
        """从文本文件加载代理。"""
        proxies = []
        try:
            with open(self.file_path, 'r') as file:
                for line in file:
                    # http, https = line.strip().split('|')
                    # proxies.append({'http': http})
                    proxies.append({'http': line.strip()})
            self.proxies = proxies
        except FileNotFoundError:
            print("代理文件不存在，将从网络获取新代理。")
        

    def get_proxies(self):
        """从指定URL获取代理，并验证其有效性。"""
        try:
            response = requests.get(self.proxy_url)
            response.raise_for_status()  # 检查HTTP请求是否成功
            proxy_list = response.text.strip().split('\n')
            # 提供给我的代理太多了，那么就需要手动选取前100个，不然验证哪一些可用太繁琐了
            random_proxy_mask = [random.randint(0, len(proxy_list) - 1) for _ in range(self.proxy_num)]
            # Select proxies based on the random indices
            selected_proxies = [proxy_list[i] for i in random_proxy_mask]
            temp_proxies = [{'http': f'http://{proxy}'} for proxy in selected_proxies]
            # 这100个代理有很多不可用，即连接不上'https://www.tripadvisor.com/'，那么我们首先需要验证一下它们哪些可用
            # self.proxies = self.verify_proxies(temp_proxies)  # 验证代理并更新列表
            self.proxies = temp_proxies
            
            self.save_proxies_to_file(self.proxies)
            if(len(self.proxies)==0):
                print('一个ok的代理都没有拿到,原始代理包括'+ str(temp_proxies))
            else:
                self.save_proxies_to_file(self.proxies)
                print('拿到通过检验的代理，共 '+ str(len(self.proxies))+" 个，包括 "+str(self.proxies))
        except requests.RequestException as e:
            print(f"获取代理时出错: {e}")
            self.proxies = self.load_proxies_from_file()

    def verify_proxies(self, proxies, test_url='https://www.tripadvisor.com/'):
        """验证代理列表中的每个代理是否能够访问指定URL。"""
        working_proxies = []
        for proxy in tqdm(proxies, desc="Verifying proxies", unit="proxy"):
            try:
                # 连接超过5秒就认为这个代理不行
                response = requests.get(test_url,headers=self.headers, proxies=proxy, timeout=5)
                if response.ok:  # 如果请求成功，认为代理有效
                    working_proxies.append(proxy)
            except requests.RequestException:
                # 这里不打印失败的代理信息，静默跳过
                pass
        return working_proxies  # 返回验证通过的代理列表

    def update_proxies_periodically(self, interval=1800):
        """每隔指定时间间隔更新代理。"""
        while True:
            print("正在更新代理...")
            self.get_proxies()
            print(f"更新后的代理数量：{len(self.proxies)}")
            time.sleep(interval)

# # 代理列表
# def get_proxies():
#     # URL of the free proxy list website
#     url = "http://list.didsoft.com/get?email=997893314@qq.com&pass=yrh93b&pid=http3000&showcountry=no"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # 检查请求是否成功
#         # 解析响应内容为代理列表
#         proxy_list = response.text.strip().split('\n')
#         # 将每个代理转换为字典格式
#         proxies = [{'http': f'http://{proxy}'} for proxy in proxy_list]
#         return proxies
#     except requests.RequestException as e:
#         print(f"Error fetching proxies: {e}")
#         return []

# 多进程处理单个页面的每一个topic
def start_proxy_update_process(proxy_manager, interval):
    # 启动代理更新进程
    proxy_update_process = multiprocessing.Process(target=proxy_manager.update_proxies_periodically, args=(interval,))
    proxy_update_process.start()
    return proxy_update_process

# 定义处理单个 topic_path 的函数
def process_topic(topic_path, proxy_manager, headers):
    try:
        proxy = get_random_proxy(proxies=proxy_manager.proxies)
        topic_html = fetch_data(proxy_manager, topic_path, proxy)
        if not topic_html:
            print(f'Failed to fetch topic HTML from {topic_path}')
            return None

        comment_soup = BeautifulSoup(topic_html, 'html.parser')
        td = comment_soup.find('div', class_='firstPostBox')

        # 读取 topic 的内容。提取所有 <p> 标签的内容并合并成一个字符串
        try:
            topic_content = ' '.join(p.get_text() for p in td.find_all('p'))
        except:
            topic_content = None

        # 获取 topic 发布的时间
        try:
            topic_time = td.find('div', class_='postDate').text
        except:
            topic_time = None

        # 获取 user_id
        try:
            user_id = re.split(r'[/?]', td.find('div', class_='avatar').find('a').get('href'))[2]
        except:
            user_id = None

        # 获取 posts, reviews 和 helpful votes 数量
        try:
            posts = td.find('div', class_='postBadge badge').find('span').text.split()[0]
        except:
            posts = 0

        try:
            reviews = td.find('div', class_='reviewerBadge badge').find('span').text.split()[0]
        except:
            reviews = 0

        try:
            helpful_votes = td.find('div', class_='helpfulVotesBadge badge').find('span').text.split()[0]
        except:
            helpful_votes = 0

        # 如果这个 topic 发布的时间为若干 years ago，那么试一下找到它的 dateCreated
        if "ago" in topic_time:
            try:
                script_tag = comment_soup.find('script', type="application/ld+json")
                json_data = json.loads(script_tag.string)
                topic_time = json_data['mainEntity']['dateCreated']
            except:
                pass

        try:
            keywords_content = comment_soup.find('meta', attrs={'name': 'keywords'})
        except:
            keywords_content = None

        # 城市
        try:
            city_name = keywords_content.get('content').split(',')[0]
        except:
            city_name = None

        # 州
        try:
            province_name = keywords_content.get('content').split(',')[1]
        except:
            province_name = None

        # topic_name
        try:
            topic_name = ', '.join(keywords_content.get('content').split(',')[2:]).strip()
        except:
            topic_name = None

        # 返回处理好的 topic 数据
        return {
            'user ID': user_id,
            'Topic Name': topic_name.strip(),
            'City': city_name.strip(),
            'Province': province_name.strip(),
            'Content': topic_content.strip() if topic_content else None,
            'Posts': str(posts),
            'Reviews': str(reviews),
            'Helpful Votes': str(helpful_votes),
            'Date Created': topic_time
        }

    except Exception as e:
        print(f'Error processing topic at {topic_path}: {e}')
        return None

def get_random_proxy(proxies=None):
    return proxies[randint(0, len(proxies) - 1)]

def fetch_data(proxy_manager, url, proxy=None, max_retries=30, timeout=(5, 15)):  # 将超时时间缩减，90s太长了点
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, headers=proxy_manager.headers, proxies=proxy, timeout=timeout)
            response.raise_for_status()  # 抛出 HTTP 错误
            if response.encoding=='br':
                return brotli.decompress(response.content).decode('utf-8', errors='replace')
            elif response.encoding=='UTF-8':
                return response.text
            return response.text
        except requests.RequestException as e:
            # 每10次尝试失败后重新获取一下proxies
            # if(retries%10==0 and retries!=0):
            #     # proxies = get_proxies()
            #     proxy_manager.get_proxies()
            #     if proxy_manager.proxies:
            #         print("在第"+str(retries)+"次Proxies obtained successfully "+str(proxy_manager.proxies))
            #     else:
            #         print("在第"+str(retries)+"次Failed to obtain proxies")
            print(f"{proxy} Request error: {e}")
            retries += 1
            # time.sleep(randint(0, 2))  # 随机等待 0 到 2 秒后重试。这个甚至可以去掉，因为我们大于50个代理随机取，所以基本不会连续取取同一个代理
            proxy = get_random_proxy(proxies=proxy_manager.proxies)
    # 所有代理尝试失败后，尝试直接本地连接
    print("All proxy attempts failed, trying direct local connection...")
    try:
        response = requests.get(url, headers=proxy_manager.headers, timeout=timeout)
        response.raise_for_status()
        print("Direct local request successful!")
        if response.encoding=='br':
            return brotli.decompress(response.content).decode('utf-8', errors='replace')
        elif response.encoding=='UTF-8':
                return response.text
    except requests.RequestException as e:
        print(f"Direct local request error: {e}")
        return None