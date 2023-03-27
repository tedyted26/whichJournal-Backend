from tokenize import String
from bs4 import BeautifulSoup, SoupStrainer
from urllib import request as rq
import Journal
import re

import ssl


def getElsevierPages():
    url = "https://www.elsevier.com/search-results?query=&labels=journals"
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
    pages = 1
    try:
        req = rq.Request(url, headers = head)
        html = rq.urlopen(req).read()
        only_pagination = SoupStrainer(class_="pagination-status")
        soup = BeautifulSoup(html, 'html.parser', parse_only=only_pagination)        
        pages = soup.text.split()
        pages = int(pages[3])

    except:
        pass

    return pages



def getElsevierJournals(paginas = 1):
    url = "https://www.elsevier.com/search-results?query=&labels=journals&sort=document.titleRaw-asc"
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
    journal_url_list = []
    i = 0

    for p in range(paginas):
        url_temp = url + "&page=" + str(p+1)
        try:
            req = rq.Request(url_temp, headers = head)
            html = rq.urlopen(req).read()
            only_journal_h2 = SoupStrainer("h2")
            soup = BeautifulSoup(html, 'html.parser', parse_only=only_journal_h2)
        
            for a in soup.findAll("a"):               
                journal_url = a["href"]
                journal_url_list.append(journal_url)
        except:
            pass
     
    return journal_url_list



def getElsevierJournalDetails(url: str):
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

    try:
        req = rq.Request(url, headers = head)
        html = rq.urlopen(req).read()
    except NameError: 
        pass

    if html == "":
        return Journal.Journal(url, "", "", "", "", "", "", 
                   "", "", "", "", "", "", "", "", "Elsevier", "")
    
    soup = BeautifulSoup(html, 'html.parser')   
    imagePath = soup.find("a", class_="js-cover-image-link").find("img")["src"]
    title = soup.find("h1").text

    desc = ""
    html_aims = ""
    try:
        req_aims = rq.Request(url.replace("https://www.journals.elsevier.com/", "https://www.sciencedirect.com/journal/") + "/about/aims-and-scope", headers = head)
        html_aims = rq.urlopen(req_aims).read()
    except: 
        pass

    if html_aims != "":
        soup_aims = BeautifulSoup(html_aims, 'html.parser')
        desc_div = soup_aims.find("div", class_="js-aims-and-scope branded text-s")
        if desc_div != None:
            desc = desc_div.text.replace("\n", "")
        soup_aims.clear()

    issn_text = soup.find(class_="js-issn").text
    issn = re.search("ISSN:\s+([\d\-]+)",issn_text).group(1)

    type = ""
    type_container = soup.find(class_ = "js-open-statement-text")
    if type_container != None:
        type = type_container.text
    
    impactFactor = ""
    try:
        impactFactor = float(soup.find(class_ = "js-impact-factor").find(class_="text-l").text)
    except:
        pass
    
    quartil = "" # No hay info
    
    otherMetric = ""
    nameOtherMetric = ""
    try:
        metric = soup.find(class_="metric") 
        nameOtherMetrics_aux = metric.find(class_="text-xs").text
        if nameOtherMetrics_aux != "Impact Factor":                 
            try:
                nameOtherMetric = nameOtherMetrics_aux
                otherMetric = float(metric.find(class_="text-l").text)
            except:
                pass
    except:
        pass

    price = ""
    try:
        price = soup.find(class_ = "list-price u-h2").text.removesuffix("*")
    except:
        pass

    acceptanceRate = ""
    timeDecision = ""
    timePublication = ""
    timeReview = ""
    try:
        metrics = soup.findAll("div", class_="metric u-padding-s-left")
        for metric in metrics:
            nameMetric = metric.find(class_ = 'text-s').text
            if nameMetric == 'Time to First Decision':
                    timeDecision = metric.find(class_ = 'value').text
            if nameMetric == 'Publication Time':
                    timePublication = metric.find(class_ = 'value').text
            if nameMetric == 'Review Time':
                    timeReview = metric.find(class_ = 'value').text
            if nameMetric == 'Acceptance Rate':
                    acceptanceRate = metric.find(class_ = 'value').text
    except:
        pass 

    indexing = []
    html_indexing = ""
    try:
        req_indexing = rq.Request(url.replace("https://www.journals.elsevier.com/", "https://www.sciencedirect.com/journal/") + "/about/abstracting-and-indexing", headers = head)
        html_indexing = rq.urlopen(req_indexing).read()
    except: 
        pass

    if html_indexing != "":
        soup_indexing = BeautifulSoup(html_indexing, 'html.parser')
        indexing_div = soup_indexing.find("div", class_="abstracting-and-indexing branded")
        if indexing_div != None:
            indexing_ul = indexing_div.find("ul")
            if indexing_ul != None:
                for li in indexing_ul.findAll("li"):
                    indexing.append(li.text.replace("\n", ""))
        soup_indexing.clear()
    
    return Journal.Journal(url, imagePath, title, desc, issn, type, price, 
                   impactFactor, quartil, otherMetric, nameOtherMetric, acceptanceRate, timeDecision, timePublication, timeReview, "Elsevier", indexing)
                


# Get all urls
# elsevier_journals_url = getElsevierJournals(getElsevierPages())

# For each journal check if it already exists and if not scrape it
# for journal in elsevier_journals_url:
#    pass

# getElsevierJournalDetails('https://www.journals.elsevier.com/acute-pain')



                