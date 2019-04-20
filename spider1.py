import requests
import bs4
import re

def douban():
    url = 'https://book.douban.com/tag/小说'
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html5lib')
    # 书名的表格
    book_name = []
    # 评分的表格
    score = []
    # 作者的表格
    author = []
    # 翻译者的表格
    translater = []
    # 出版社的表格
    pub = []
    # 出版日期的表格
    pub_data = []
    # 价格的表格
    price = []

    # 提取书名
    n = soup.find_all('div', class_ = 'info')
    for s in n:
        l = s.find('a')['title']
       # print(l)
        book_name.append(l)

    # 提取评分信息
    f = soup.find_all('span', class_ = 'rating_nums')
    for g in f:
        sc = g.get_text()
        # print(sc)
        score.append(sc)

    # 提取出版社信息
    m = soup.find_all('div', class_ = 'pub')
    for i in m:
        mg = i.get_text()
        #print(mg)
        mg1 = mg.strip()
        lgh = mg1.split('/', 4)
        if len(lgh) <= 4 :
            author.append(lgh[0])
            pub.append(lgh[1])
            pub_data.append(lgh[2])
            price.append(lgh[3])
        else:
            author.append(lgh[0])
            pub.append(lgh[2])
            pub_data.append(lgh[3])
            price.append(lgh[4])
            translater.append(lgh[1])

    for h in range(20):
        he = author[h] + book_name[h] + pub[h] + pub_data[h] + 'star' + score[h]
        print(he)



        #print(lhg)
    
  #  c = soup.find_all('span', class_ = 'rating_nums')
   
  # for y in c:
   #     print(y)
        #x = re.match('^">(.*)<$', y)
        #print(x)

if __name__ == "__main__":
    douban()