from tokenize import String
from bs4 import BeautifulSoup, SoupStrainer
from urllib import request as rq

def insertSJRInformation(issn: str):
    html = ""
    head = {
  'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
  'Accept-Encoding': 'none',
  'Accept-Language': 'en-US,en;q=0.8',
  'Connection': 'keep-alive',
  'refere': 'https://example.com',
  'cookie': """your cookie value ( you can get that from your web page) """
    }

    base_url = 'https://www.scimagojr.com/journalsearch.php?q='
    issn = issn.replace("-", "")
    url = base_url + issn
    
    try:
        req = rq.Request(url, headers = head)
        html = rq.urlopen(req).read()
    except: 
        pass

    if html == "":
        return
    
    only_results = SoupStrainer("div", attrs={"class": "search_results"})
    soup = BeautifulSoup(html, 'html.parser', parse_only=only_results)   
    url_journal = "https://www.scimagojr.com/" + soup.find("a")["href"]

    if url_journal == None:
        return
    
    html_journal = ""

    try:
        req_journal = rq.Request(url_journal, headers = head)
        html_journal = rq.urlopen(req_journal).read()
    except: 
        pass

    if html_journal == "":
        return
    
    only_categories = SoupStrainer("div", attrs={"class": "cell1x1 dynamiccell"}) # FIXME change class
    soup = BeautifulSoup(html_journal, 'html.parser', parse_only=only_categories) 

    #TODO
    #get sjr_ranking from same page
    only_ranking = SoupStrainer("div", attrs={"class": "cell1x1 dynamiccell"}) # FIXME change class
    soup = BeautifulSoup(html_journal, 'html.parser', parse_only=only_ranking)

    #TODO
    #use selenium to get quartils

    #TODO 
    #INSERT into db

    print(soup)
    

    
insertSJRInformation('2287-1160')
