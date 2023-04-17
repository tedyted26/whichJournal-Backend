from tokenize import String
from bs4 import BeautifulSoup, SoupStrainer
from urllib import request as rq
import Journal
import re

import ssl


def getMDPIJournals():
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
    url="https://www.mdpi.com/about/journals"
    journal_url_list = []
    html = ""

    try:
        req = rq.Request(url, headers = head)
        html = rq.urlopen(req).read()
    except:
        pass
    
    if (html != ""):
        only_journal_tr = SoupStrainer("tr")
        soup = BeautifulSoup(html, 'html.parser', parse_only=only_journal_tr)
        
        for a in soup.findAll("a", attrs={"class": "lean"}):
            journal_url = a["href"]
            journal_url_list.append("https://www.mdpi.com"+journal_url)

    return journal_url_list



def getMDPIJournalDetails(url: str):
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
        return Journal.Journal(url, "", "", "", "", "", "", "", 
                   "", "", "", "", "", "", "", "", "MDPI", "", [], [], "")
    
    soup = BeautifulSoup(html, 'html.parser')   
    
    imagePath = soup.find("div", attrs = {"id":"js-main-top-container"}).find("img")["src"]

    journal_desc_div = soup.find("div", class_="journal__description")
    title = journal_desc_div.find("h1").text.strip()
    desc = journal_desc_div.find(class_ = "journal__description__content").text.replace("\n", "").replace("\xa0", "")

    issn = ""
    possible_issn = journal_desc_div.find("a", class_="oa-link").find_next_siblings()
    for i in possible_issn:
        text = i.text.strip()
        if text.startswith("ISSN: "):
            issn = text.removeprefix("ISSN: ")

    type = "Open Access"
    
    quartil = "" # No hay info
    
    impactFactor = ""
    otherMetric = ""
    nameOtherMetric = ""
    
    metric_divs = soup.findAll(class_="header-impact-factor")

    if metric_divs != None:
        try:
            cs_div = metric_divs[0].find(class_ = "iflogo2")
            if cs_div != None:
                otherMetric = cs_div.find_next_sibling().text
                nameOtherMetric = "Citescore"
        except:
            pass
        try:
            if_div = metric_divs[1].find(class_ = "iflogo2")
            if if_div != None:
                impactFactor = if_div.find_next_sibling().text          
        except:
            pass

    acceptanceRate = ""
    timeDecision = ""
    timePublication = ""
    timeReview = ""

    rapid_publication_container = soup.find("div", class_="journal__description__content")
    if rapid_publication_container != None:
        rapid_publication_list = rapid_publication_container.find("ul")
        if rapid_publication_list != None:
            rapid_publication = rapid_publication_list.findAll("li")
            try:
                for li in rapid_publication:
                    if li.text.startswith("Rapid"):
                        timeDecision = re.search("first\s+decision[\w\s]+\s(\d+\.\d+\sdays)",li.text).group(1)
                        timePublication = re.search("acceptance\s+to\s+publication[\w\s]+\s(\d+\.\d+\sdays)",li.text).group(1)
            except:
                pass

    price = ""
    otherInfo = []
    
    html_precio = ""
    url_precio = url+"/apc"
    try:
        req_precio = rq.Request(url_precio, headers = head)
        html_precio = rq.urlopen(req_precio).read()
    except: 
        pass

    if html != "":
        soup_precio = BeautifulSoup(html_precio, 'html.parser')  
        content = soup_precio.find("div", class_="middle-column__main ul-spaced").text
        price_re = re.search("\(APC\)\sof\s(\d+\s\w+)",content)
        if price_re != None:
            price = price_re.group(1).replace("\xa0", "")

    html_index = ""
    url_index = url+"/indexing"

    try:
        req_index = rq.Request(url_index, headers = head)
        html_index = rq.urlopen(req_index).read()
    except: 
        pass

    if html_index != "":
        soup_index = BeautifulSoup(html_index, 'html.parser')  
        content = soup_index.find("h2", string="Indexing & Abstracting Services").find_next_sibling()
        for li in content.findAll("li"):
            otherInfo.append(li.text.strip())


    return Journal.Journal(url, imagePath, title, desc, issn, type, price, 
                   impactFactor, quartil, otherMetric, nameOtherMetric, acceptanceRate, timeDecision, timePublication, timeReview, "MDPI", otherInfo, [], [], "")
                


# Get all urls
# wiley_journals_url = getMDPIJournals()
# i = 0
# # For each journal check if it already exists and if not scrape it
# for journal in wiley_journals_url:
#     print(journal)
#     print(getMDPIJournalDetails(journal).price)
#     i +=1
#     pass

getMDPIJournalDetails("https://www.mdpi.com/journal/blsf")



                