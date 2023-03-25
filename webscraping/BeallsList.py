from tokenize import String
from bs4 import BeautifulSoup, SoupStrainer
from urllib import request as rq

# update 2021
# others 2016
# MDPI has some controversy

def getBeallsPublishers():
    url = "https://beallslist.net/"
    beallsPublishers = {}
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
        return beallsPublishers
    
    soup = BeautifulSoup(html, 'html.parser') 
    list = soup.find("div", class_="wp-block-column").find("ul")
    for li in list.findAll("li"):
        try:
            beallsPublishers[li.text.strip().replace("\xa0", "")] = li.find("a")["href"]
        except:
            pass

    return beallsPublishers
    
def getBeallsPublishersUpdated():
    url = "https://beallslist.net/"
    beallsPublishers = {}
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
        return beallsPublishers
    
    soup = BeautifulSoup(html, 'html.parser') 
    list = soup.find("h2", string="Update").find_next_sibling().find_next_sibling()
    for li in list.findAll("li"):
        a = li.find("a")
        try:
            beallsPublishers[a.text.strip().replace("\xa0", "")] = a["href"]
        except NameError:
            print(NameError)
        
    return beallsPublishers
    

def getBeallsStandaloneJournals():
    url = "https://beallslist.net/standalone-journals/"
    beallsStandaloneJournals = {}
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
        return beallsStandaloneJournals
    
    soup = BeautifulSoup(html, 'html.parser') 
    list = soup.find("div", class_="wp-block-column").find("ul")
    for li in list.findAll("li"):
        try:
            beallsStandaloneJournals[li.text.strip().replace("\xa0", "")] = li.find("a")["href"]
        except:
            pass
        
    return beallsStandaloneJournals

def getBeallsStandaloneJournalsUpdated():
    url = "https://beallslist.net/standalone-journals/"
    beallsStandaloneJournals = {}
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
        return beallsStandaloneJournals
    
    soup = BeautifulSoup(html, 'html.parser') 
    list = soup.find("h2", string="Update").find_next_sibling().find_next_sibling()
    for li in list.findAll("li"):
        a = li.find("a")
        try:
            beallsStandaloneJournals[a.text.strip().replace("\xa0", "")] = a["href"]
        except NameError:
            print(NameError)
        
    return beallsStandaloneJournals

def getBeallsVanityPress():
    url = "https://beallslist.net/vanity-press/"
    beallsVanityPress = {}
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
        return beallsVanityPress
    
    soup = BeautifulSoup(html, 'html.parser') 
    list = soup.find("h2", string="List of vanity press").find_next_sibling().find_next_sibling()
    for li in list.findAll("li"):
        a = li.find("a")
        try:
            beallsVanityPress[a.text.strip().replace("\xa0", "")] = a["href"]
        except NameError:
            print(NameError)
        
    return beallsVanityPress
