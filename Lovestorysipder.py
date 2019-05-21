import pymysql
import requests
import bs4
import re
import datetime
import sys
from model.Book import Book
import string
sys.setrecursionlimit(4000)

class DoubanSpider(object):
    """使用面向对象的思想将爬取到的数据存入数据库中"""

    # 初始化
    def __init__(self, url, table_name, book_type):
        self.db = pymysql.connect('localhost', 'root', '123456', 'douban', charset = 'utf8')
        self.cursor = self.db.cursor()
        self.table_name  = table_name
        self.book_type = book_type
        # 创建表格
        # sql语句
        # 作者，译者， 书名， 评分， 出版社， 出版日期， 价格
        #self.cursor.execute('drop table bookinfos if exits')
        self.url = url
        self.response = requests.get(self.url)
        self.soup = bs4.BeautifulSoup(self.response.text, 'html5lib')


    # 优化
    # 就是将类型转换成MySQL匹配的类型
    def change_type(self, book):
        # 分析哪些是需要进行格式化的： 价格  评分 
        if book.get_price():
            # print(book.get_price())
            try:
                self.price_changed = re.findall(r'[0-9]+'+'\.*'+'[0-9]*',book.get_price())[0]
            # print(self.price_changed)
                self.price_changed = float(self.price_changed)
                book.set_price(self.price_changed) 
            except Exception as ret:
                book.set_price(0.00) 
        else:
            book.set_price(0.00)
          
        if book.get_score():
            self.score_changed = float(book.get_score())
            book.set_score(self.score_changed)
        else:
            book.set_score(0.0)
        return book 

    # 获取一个页面的所有书籍信息
    def get_book_info(self):
        # 定义一个book类的集合
        self.bookSet = set()
        # 获取到所有书籍的内容
        self.BookInfoList = self.soup.find_all('li', class_ = 'subject-item')
        # 遍历每本书籍，获取每本书籍的信息
        for every in self.BookInfoList:
            # 创建一个book书籍对象
            book = Book("", "", "", 0.0, "", "", 0.00)
            self.bookInfo = every.find('div', class_ = 'info')
            # 书名
            if "\'" in self.bookInfo.find('a')['title']:
                self.bookInfo.find('a')['title'] = self.bookInfo.find('a')['title'].replace("'", "\\\'")
            book.set_book_name(self.bookInfo.find('a')['title'])
            # 评分
            # print(self.bookInfo.find('span', class_ = 'rating_nums').get_text())
            if self.bookInfo.find('span', class_ = 'rating_nums'):
                if self.bookInfo.find('span', class_ = 'rating_nums').get_text():
                    book.set_score(self.bookInfo.find('span', class_ = 'rating_nums').get_text())
                else:
                    book.set_score(0.0)
            else:
                book.set_score(0.0)
            # 其他信息
            self.otherInfo = self.bookInfo.find('div', class_ = 'pub').get_text()
            self.otherInfoStrip = self.otherInfo.strip()
            # todo 修改参数
            self.otherInfoList = self.otherInfoStrip.split("/")
            # 将单引号进行转换
            for i in range(0, len(self.otherInfoList)):
                if "\'" in self.otherInfoList[i]:
                    self.otherInfoList[i] = self.otherInfoList[i].replace("'", "\\\'")
            book.set_author(self.otherInfoList[0])
            if len(self.otherInfoList) == 4:
                book.set_publish(self.otherInfoList[1])
                book.set_publish_date(self.otherInfoList[2])
                # if len(self.otherInfoList[-1]) >7:
                    # book.set_price(0.0)
                # else:
                book.set_price(self.otherInfoList[3])
                
            elif len(self.otherInfoList) == 5:
                book.set_translater(self.otherInfoList[1])
                book.set_publish(self.otherInfoList[2])
                book.set_publish_date(self.otherInfoList[3])
                # if len(self.otherInfoList[-1]) > 6:
                    # book.set_price(0.0)
                # else:
                book.set_price(self.otherInfoList[4])
                  
            else:
                book.set_price(self.otherInfoList[-1])
            # todo 需要适配其他的情况
            # 先把一个book对象格式化
            book = self.change_type(book)
            self.bookSet.add(book)
        return self.bookSet

    # 将一个set集合的信息写入数据库
    def writeToDB(self):
        self.get_book_info()
        for every in self.bookSet:
            # insert语句
            print(every.get_author(), every.get_translater(), every.get_book_name(),\
                            every.get_score(), every.get_publish(), every.get_publish_date(), every.get_price())

            self.sql = "INSERT INTO `%s`(`author`, `translater`, `book_name`, `score`, \
                `publish`, `publish_date`, `price`, `book_type`)\
                    VALUES('%s', '%s', '%s', %f, '%s', '%s', %f, '%s');"\
                        %(self.table_name, every.get_author(), every.get_translater(), \
                        every.get_book_name(), every.get_score(), every.get_publish(), every.get_publish_date(),\
                            every.get_price(), self.book_type)
            self.cursor.execute(self.sql)
            self.db.commit()

def Spider_run():
    urllist = 'https://book.douban.com/tag/{}?start={}&type=T'
    typelist = ["策划", "科普", '互联网', '编程', '科学', '交互设计', '用户体验', '算法', '科技'] # 
    for t in typelist:
        for j in range(0, 55):
            u = j * 20 
            url = urllist.format(t, u)  
            c = DoubanSpider(url, 'story', t)
            c.writeToDB()
        
if __name__ == "__main__":
    Spider_run()
    

