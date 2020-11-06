import re
import requests
import json
import nltk
from urllib import request
from bs4 import BeautifulSoup
from lxml import etree
from io import StringIO
from newspaper import Article

with open('config.json', 'r') as file:
    config = json.load(file)
data_path = config['paths']['data']

def cna_helper(article_num, url, article_total):
    try:
        article_name = "article_{:04d}".format(article_num)
        print(">>> Processing: {}/{}".format(article_num, article_total), end='\r')
    
        article = Article(url, "english")
        article.download()
        
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(article.html), parser).getroot()
        result = ''
        
        for div in tree.iter('div'):
            if 'class' in div.attrib and 'c-rte--article' in div.attrib['class']:
                for p in div.iter('p'):
                    result += etree.tostring(p, method="html").decode("utf-8")
                break
        
        article.html = result 
        article.parse()

        body = article.text
        words = body.split()
        text = ' '.join(words)
    
    except:
        print(">>> Broken link, skipping URL {}".format(article_num))
        return
    
    out_dir = data_path+config['scraping']['folder']
    filename = "{}{}.txt".format(out_dir, article_name)
    
    with open(filename, 'w') as f:
        f.write(text)

def scrape_cna():
    url = 'https://kkwfbq38xf-dsn.algolia.net/1/indexes/cna-EZrqV5Hx/query?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser&x-algolia-application-id=KKWFBQ38XF&x-algolia-api-key=504d2f0996dac6611337bfcde2392960'

    data = {
            "query": "crime",
            "hitsPerPage": config['scraping']['num_articles'],
            "attributesToRetrieve": ["id",
                                    "title",
                                    "categories",
                                    "abstractText",
                                    "description",
                                    "url",
                                    ],
            "page": "0",
            "facets": ["type"],
            "filters": "longDates.validFrom <= 1602578054335 AND longDates.validTo >= 1602578054335"
            }

    data = json.dumps(data)
    response = requests.post(url, data=data)
    
    json_file = data_path+'cna_data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)

    with open(json_file) as f:
        data = json.load(f)

    titles = []
    urls = []

    for i in data['hits']:
        if '/singapore/' in i['url']:
            titles.append(i['title'])
            urls.append(i['url'])

    titles_file = data_path+'cna_titles.txt'
    with open(titles_file, 'w') as f:
        for title in titles:
            f.write(title+'\n')

    urls_file = data_path+'cna_urls.txt'
    with open(urls_file, 'w') as f:
        for url in urls:
            f.write(url+'\n')

    article_total = len(urls)
    article_num = 1

    for url in urls:
        cna_helper(article_num, url, article_total)
        article_num += 1    

    print("\n>>> Completed: {}/{}".format(article_num-1, article_total))

def st_helper(article_num, url, article_total):
    try:
        article_name = "article_{:04d}".format(article_num)
        print(">>> Processing: {}/{}".format(article_num, article_total), end='\r')
    
        article = Article(url, "english")
        article.download()
        
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(article.html), parser).getroot()
        result = ''
        
        for div in tree.iter('div'):
            if 'class' in div.attrib and 'odd field-item' in div.attrib['class']:
                for p in div.iter('p'):
                    result += etree.tostring(p, method="html").decode("utf-8")
                break
        
        article.html = result 
        article.parse()

        body = article.text
        words = body.split()
        text = ' '.join(words)
    
    except:
        print(">>> Broken link, skipping URL {}".format(article_num))
        return
    
    out_dir = data_path+config['scraping']['folder']
    filename = "{}{}.txt".format(out_dir, article_name)
    
    with open(filename, 'w') as f:
        f.write(text)

def scrape_st():
    main_url = 'https://www.straitstimes.com/singapore/courts-crime?page='
    num_pages = config['scraping']['num_pages']
    
    titles_path = data_path+'st_titles.txt'
    titles_file = open(titles_path, 'w')
    urls_path = data_path+'st_urls.txt'
    url_file = open(urls_path, 'w')
    
    titles = []
    urls = []
    
    for i in range(num_pages):
        try:
            print(">>> Processing page {}/{}".format(i, num_pages), end='\r')
            url = main_url+str(i)
            html = request.urlopen(url).read().decode("utf8")
            soup = BeautifulSoup(html, "html.parser")

            st = 'https://www.straitstimes.com'
            hrefs = str(soup.find_all('span', class_='story-headline'))

            titles_per_page = re.findall('>(.*?)</a>', hrefs)
            urls_per_page = re.findall('href=\"(.*?)\"', hrefs)
            urls_per_page = [st+url for url in urls_per_page if urls_per_page and 'javascript' not in url]
            urls_per_page = [url for url in urls_per_page if 'multimedia/' not in url]

            for title, url in zip(titles_per_page, urls_per_page):
                titles.append(title)
                urls.append(url)
        except:
            print(">>> Reached end of search results")
            break
    
    print('')
    for title, url in zip(titles, urls):
        titles_file.write(title+'\n')
        url_file.write(url+'\n')

    article_total = len(urls)
    article_num = 1

    for url in urls:
        st_helper(article_num, url, article_total)
        article_num += 1    

    print("\n>>> Completed: {}/{}".format(article_num-1, article_total))

def today_helper(article_num, body, article_total):
    try:
        article_name = "article_{:04d}".format(article_num)
        print(">>> Processing: {}/{}".format(article_num, article_total), end='\r')
        
        parser = etree.HTMLParser()
        tree = etree.parse(StringIO(body), parser).getroot()
        result = ''
        
        for p in tree.iter('p'):
            result += etree.tostring(p, method="html").decode("utf-8")
        
        article = Article(body)
        article.download()
        article.html = result
        article.parse()
        
        body = article.text
        words = body.split()
        text = ' '.join(words)
    
    except:
        print(">>> Broken link, skipping URL {}".format(article_num))
        return
    
    out_dir = data_path+config['scraping']['folder']
    filename = "{}{}.txt".format(out_dir, article_name)

    with open(filename, 'w') as f:
        f.write(text)

def scrape_today():
    url = 'https://www.todayonline.com/api/v3/news_feed/119811?&items='
    num_articles = config['scraping']['num_articles']
    response = requests.get(url+str(num_articles))

    json_file = data_path+'today_data.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(response.json(), f, ensure_ascii=False, indent=4)
        
    with open(json_file) as json_file:
        data = json.load(json_file)
        
    titles = []
    urls = []
    
    for i in data['nodes']:
        titles.append(i['node']['title'])
        urls.append(i['node']['node_url'])
    
    article_total = len(data['nodes'])
    article_num = 1
    
    for i in data['nodes']:
        body = i['node']['body']
        today_helper(article_num, body, article_total)
        article_num += 1

    print("\n>>> Completed: {}/{}".format(article_num-1, article_total))
    
    titles_file = data_path+'today_titles.txt'
    with open(titles_file, 'w') as f:
        for title in titles:
            f.write(title+'\n')

    urls_file = data_path+'today_urls.txt'
    with open(urls_file, 'w') as f:
        for url in urls:
            f.write(url+'\n')

def url_scraper():
    file = data_path+config['scraping']['urls']
    urls = open(file).read().split()
    site = config['scraping']['site']
    
    article_total = len(urls)
    article_num = 1

    for url in urls:
        try:
            if site == 'cna': cna_helper(article_num, url, article_total)
            elif site == 'st': st_helper(article_num, url, article_total)
            elif site == 'today': raise NotImplementedError('Function not implemented')
            
            article_num += 1
        
        except NotImplementedError as e:
            print(">>> {}".format(e))
            return

    print("\n>>> Completed: {}/{}".format(article_num-1, len(urls)))

if __name__ == '__main__':
    if not nltk.data.find('tokenizers/punkt'):
        nltk.download('punkt')
    
    if config['scraping']['run_all']:
        scrape_cna()
        scrape_st()
        scrape_today()
    
    else:
        mode = config['scraping']['mode']
        
        if mode == 'cna': scrape_cna()
        elif mode == 'st': scrape_st()
        elif mode == 'today': scrape_today()
        elif mode == 'txt': url_scraper()

