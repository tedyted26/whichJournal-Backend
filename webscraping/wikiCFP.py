from tokenize import String
from bs4 import BeautifulSoup, SoupStrainer
from urllib import request as rq
import Conference
import re

import ssl

def getWikiCFPCategories():
    url = "http://www.wikicfp.com/cfp/allcat"
    categories = []
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
        soup = BeautifulSoup(html, 'html.parser')        
        
        table_rows = soup.find("div", class_="contsec").findAll("tr")
        for row in table_rows:
            row_items = row.findAll("td")
            for item in row_items:
                category = item.find("a")
                if category != None:
                    categories.append(category.text)

    except:
        pass
    
    return categories

def getWikiCFPConferences(category):
    url = "http://www.wikicfp.com/cfp/call?conference=" + category.replace(" ", "%20")
    list_links = []
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
        return list_links

    soup = BeautifulSoup(html, 'html.parser')
    pages_table = soup.find("table", attrs={"cellpadding":"2", "cellspacing": "2", "align":"center"})
    pages_text = pages_table.find(attrs={"align":"center"}).text
    pages = int(re.search("in\s*(\d+)\s*pages",pages_text).group(1))

    for i in range(pages):
        if i != 0:
            html =""
            url = url + "&page="+str(i+1)
            try:
                req = rq.Request(url, headers = head)
                html = rq.urlopen(req).read()
            except: 
                pass
        if html == "":
            continue

        td_event = soup.findAll("td", attrs={"rowspan":"2", "align": "left"})
        for event in td_event:       
            link = event.find("a")["href"]
            if list_links.count(link) <= 0:
                list_links.append(link)

    return list_links

def getWikiCFPConferenceDetails(link):
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
    html = ""

    try:
        req = rq.Request(link, headers = head)
        html = rq.urlopen(req).read()
    except: 
        pass

    if html == "":
        return Conference.Conference(link,"","","","","","","","","","","", "WikiCFP")
    
    soup = BeautifulSoup(html, 'html.parser')
    titulo = soup.find("span", attrs={"property": "v:description"}).text
    
    temas = []
    temas_container = None
    try:
        temas_container = soup.find("p", string="Topics of interest include, but are not limited to, the following").find_next_sibling()
        for li in temas_container.findAll("li"):
            li_aux = li.text.split("\r")
            temas.extend(li_aux)
    except:
        pass

    desc = ""
    try: 
        desc = soup.find("p", string="Scope & Topics").find_next_sibling().text
    except:
        pass
    
    if temas_container == None and desc == "":
        desc = soup.find(class_="cfp").text.strip()

    if desc == '[Empty]':
        desc = ""


    fecha = soup.find("th", string="When").find_next_sibling().text.strip()
    ubicacion = soup.find("th", string="Where").find_next_sibling().text
    tipo = ""
    if ubicacion.find("Virtual")!=-1:
        ubicacion = ""
        tipo = "Virtual"
    if ubicacion != "":
        tipo = "In-person"
    fechaEntrega = soup.find("th", string="Submission Deadline").find_next_sibling().text.strip()
    organizacion = ""
    try: 
        organizacion = re.search("(\w+)\s*\d+\s*:",titulo).group(1)
    except:
        pass
    
    tags = []
    try:
        category_table = soup.findAll("table", class_="gglu")[1]
        for a in category_table.findAll("a"):
            tag = a.text.strip().replace("\xa0", "")
            if tag.find("Categories")!=-1:
                continue
            tags.append(a.text.strip().replace("\xa0", ""))
    except:
        pass
    precio = ""

    return Conference.Conference(link,titulo,desc,temas,fecha,ubicacion,fechaEntrega,organizacion,tipo,tags,precio,"WikiCFP")



def getSavedCategories():
    return [
"computer science"
,"applications"
,"testing"
,"artificial intelligence"   
,"philosophy"
,"human computer interaction"
,"engineering"
,"soft computing"
,"e-education"
,"machine learning"
,"information management"
,"society"
,"education"
,"sustainable development"
,"text mining"
,"security"
,"AI"
,"electron devices"
,"software engineering"
,"cultural studies"
,"medical imaging"
,"information technology"
,"mobile"
,"ICT"
,"data mining"
,"network security"
,"theory"
,"communications"
,"materials science"
,"services"
,"big data"
,"chemistry"
,"knowledge representation"
,"robotics"
,"informatics"
,"agents"
,"cloud computing"
,"cyber security"
,"VLSI"
,"management"
,"learning"
,"music"
,"networking"
,"high performance computing"
,"nursing"
,"signal processing"
,"internet"
,"anthropology"
,"image processing"
,"sensor networks"
,"information system"
,"technology"
,"parallel computing"
,"ehealth"
,"NLP"
,"civil engineering"
,"augmented reality"
,"business"
,"agriculture"
,"multi-agent systems"
,"energy"
,"medical"
,"mobility"
,"multimedia"
,"industrial engineering"
,"public health"
,"economics"
,"cloud"
,"computer security"
,"computer vision"
,"teaching"
,"linked data"
,"computing"
,"information"
,"software architecture"
,"control"
,"computer architecture"
,"cancer"
,"humanities"
,"cryptography"
,"development"
,"mechanical engineering"
,"visualization"
,"ethics"
,"automation"
,"culture"
,"safety"
,"bioinformatics"
,"computational linguistics"
,"cardiology"
,"internet of things"
,"innovation"
,"entrepreneurship"
,"social sciences"
,"sociology"
,"fuzzy systems"
,"intelligent systems"
,"programming languages"
,"technologies"
,"environment"
,"neural networks"
,"speech"
,"information systems"
,"social networks"
,"transportation"
,"communication"
,"wireless networks"
,"workshop"
,"electronics"
,"social media"
,"e-health"
,"databases"
,"marketing"
,"ambient intelligence"
,"computational intelligence"
,"politics"
,"graphics"
,"manufacturing"
,"electrical"
,"tourism"
,"wireless"
,"wireless communications"
,"international relations"
,"information retrieval"
,"physics"
,"analytics"
,"IOT"
,"cybersecurity"
,"edge computing"
,"nanotechnology"
,"network"
,"performance"
,"networks"
,"mobile computing"
,"chemical"
,"privacy"
,"language"
,"conferences"
,"healthcare"
,"ubiquitous computing"
,"chemical engineering"
,"materials"
,"virtual reality"
,"recommender systems"
,"literature"
,"electronics engineering"
,"environmental sciences"
,"computer engineering"
,"computer networks"
,"wireless communication"
,"science"
,"arts"
,"5G"
,"e-learning"
,"power engineering"
,"nutrition"
,"electrical engineering"
,"biomedical"
,"digital humanities"
,"simulation"
,"biometrics"
,"photonics"
,"biotechnology"
,"sensors"
,"logistics"
,"renewable energy"
,"e-commerce"
,"GIS"
,"linguistics"
,"mechanical"
,"parallel processing"
,"mechatronics"
,"verification"
,"climate change"
,"computer"
,"knowledge discovery"
,"compilers"
,"social science"
,"pervasive computing"
,"dependability"
,"semantic web"
,"logic"
,"business intelligence"
,"modeling"
,"circuits"
,"social"
,"embedded systems"
,"higher education"
,"digital forensics"
,"data science"
,"health informatics"
,"ecology"
,"pattern recognition"
,"smart cities"
,"film"
,"computer graphics"
,"art"
,"data"
,"natural language processing"
,"modelling"
,"design automation"
,"algorithms"
,"research"
,"social computing"
,"sustainability"
,"statistics"
,"remote sensing"
,"HCI"
,"computational biology"
,"molecular biology"
,"architecture"
,"human-computer interaction"
,"popular culture"
,"software"
,"e-business"
,"environmental"
,"information security"
,"telecommunications"
,"grid computing"
,"finance"
,"neuroscience"
,"programming"
,"health"
,"power electronics"
,"leadership"
,"conference"
,"software testing"
,"pediatrics"
,"psychology"
,"evolutionary computation"
,"ECONOMIC"
,"web"
,"cyber-physical systems"
,"neurology"
,"information science"
,"HPC"
,"operating systems"
,"interdisciplinary"
,"wireless sensor networks"
,"optics"
,"systems"
,"media"
,"collaboration"
,"deep learning"
,"trust"
,"complexity"
,"systems engineering"
,"pedagogy"
,"training"
,"biomedical engineering"
,"games"
,"elearning"
,"history"
,"aerospace"
,"industry"
,"distributed systems"
,"business management"
,"ontologies"
,"biology"
,"cognitive science"
,"multidisciplinary"
,"formal methods"
,"semantics"
,"information theory"
,"design"
,"reliability"
,"trainings"
,"mathematics"
,"ontology"
,"measurement"
,"law"
,"database"
,"oncology"
,"distributed computing"
,"knowledge engineering"
,"security and privacy"
,"blockchain"
,"data analytics"
,"green computing"
,"data management"
,"web services"
,"civil"
,"knowledge management"
,"smart grid"
,"industrial electronics"
,"medicine"
,"life sciences"
,"material science"
,"power"
,"religion"
,"middleware"
,"optimization"
,"political science"
,"applied science"
,"environmental engineering"
,"theoretical computer science"
,"english"
]

# categories = getWikiCFPCategories()
# links = []
# list_conferences = []

# for c in getSavedCategories():
#    print(c)
#    links.extend(getWikiCFPConferences(c))

# for link in links:
#     # comprobar si link existe en la bbdd antes de scrapear de nuevo
#     list_conferences.append(getWikiCFPConferenceDetails("http://www.wikicfp.com/" + link))

# getWikiCFPConferenceDetails("http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=170772&copyownerid=178675")