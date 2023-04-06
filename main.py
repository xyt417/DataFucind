import os
import math
from collections import defaultdict
from bs4 import BeautifulSoup
import requests
import selenium
from selenium import webdriver
import re
import time

class RetrievalModel: # 定义一个名为RetrievalModel的类 RetrievalModel:检索模型
    def __init__(self, path): # 定义初始化函数，传入参数为文件路径
        self.path = path # 将文件路径赋值给self.path
        self.index = defaultdict(dict) # 定义一个默认字典用于存储倒排索引
        self.doc_length = {} # 定义一个空字典用于存储每个文档的长度
        self.total_length = 0 # 定义一个变量用于存储所有文档总长度 所有文件长度之和是指所有文件中所有词的长度之和？
        self.docs = [] # 定义一个空列表用于存储所有文档文件名
        self.stop_words = set() # 定义一个空集合用于存储停用词表
        self.load_stop_words() # 载入停用词表
        self.build_index() # 建立倒排索引
        self.compute_lengths() # 计算每个文档的长度
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36', 
            # "Cookie": 'first_visit_datetime_pc=2023-04-03+20:05:21; p_ab_id=6; p_ab_id_2=4; p_ab_d_id=1639917103; yuid_b=J4OFEVE; _fbp=fb.1.1680519923390.2095052467; PHPSESSID=71354849_ImIU8T760AzZaIuigmucF7bfvSy0Hjg8; device_token=a7eaec54414b62037030260d34dff8a1; privacy_policy_agreement=5; c_type=22; privacy_policy_notification=0; a_type=0; b_type=0; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; p_b_type=1; tag_view_ranking=0xsDLqCEW6~Lt-oEicbBr~r_Jjn6Ua2V~HY55MqmzzQ~uvBGOtCzqF~_vCZ2RLsY2~5oPIfUbtd6~68luzZqFS0~-7RnTas_L3~jk9IzfjZ6n~tLEo7GtjcE~iRFlj3p1GG~ctjJwbmssT~uW5495Nhg-~O4zMr8hRGP~EYYBFpYNJp~98FF78f4J0~bYn3xr0RaN~zqe8dqUBGC~ckoqr0bPHv~5oHuFQXax5~rOnsP2Q5UN~_EOd7bsGyl~6n5sWl9nNm~tJaVY8ie4B~qG6ZMBxhkE~QaiOjmwQnI~ZTBAtZUDtQ~zaEtI28sYq~qXzcci65nj~TWrozby2UO~ncUG68iRRJ~PwDMGzD6xn~-LwvviyTfq~faHcYIP1U0~Ie2c51_4Sp~uK-xlAOB9q~0r_Dr-UWZa~wmxKAirQ_H~vrf3o5XcIa~pNtQi6YIt-~NGpDowiVmM~gCB7z_XWkp~vzTU7cI86f~azESOjmQSV~zyKU3Q5L4C~nIjJS15KLN~qkC-JF_MXY~4QveACRzn3~cnS1oIcWKc~aKhT3n4RHZ~HZk-7ZdqP6~w8ffkPoJ_S~HBlflqJjBZ~T40wdiG5yy~CEYqcod4iE~D4hLr_YmAD~_C6hhzFNWQ~gnmsbf1SSR~LX3_ayvQX4~r6jbYbwfYK~OgLi_QXWK2~fW51ff7RoH~DDIrgPa5XM~eVxus64GZU~KhhTM1zuNN~rI4MmDPPTp~FdBF-J6Pun~PnFukw__z_~LiGJo4dg8B~BtH0Tl8o51; _gid=GA1.2.812029370.1680713774; __cf_bm=jJRIu1fs568CGkJIsX1_hJBVI.9EAvWTv.DMD.20ExE-1680714712-0-AdhsU2aHwsmfFW8X25KWbCE4Yclwr8ddzk0ynWxWq3q4Atv1jx+4NN8YYAeC0zyxnEz3UC8QgiQLrZY68YpSPyj0BmhnfxTeZiF3HdTnqWcpTG8h6aXRsJ+AtrDMnGU7Nmi9hB55m3Q2bn1NNTANGXYWFgVkd0JtHxC6mK8vBnuw0X6gObB0jC4XYQbld0nt8w==; _ga=GA1.1.900687260.1680519923; _ga_75BBYNYN9J=GS1.1.1680713769.5.1.1680715263.0.0.0',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
        }

    def load_stop_words(self): # 定义载入停用词表的函数
        with open('stop_words.txt', 'r', encoding='utf-8') as f: # 打开停用词表文件
            for line in f: # 遍历文件中的每一行
                self.stop_words.add(line.strip()) # 将去除空白符的行添加到停用词表中

    #倒牌索引的概念是什么？
    #倒排索引是一种数据结构，它将文档中的每个单词与包含该单词的文档列表相关联。倒排索引是一种非常有效的数据结构，因为它允许我们快速地找到包含特定单词的文档。在这里，我们将使用一个字典来存储倒排索引。字典的键是单词，值是一个字典，该字典的键是文档ID，值是单词在文档中出现的次数。
    def build_index(self): # 定义建立倒排索引函数
        for doc_id, file in enumerate(os.listdir(self.path)): # 遍历文件夹中的每个文件 enumrate()函数用于将一个可遍历的数据对象组合为一个索引序列，同时列出数据和数据下标
            self.docs.append(file) # 将文件名添加到文档列表中
            with open(os.path.join(self.path, file), 'r', encoding='utf-8') as f: # 打开文件
                for line in f: # 遍历文件中的每一行
                    tokens = line.strip().split() # 将每行转换为单词列表
                    for token in tokens: # 遍历单词列表中的每个单词
                        if token not in self.stop_words: # 如果单词不在停用词表中
                            self.index[token][doc_id] = self.index[token].get(doc_id, 0) + 1 # 在倒排索引中添加单词和文档ID的映射关系

    def compute_lengths(self): # 定义计算文档长度的函数
        for doc_id in range(len(self.docs)): # 遍历每个文档
            length = 0 # 初始化文档长度为0
            for term, freq in self.index.items(): # 遍历每个单词在倒排索引中的出现频率
                tf = freq.get(doc_id, 0) # 获取该单词在该文档中的出现次数
                if tf > 0: # 如果出现次数大于0
                    length += (1 + math.log(tf)) # 将该单词的长度加到文档长度上
            self.doc_length[doc_id] = length # 将文档长度添加到文档长度字典中
            self.total_length += length # 将文档长度加到所有文档总长度上

    def calculate_query_vector(self, query): # 定义计算查询向量的函数
        query_vector = defaultdict(int) # 定义一个默认字典用于存储查询向量
        for term in query.strip().split(): # 遍历查询中的每个单词
            if term not in self.stop_words: # 如果单词不在停用词表中
                query_vector[term] += 1 # 在查询向量中添加单词和出现次数的映射关系
        length = math.sqrt(sum(map(lambda x: x*x, query_vector.values()))) # 计算查询向量的长度
        for term, freq in query_vector.items(): # 遍历查询向量中的每个单词和出现次数
            query_vector[term] = freq / length # 将每个单词的出现次数除以查询向量的长度，得到单词的权重
        return query_vector # 返回查询向量

    def calculate_score(self, query): # 定义计算文档得分的函数
        query_vector = self.calculate_query_vector(query) # 调用计算查询向量的函数，得到查询向量
        scores = defaultdict(float) # 定义一个默认字典用于存储文档得分
        for term, freq in query_vector.items(): # 遍历查询向量中的每个单词和出现次数
            if term in self.index: # 如果单词在倒排索引中
                idf = math.log(len(self.docs) / len(self.index[term])) # 计算单词的逆文档频率
                for doc_id, tf in self.index[term].items(): # 遍历单词在倒排索引中的每个文档ID和出现次数
                    tf_weight = 1 + math.log(tf) # 计算单词的权重
                    scores[doc_id] += freq * tf_weight * idf # 计算文档得分
        for doc_id, score in scores.items(): # 遍历文档得分中的每个文档ID和得分
            scores[doc_id] /= self.doc_length[doc_id] / self.total_length # 将得分除以文档长度的比例和所有文档总长度的比例
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True) # 将文档得分按照得分从大到小排序
        return sorted_scores # 返回排序后的文档得分列表

    def search(self, query, num_results=10): # 定义查询函数
        results = self.calculate_score(query)[:num_results] # 调用计算文档得分的函数，取前num_results个文档
        for doc_id, score in results: # 遍历所有结果中的每个文档ID和得分
            print('Document:', self.docs[doc_id]) # 打印文档名
            print('Score:', score) # 打印得分
            with open(os.path.join(self.path, self.docs[doc_id]), 'r', encoding='utf-8') as f: # 打开文档
                print('Content:', f.readline().strip()) # 打印文档内容的第一行
            print('---') # 打印分割线

    def crawl(self, url, depth=1): # 定义爬取函数
        file = open('text', 'w+') # 打开urls.txt文件
        if depth == 0: # 如果爬取深度为0
            return # 返回
        # try: # 尝试执行以下代码
        print('-' * 30) # 打印分割线'
        print('Crawling:', url) # 打印爬取的网页地址
        response = requests.get(url) # 发送GET请求
        if response.status_code == 200: # 如果请求成功
            print('Status code:', response.status_code) # 打印状态码
            print('Content type:', response.headers['Content-Type']) # 打印内容类型
            print('Encoding:', response.encoding) # 打印编码方式
            print('-' * 30) # 打印分割线
            #ISO-8859-1 转 gnk
            text = response.text.encode(response.encoding).decode('gbk', errors='ignore') # 将网页内容从response.encoding编码转换为utf-8编码
            soup = BeautifulSoup(text, 'lxml') # 使用BeautifulSoup解析网页
            for link in soup.find_all('a'): # 遍历网页中的每个链接
                if link.has_attr('href'): # 如果链接有href属性
                    if link['href'].startswith('http'): # 如果链接以http开头
                        self.crawl(link['href'], depth-1) # 递归调用爬取函数，爬取深度减1
                    else:
                        self.crawl(url + link['href'], depth-1) # 递归调用爬取函数，爬取深度减1
            text = soup.get_text() # 获取网页中的文本
            text = re.sub(r'\s+', ' ', text) # 将文本中的多个空格替换为一个空格
            text = re.sub(r'\n', ' ', text) # 将文本中的换行符替换为空格
            text = re.sub(r'\t', ' ', text) # 将文本中的制表符替换为空格
            text = re.sub(r'\xa0', ' ', text) # 将文本中的不间断空格替换为空格
            text = re.sub(r'\u3000', ' ', text) # 将文本中的全角空格替换为空格
            text = re.sub(r'[^\w\s]', ' ', text) # 将文本中的非单词和非空格字符替换为空格
            text = re.sub(r'\s+', ' ', text) # 将文本中的多个空格替换为一个空格
            text = text.strip() # 去掉文本两端的空格
            file.write(text)
            if len(text): # 如果文本不为空
                print('Text length:', len(text)) # 打印文本长度
                self.docs.append(url) # 将网址添加到文档列表中
                self.doc_length[url] = len(text) # 将文档长度添加到文档长度列表中
                self.total_length += len(text) # 将文档长度添加到总长度中
                with open(os.path.join(self.path, url.replace('/', '_')), 'w+', encoding='utf-8') as f: # 打开文档
                    f.write(text) # 写入文本
                    print('Saved to:', os.path.join(self.path, url.replace('/', '_'))) # 打印文档保存路径
        else:
            print('Error:', response.status_code)
        # except: # 如果发生异常
        #     print('Exception!')



rm = RetrievalModel('HongLouMeng') # 创建一个RetrievalModel对象，传入文件路径
rm.crawl('http://www.purepen.com/hlm/', depth=2) # 调用爬取函数，传入网址和爬取深度
# rm.build_index() # 调用建立索引的函数
# rm.search('魔法少女') # 调用查询函数，传入查询字符串


