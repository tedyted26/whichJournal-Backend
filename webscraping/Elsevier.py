from tokenize import String
from bs4 import BeautifulSoup, SoupStrainer
from urllib import request as rq
import Journal

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

    except NameError:
        print(NameError.name)

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
        print("Scrapeando: ", url_temp)
        try:
            req = rq.Request(url_temp, headers = head)
            html = rq.urlopen(req).read()
            only_journal_h2 = SoupStrainer("h2")
            soup = BeautifulSoup(html, 'html.parser', parse_only=only_journal_h2)
        
            for a in soup.findAll("a"):               
                journal_url = a["href"]
                print("Journal_url:", journal_url)
                journal_url_list.append(journal_url)
        except:
            i += 1 # para ver cuantas páginas tienen error
            print("Error ", i)
    #except NameError:
    #    print(NameError.name)
     
    for journal_url in journal_url_list:
        print(journal_url)

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
    except: 
        pass

    if html == "":
        return Journal.Journal(url, "", "", "", "", "", "", "", 
                   "", "", "", "", "", "", "", "", "Elsevier", "")
    
    soup = BeautifulSoup(html, 'html.parser')   
    imagePath = soup.find("a", class_="js-cover-image-link").find("img")["src"]
    title = soup.find("h1").text
    desc = soup.find(class_ = "slide-out").find(class_="spaced").text

    issn_text = soup.find(class_="js-issn").text.split()
    issn = issn_text[2].removesuffix("Print")

    releaseYear = "" # No encuentro info
    type = soup.find(class_ = "js-open-statement-text").text
    
    impactFactor = "" # Por si acaso no sale
    try:
        impactFactor = soup.find(class_ = "js-impact-factor").find(class_="text-l").text
    except:
        pass
    
    quartil = "" # No hay info
    
    otherMetric = ""
    nameOtherMetric = ""
    try:
        metric = soup.find(class_="metric") 
        nameOtherMetrics_aux = metric.find(class_="text-xs").text
        if nameOtherMetrics_aux != "Impact Factor":     
            nameOtherMetric = nameOtherMetrics_aux
            otherMetric = metric.find(class_="text-l").text
    except:
        pass

    price = ""
    try:
        price = soup.find(class_ = "list-price").text.removesuffix("*")
    except:
        pass
    
    acceptanceRate = ""
    try:
        
        acceptanceRate = soup.find()
    except: 
        pass

    timeDecision = ""
    try:
        otherMetrics = soup.find(class_ = 'metrics-row')
        for metric in otherMetrics.findAll(class_="metric"):
            nameMetric = metric.find(class_ = 'text-s').text
            if nameMetric == 'Time to First Decision':
                timeDecision = metric.find(class_ = 'value').text
    except:
        pass

    timePublication = ""
    try:
        otherMetrics = soup.find(class_ = 'metrics-row')
        for metric in otherMetrics.findAll(class_="metric"):
            nameMetric = metric.find(class_ = 'text-s').text
            if nameMetric == 'Publication Time':
                timePublication = metric.find(class_ = 'value').text
    except:
        pass

    timeReview = ""
    try:
        otherMetrics = soup.find(class_ = 'metrics-row')
        for metric in otherMetrics.findAll(class_="metric"):
            nameMetric = metric.find(class_ = 'text-s').text
            if nameMetric == 'Review Time':
                timeReview = metric.find(class_ = 'value').text
    except:
        pass

    otherInfo = ""
    
    return Journal.Journal(url, imagePath, title, desc, issn, releaseYear, type, price, 
                   impactFactor, quartil, otherMetric, nameOtherMetric, acceptanceRate, timeDecision, timePublication, timeReview, "Elsevier", otherInfo)
                


# Get all urls
elsevier_journals_url = getElsevierJournals(getElsevierPages())

# For each journal check if it already exists and if not scrape it
# for journal in elsevier_journals_url:
#    pass

# getElsevierJournalDetails('https://www.sciencedirect.com/journal/international-journal-of-applied-earth-observation-and-geoinformation')



                