# coding=utf-8
import random

import openpyxl
import requests
import configparser
import base64
from gevent import monkey, pool; monkey.patch_all()
import xlsxwriter
from bs4 import BeautifulSoup
import chardet
from urllib.parse import quote
import os

requests.packages.urllib3.disable_warnings()

abs_path = os.getcwd() + os.path.sep

port_rules = {
    'FTP': '21',
    'SSH': '22',
    'Telnet': '23',
    'SMTP': '25',
    'DNS': '53',
    'DHCP': '68',
    'HTTP': '80',
    'TFTP': '69',
    'HTTP': '8080',
    'POP3': '995',
    'NetBIOS': '139',
    'IMAP': '143',
    'HTTPS': '443',
    'SNMP': '161',
    'LDAP': '489',
    'SMB': '445',
    'SMTPS': '465',
    'Linux R RPE': '512',
    'Linux R RLT': '513',
    'Linux R cmd': '514',
    'Rsync': '873',
    'IMAPS': '993',
    'Proxy': '1080',
    'JavaRMI': '1099',
    'Lotus': '1352',
    'MSSQL': '1433',
    'MSSQL': '1434',
    'Oracle': '1521',
    'PPTP': '1723',
    'cPanel': '2082',
    'CPanel': '2083',
    'Zookeeper': '2181',
    'Docker': '2375',
    'Zebra': '2604',
    'MySQL': '3306',
    'Kangle': '3312',
    'RDP': '3389',
    'SVN': '3690',
    'Rundeck': '4440',
    'GlassFish': '4848',
    'PostgreSql': '5432',
    'PcAnywhere': '5632',
    'VNC': '5900',
    'CouchDB': '5984',
    'varnish': '6082',
    'Redis': '6379',
    'Weblogic': '9001',
    'Kloxo': '7778',
    'Zabbix': '8069',
    'RouterOS': '8291',
    'Elasticsearch': '9200',
    'Elasticsearch': '9300',
    'Zabbix': '10050',
    'Zabbix': '10051',
    'Memcached': '11211',
    'MongoDB': '27017',
    'MongoDB': '28017',
    'Hadoop': '50070'
}


class Request:
    def __init__(self, cookie=None):
        self.cookie = cookie

    def get_request(self, url):
        # print(self._get_url(url))
        try:
            resp = requests.get(self._get_url(url), timeout=2, headers=self._get_headers(), verify=False, allow_redirects=True)
            text = resp.content.decode(encoding=chardet.detect(resp.content)['encoding'])
            title = self._get_title(text).strip().replace('\r', '').replace('\n', '')
            status = resp.status_code
            return title, status, resp
        except Exception as e:
            return e


    def get_url_by_port(self, domain, port):
        protocols = ['http://', 'https://']
        if port == 80:
            url = f'http://{domain}'
            return url
        elif port == 443:
            url = f'https://{domain}'
            return url
        else:
            url = []
            for protocol in protocols:
                url.append(f'{protocol}{domain}:{port}')
            return url

    def _get_headers(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) '
            'Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0']
        ua = random.choice(user_agents)
        headers = {
            # "Connection": "keep-alive",
             # "Cookie": "fofa_token=" + self.cookie,
            'User-Agent': ua
        }
        return headers

    def _get_title(self, markup):
        soup = BeautifulSoup(markup, 'lxml')

        title = soup.title
        if title:
            return title.text

        h1 = soup.h1
        if h1:
            return h1.text

        h2 = soup.h2
        if h2:
            return h2.text

        h3 = soup.h3
        if h2:
            return h3.text

        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            return desc['content']

        word = soup.find('meta', attrs={'name': 'keywords'})
        if word:
            return word['content']

        text = soup.text
        if len(text) <= 200:
            return text
        return ''

    def _get_url(self, domain):
        if 'http://' in domain or 'https://' in domain:
            return f'{domain}'
        else:
            return f'http://{domain}'


class TextUtils:
    @staticmethod
    def getUniqueList(L):
        (output, temp) = ([], [])
        for l in L:
            for k, v in l.items():
                flag = False
                if (k, v) not in temp:
                    flag = True
                    break
            if flag:
                output.append(l)
            temp.extend(l.items())
        return output

    @staticmethod
    def getPortService(port):
        for k, v in port_rules.items():
            if v == port:
                return k
        return ''


class FofaSpider():
    def __init__(self, search_keyword):
        self.request = Request()  # 初始化请求类
        self.pageSize = 0
        self.searchKeyword = quote(base64.b64encode(bytes(search_keyword, encoding="utf-8")).decode('utf-8'))
        self._getConfig()  # 初始化配置信息
        self.searchUrl = "https://fofa.so/api/v1/search/all?email={FOFA_EMAIL}&key={API_KEY}&qbase64={B64_DATA}&size=100&page={PAGE}"
        self.webDomainList = []

    # 基于API的爬取
    def _getApiSpider(self):
        webList = []
        for page in range(1, self.pageSize + 1):
            print("===========================")
            print("当前请求的URL: " + self.searchUrl.format(FOFA_EMAIL=self.fofa_email, API_KEY=self.fofa_key,
                                                       B64_DATA=self.searchKeyword, PAGE=page))
            print("===========================")

            #  开始解析数据
            a, b, c = self.request.get_request(self.searchUrl.format(FOFA_EMAIL=self.fofa_email, API_KEY=self.fofa_key, B64_DATA=self.searchKeyword, PAGE=page))
            jsonData = c.json()
            for i in jsonData['results']:
                # a,b,c = self.request.get_request(i[0])
                info = {
                    'spider': 'FOFA',
                    'domain': i[0],
                    'title': '',  # 先不写
                    'ip': i[1],
                    'port': i[2],
                    'web_service': '',  # 先不写
                    'port_service': TextUtils.getPortService(i[2]),
                    'search_keyword': self.searchKeyword
                }
                print(info)
                webList.append(info)

        print(webList)
        gevent_pool = pool.Pool(int(self.thread_num))
        while webList:
            tasks = [gevent_pool.spawn(self._fetchUrl, webList.pop()) for i in
                     range(len(webList[:int(self.thread_num) * 10]))]
            for task in tasks:
                task.join()
            del tasks

    def _getConfig(self):
        conf = configparser.ConfigParser()
        conf.read(__file__[0:-7] + 'fofa.config')  # 读config.ini文件
        self.fofa_key = conf.get('config', 'fofa_key')
        self.fofa_email = quote(conf.get('config', 'fofa_email'))
        self.thread_num = conf.get('config', 'threads')
        # self.cookie = conf.get('config', 'cookie')

    def _getPage(self):
        # 先获取该语法查询的总数量
        a, b, c = self.request.get_request(self.searchUrl.format(FOFA_EMAIL=self.fofa_email, API_KEY=self.fofa_key, B64_DATA=self.searchKeyword, PAGE=1))
        self.pageSize = c.json().get('size') // 100 + 1

    def _writeFile(self):
        workbook = openpyxl.load_workbook(abs_path + "result.xlsx")
        worksheet = workbook.worksheets[0]
        for i in self.webDomainList:
            web = list()
            web.append(i['spider'])
            web.append(i['domain'])
            web.append(i['title'])
            web.append(i['ip'])
            web.append(i['port'])
            web.append(i['web_service'])
            web.append(i['port_service'])
            web.append(i['search_keyword'])
            worksheet.append(web)
        workbook.save(abs_path + "result.xlsx")
        workbook.close()

    def _fetchUrl(self, aDict):
        # 重新再封装一个request: 对于获取标题要使用的request请求
        print("标题扫描: " + str(aDict['domain']) )
        a,b,c = self.request.get_request(aDict['domain'])
        aDict['title'] = a
        aDict['web_service'] = c.headers.get('Server')
        self.webDomainList.append(aDict)


    def run(self):
        self._getPage()
        print("当前语法的总页数为: " + str(self.pageSize))
        Size = input("你想要爬取的页数（回车默认为最大页数）: ")
        if Size == '':
            self.pageSize = self.pageSize
        else:
            Size = int(Size)
            if Size >= 0 and Size <= self.pageSize:
                self.pageSize = Size

        print("最终要爬取的总页数为: {}".format(str(self.pageSize)))

        if self.pageSize == 0:
            print("程序结束，原因为指定的语法查询数量为0!")
            exit(0)
        else:
            self._getApiSpider()

            # 刷新去重一遍
            TextUtils.getUniqueList(self.webDomainList)

            # 写入数据完成
            self._writeFile()


def initXlsx():
    workbook = xlsxwriter.Workbook("result.xlsx")
    worksheet = workbook.add_worksheet('FOFA空间搜索引擎')
    headings = ['空间引擎名', 'HOST', '标题', 'ip', '端口', '服务', '协议', '查询语句']
    worksheet.set_column('A:A', 11)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 37)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 8)
    worksheet.set_column('F:F', 20)
    worksheet.set_column('G:G', 8)
    worksheet.set_column('H:H', 24)
    worksheet.write_row('A1', headings)
    workbook.close()


if '__main__' == __name__:
    if not os.path.exists(abs_path + "result.xlsx"):
        initXlsx()
    search_keyword = input("输入你要的Fofa搜索语法: ")
    fofa = FofaSpider(search_keyword)

    try:
        # fofa.getWebSpider()
        fofa.run()
    except KeyboardInterrupt:
        print("用户 Ctrl+C 结束退出")
        exit(0)
