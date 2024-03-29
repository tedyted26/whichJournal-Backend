from tokenize import String
from bs4 import BeautifulSoup, SoupStrainer
from urllib import request as rq
import Journal

import re

import ssl


def getSpringerJournals():
    base_url = 'https://link.springer.com/journals/'
    journal_url_list = []
    i = 0

    for letter in ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','#'):      
        for page in range(0, 10): # por si acaso
            url = base_url + letter + '/' + str(page+1)
            try:
                html = rq.urlopen(url, context=ssl.SSLContext()).read()
        
                only_journal_li = SoupStrainer("li", attrs={"class": "c-atoz-list__item"})
                soup = BeautifulSoup(html, 'html.parser', parse_only=only_journal_li)
        
                for a in soup.findAll("a"):
                    journal_url = a["href"]
                    journal_url_list.append(journal_url)
            
            except:
                break

    return journal_url_list



def getSpringerJournalDetails(url: str):
    html = ""
    head = {
  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
  'Accept-Encoding': 'none',
  'Accept-Language': 'en-US,en;q=0.8',
  'Connection': 'keep-alive',
  'refere': 'https://example.com',
  'cookie': """your cookie value ( you can get that from your web page) """
    }

    try:
        req = rq.Request(url, headers = head)
        html = rq.urlopen(req).read()
    except: 
        pass

    if html == "":
        return Journal.Journal(url, "", "", "", "", "", "", 
                   "", "", "", "", "", "", "", "", "Springer", "", [], [], "")
    
    soup = BeautifulSoup(html, 'html.parser')

    imagePath = ""
    img_div = soup.find("div", class_="c-product-header__cover")
    if img_div == None:
        img_div = soup.find("img", attrs={"id", "coverImage"})
    
    try:
        imagePath = img_div.find("img")["src"]
    except:
        pass

    title = ""
    title_h1 = soup.find("h1", class_="c-product-header__title")
    if title_h1 == None:
        title_h1 = soup.find("h1", class_="c-journal-header__title")
        
    try:
        title = title_h1.text.replace("\n", "")
    except:
        pass
    
    issn = ""
    type = ""
    description_items = soup.findAll(class_="c-list-description__item")
    for item in description_items:
        item_name = item.find(class_="c-list-description__term").text.replace("\n", "")
        if item_name.find("ISSN") != -1:
            issn = item.find(class_="c-list-description__details").text.replace("\n", "").replace(" ", "")
        if item_name == "Publishing model":
            type = item.find(class_="c-list-description__details").text.replace("How to publish with us, including Open Access", "").replace("How to publish with us", "").replace("\n", "").replace(".", "").lstrip().rstrip()
    
    journal_metrics = soup.findAll(class_ = "app-journal-metrics__details")
    impactFactor = ""
    otherMetric = ""
    nameOtherMetric = ""
    timeDecision = ""
    for metric in journal_metrics:
        if metric["data-test"] == "metrics-speed-value":
            timeDecision = metric.text
        if metric["data-test"] == "impact-factor-value":
            try:
                impactFactor = float(metric.text.split()[0])
            except:
                pass
        if metric["data-test"] == "five-year-impact-factor-value":
            try:
                otherMetric = float(metric.text.split()[0])
                nameOtherMetric = "Five year impact factor"
            except:
                pass

    price = ""
    desc = ""

    try:
        req_about = rq.Request(url + "/about", headers = head)
        html_about = rq.urlopen(req_about).read()
    except: 
        pass

    if html_about != None:
        soup_about =  BeautifulSoup(html_about, 'html.parser')
        desc_div = soup_about.find("div", attrs={"id": "aimsAndScope"})
        if desc_div != None:
            desc = desc_div.find("p").text.replace("\n", "")
        price_div = soup_about.find("div", attrs={"id": "article-processing+charges"})
        if price_div != None:
            try:
                price = re.search("\$\d+\.?\d+",price_div.text).group()
            except:
                pass

    quartil = "" # No hay info
    acceptanceRate = ""
    timePublication = ""
    timeReview = ""
    indexing = []

    try:
        indexing_list = soup.find("h2", class_="app-section__heading", string="About this journal").find_next_sibling()
        for li in indexing_list.findAll("li", class_="c-list-columned__item"):
            indexing.append(li.text.strip())
    except:
        pass
    
    
    return Journal.Journal(url, imagePath, title, desc, issn, type, price, 
                   impactFactor, quartil, otherMetric, nameOtherMetric, acceptanceRate, timeDecision, timePublication, timeReview, "Springer", indexing, [], [], "")
                


# list_journals = getSpringerJournals()
# i = 0
# for journal in list_journals:
#     print("Empezando journal " + str(i+1)+ " de "+ str(len(list_journals)))
#     print(getSpringerJournalDetails(journal).title)
#     i = i+1

# getSpringerJournalDetails("https://link.springer.com/journal/41120")           