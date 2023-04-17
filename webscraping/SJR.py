from tokenize import String
from bs4 import BeautifulSoup, SoupStrainer
from urllib import request as rq
import mysql.connector

def updateJournalInformation(mydb, limit): 
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id, issn FROM journals ORDER BY id DESC LIMIT "+str(limit))
    new_data = mycursor.fetchall()

    for row in new_data:
        id = row[0]
        issn = row[1]
        insertSJRInformation(mydb, id, issn)
    
    


def insertSJRInformation(mydb, journal_id, issn: str):
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
    subject_areas = []
    subject_categories = {}
    quartil_per_category = {}
    sjr_ranking = 0
    
    try:
        req = rq.Request(url, headers = head)
        html = rq.urlopen(req).read()
    except: 
        pass

    if html == "":
        return
    
    only_results = SoupStrainer("div", attrs={"class": "search_results"})
    soup = BeautifulSoup(html, 'html.parser', parse_only=only_results)  
    a = soup.find("a")

    if a == None:
        return
    
    url_journal = "https://www.scimagojr.com/" + a["href"]
    
    html_journal = ""

    try:
        req_journal = rq.Request(url_journal, headers = head)
        html_journal = rq.urlopen(req_journal).read()
    except: 
        pass

    if html_journal == "":
        return
    
    # get categories
    only_categories = SoupStrainer("div", attrs={"class": "journalgrid"})
    soup = BeautifulSoup(html_journal, 'html.parser', parse_only=only_categories) 

    category_div = soup.findAll("div")[2]

    subject_area_ul = category_div.findAll("ul", attrs={"style": "padding-left:0px"})

    for ul in subject_area_ul:
        area = ul.find("a").text.strip()
        subject_areas.append(area)
        subject_categories_ul = ul.find("ul", class_="treecategory")
        if subject_categories_ul != None:
            for c_ul in subject_categories_ul:
                subject_categories[c_ul.find("a").text.strip()] = area
        
    
    #get quartils
    only_ranking = SoupStrainer("div", attrs={"class": "dashboard"})
    soup = BeautifulSoup(html_journal, 'html.parser', parse_only=only_ranking)

    q_div = soup.find("div", class_="cell100x1 dynamiccell")
    q_table = q_div.find("table").find("tbody")
    q_rows = q_table.findAll("tr")
    q_row_length = len(q_rows)
    categories_len = len(subject_categories)
    for i in range(categories_len):
        row = q_rows[(i+1)*int(q_row_length/categories_len)-1]
        row_elements = row.findAll("td")
        quartil_per_category[row_elements[0].text.strip()] = row_elements[2].text.strip()

    #get sjr_ranking from same page
    sjr_div = soup.find("div", class_="cell1x1 dynamiccell")
    sjr_table = sjr_div.find("table").find("tbody")
    sjr_rows = sjr_table.findAll("tr")[-1]
    sjr_ranking = sjr_rows.findAll("td")[1].text.strip()

    #INSERT into db
    
    mycursor = mydb.cursor()

    for i in subject_areas:
        mycursor.execute("INSERT IGNORE into sjr_subject_areas "
                    "(area) VALUES ('" + str(i) + "')" )   
        mydb.commit()

    for key in subject_categories:
        area = subject_categories[key]
        mycursor.execute("SELECT id FROM sjr_subject_areas "
                    "WHERE area = '" + area + "'" )
        id = mycursor.fetchall()[0][0]
        mycursor.execute("INSERT IGNORE into sjr_subject_categories "
                        "(category, area_id) VALUES ('" + key + "'," + str(id) + ")")   
        mydb.commit()

    add_info = ("UPDATE journals "
               "SET sjr_subject_areas = %s, sjr_subject_categories = %s," 
               "quartil_per_category = %s, sjr_ranking = %s "
               "WHERE id = " + str(journal_id))

    mycursor.execute("SELECT * FROM sjr_subject_areas")
    db_areas = mycursor.fetchall()

    subject_areas_ids_insert = "["
    for id, a in db_areas: 
        if a in subject_areas:
            subject_areas_ids_insert += str(id) + ","
    subject_areas_ids_insert = subject_areas_ids_insert.removesuffix(",") + "]"

    mycursor.execute("SELECT id, category FROM sjr_subject_categories")
    db_categories = mycursor.fetchall()

    subject_categories_ids_insert = "["
    quartil_per_id_category = "["
    for id, c in db_categories:
        if c in subject_categories:
            subject_categories_ids_insert += str(id) + ","
            quartil_per_id_category += str(quartil_per_category[c]) + ","
    subject_categories_ids_insert = subject_categories_ids_insert.removesuffix(",") + "]"
    quartil_per_id_category = quartil_per_id_category.removesuffix(",") + "]"

    add_info_text = (subject_areas_ids_insert, subject_categories_ids_insert, quartil_per_id_category, sjr_ranking)
    mycursor.execute(add_info, add_info_text)

    mydb.commit()
    mycursor.close()
  
try:
    mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="whichjournal"
    )
except:
    pass
    
# insertSJRInformation(mydb, 4998, '2287-1160')

# updateJournalInformation(mydb, 20)
