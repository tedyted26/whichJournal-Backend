from tokenize import String
from bs4 import BeautifulSoup, SoupStrainer
from urllib import request as rq
import Journal
import re

import ssl


def getBMCJournals():
    url = 'https://www.biomedcentral.com/journals-a-z'
    journal_url_list = []
    i = 0

    try:
        html = rq.urlopen(url, context=ssl.SSLContext()).read()
        only_journal_ol = SoupStrainer("ol", attrs={"class": "u-list-reset ctx-journal-list"})
        soup = BeautifulSoup(html, 'html.parser', parse_only=only_journal_ol)

        for li in soup.findAll("li", attrs={"class": "c-list-group__item"}):
            journal_url = li.find("a")["href"].replace("//", "https://")
            journal_url_list.append(journal_url)
                   
    except NameError:
            print(NameError.name)
     
    for journal_url in journal_url_list:
        print(journal_url)

    return journal_url_list



def getBMCJournalDetails(url: str):
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
                   "", "", "", "", "", "", "", "", "BMC", "")
    
    soup = BeautifulSoup(html, 'html.parser')
    imagePath = ""   
    try: 
        imagePath = soup.find("div", class_="cms-item c-image-copyright").find("img")["src"]
    except:
        pass
    title = soup.find(class_="c-journal-header__inner").text.replace("\n", "")
    desc = ""
    issn = soup.find(class_="c-journal-footer__issn").text.split()[1]
    type = "Open Access"

    impactFactor = "" # Por si acaso no sale
    otherMetric = ""
    nameOtherMetric = ""

    timeDecision = ""
    acceptanceRate = ""
    timePublication = ""
    timeReview = ""
    
    metrics = soup.find(class_="c-page-layout__side u-text-sm").findAll(class_="c-separator")
    timeSubmissionToAcceptance = 0
    timeAcceptanceToPublication = 0
    for div in metrics:
        div_header = div.find("h3")
        if div_header != None and div_header.text == "Annual Journal Metrics":
            whole_text = ""
            for p in div.find(class_="cms-article__body").findAll("p"):
                whole_text += p.text.replace("\xa0", " ")

            metric_match = re.findall(r'(\d+\.\d+)\s-\s([\d\-\w\s]*)',whole_text)
            speed_match = re.findall(r'(\d+)\sdays\s(to|from)\s([A-Za-z\s]+)',whole_text)

            if (metric_match == None or metric_match == []) and (metric_match == None or metric_match == []):
                continue

            if metric_match[0][1].startswith("2-year Impact Factor") or metric_match[0][1].startswith("2 year Impact Factor"):
                impactFactor = metric_match[0][0]
            
                otherMetric = metric_match[1][0]
                nameOtherMetric = metric_match[1][1]               
            else:
                otherMetric = metric_match[0][0]
                nameOtherMetric = metric_match[0][1]

            for match in speed_match:
                if match[2].find('first decision for all manuscripts') != -1:
                    weeks = round(int(match[0])/7, 1)
                    timeDecision = str(weeks) + ' weeks'
                elif match[2].find('submission to acceptance') != -1:
                    timeSubmissionToAcceptance = match[0]
                elif match[2].find('acceptance to publication') != -1:
                    timeAcceptanceToPublication = match[0]
    if timeSubmissionToAcceptance != 0 and timeAcceptanceToPublication != 0:
        weeks = round((int(timeSubmissionToAcceptance) + int(timeAcceptanceToPublication))/7, 1)
        timePublication = str(weeks) + ' weeks' 
    
    quartil = "" # No hay info

    price = ""

    otherInfo = []
    html_about = ""

    try:
        req_about = rq.Request(url + "about", headers = head)
        html_about = rq.urlopen (req_about).read()
    except:
        pass
    
    if html_about != "":
        price_soup = BeautifulSoup(html_about, 'html.parser')
        main_section = price_soup.find(class_="c-page-layout__main")
        for div in main_section.findAll("div", attrs={"class": "cms-item"}):
            if div.find("h2").text == "Aims and scope":
                desc = price_soup.find(class_ = "placeholder-aimsAndScope_content").text.replace("\n", "")
                continue

            if div.find("h2").text == "Article-processing charges":
                price_section = div.find(class_="cms-article__body")
                try:
                    price = re.search("\$\d+\.?\d+",price_section.text).group()
                except:
                    pass
                continue
            
            if div.find("h2").text == "Indexing services":
                indexing = div.find("ul")
                for li in indexing.findAll("li"):
                    otherInfo.append(li.text.strip())
                continue
 
    
    return Journal.Journal(url, imagePath, title, desc, issn, type, price, 
                   impactFactor, quartil, otherMetric, nameOtherMetric, acceptanceRate, timeDecision, timePublication, timeReview, "BMC", otherInfo)
                


# list_journals = getBMCJournals()
# i = 0
# for journal in list_journals:
#     print("Empezando journal " + str(i+1)+ " de "+ str(len(list_journals)))
#     print(journal)
#     j = getBMCJournalDetails(journal)
#     print(j.title)
#     i = i+1

# getBMCJournalDetails("https://aepi.biomedcentral.com/")