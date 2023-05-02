from flask import Flask, request, g
from flask_cors import CORS, cross_origin
from processing.recommender import recommender_class
from processing.classifier import classifier_class
from processing.doc_processing import transform_input_file_into_title_abstract
import mysql.connector
import db
import datetime
import logging
import statistics
import ast
import json

# https://flask.palletsprojects.com/en/2.2.x/installation/#install-flask
# https://flask.palletsprojects.com/en/2.2.x/quickstart/
#  venv\Scripts\activate
# https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/
#  python -m flask run 

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'whichjournal'

date = datetime.datetime.now()
logname = str(date.day) + "-" +str(date.month) + "-" + str(date.year) + "__" + date.strftime("%X").replace(":", "-")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("processing/logs/" + logname + '.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

rm = recommender_class(logger)
cs = classifier_class(logger)

@app.route("/")
@cross_origin()
def hello_world():
    return '{"text": "Hello, World!"}'

@app.before_request
def before_request():
    g.db = db.get_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route("/get_results", methods = ['POST'])
def get_results(): 
    data = json.loads(request.form['data'])

    file = None
    if request.files and 'file' in request.files:
        file = request.files['file']       

    title = ""
    abstract = ""
    keywords = ""

    if file==None:

        title = data['title_j']
        abstract = data['abstract']
        keywords = data['keywords']

    else:
        title, abstract, keywords = transform_input_file_into_title_abstract(file)

    
    isJournals = data['check_j']
    isConferences = data['check_c']
    _top = 20
    json_journals = ""
    json_conferences = ""

    if isJournals:
        rm_journals = rm.recommend(title, abstract, keywords, table = "journals", top = _top)
        cs_journals = cs.classify_predators(rm_journals)
        json_journals = get_journals_json(cs_journals)
    if isConferences:
        rm_conferences = rm.recommend(title, abstract, keywords, table = "conferences", top = _top)
        json_conferences = get_conferences_json(rm_conferences)
    
    if isJournals and isConferences and json_journals != "" and json_conferences != "":
        result = json_journals.removesuffix(']') + ',' + json_conferences.removeprefix('[')
    elif isJournals:
        result = json_journals
    elif isConferences:
        result = json_conferences
    else:
        result = ""

    return result

def get_journals_json(journals_dict):
    if journals_dict == None or len(journals_dict) < 1:
        return ""
    
    mycursor = g.db.cursor()

    json = '['
    
    for key in journals_dict:
        mycursor.execute("SELECT * from journals WHERE id=" + str(key))
        journal_info = mycursor.fetchall()[0]

        json += '{"url" : "'+journal_info[1]+'",'
        json += '"imagePath" : "'+journal_info[2]+'",'
        json += '"title" : "'+journal_info[3]+'",'
        json += '"issn" : "'+journal_info[5]+'",'
        json += '"type" : "'+journal_info[6]+'",'
        json += '"price" : "'+journal_info[7]+'",'
        json += '"impactFactor" : "'+str(journal_info[8])+'",'   
        json += '"otherMetric" : "'+str(journal_info[9])+'",'
        json += '"nameOtherMetric" : "'+journal_info[10]+'",'
        json += '"acceptanceRate" : "'+journal_info[11]+'",'
        json += '"timeDecision" : "'+journal_info[12]+'",'
        json += '"timePublication" : "'+journal_info[13]+'",'
        json += '"timeReview" : "'+journal_info[14]+'",'

        categories_array = journal_info[18]
        quartil_array = journal_info[19]
        quartil = ""
        category = ""

        if quartil_array != None or quartil_array != "":
            # if info matches, then get first quartil and first category
            if categories_array != None and categories_array != "" and len(quartil_array) == len(categories_array):
                quartil = quartil_array[0]
                category = categories_array[0]
            # if not, get an average
            else:
                values = []
                for q in quartil:
                    if q != "":
                        values.append(int(q.removeprefix("Q")))
                if values != []:
                    quartil = "Q" + str(statistics.mode(values))
                    category = "most frequently"
        if quartil != "":
            quartil_string = quartil + "(" + category + ")" 
        else: 
            quartil_string = ""       
        json += '"quartil" : "'+quartil_string+'",'
        ranking = str(journal_info[20])
        if ranking == "None":
            ranking = ""
        json += '"sjr_ranking":"'+ranking+'",'
        json += '"predator" : "'+journals_dict[key][1]+'"},'

    json = json.removesuffix(",")
    json += ']'

    mycursor.close()
    return json

def get_conferences_json(conferences_dict):
    if conferences_dict == None or len(conferences_dict) < 1:
        return ""
    
    mycursor = g.db.cursor()

    json = '['
    for key in conferences_dict:
        mycursor.execute("SELECT * from conferences WHERE id=" + str(key))
        conference_info = mycursor.fetchall()[0]

        json += '{"url" : "'+conference_info[1]+'",'
        json += '"title" : "'+conference_info[2]+'",'
        json += '"date" : "'+conference_info[5]+'",'
        json += '"location" : "'+conference_info[6]+'",'
        json += '"dueDate" : "'+conference_info[7]+'",'
        json += '"organization" : "'+conference_info[8]+'",'
        json += '"type" : "'+conference_info[9]+'",'

        tags =  ast.literal_eval(conference_info[10])

        if len(tags) >= 5:
            tags = tags[:5]

        json += '"tags" : '+str(tags).replace('"','').replace("'", '"').replace(",",", ")+'},'

    json = json.removesuffix(",")
    json += ']'

    mycursor.close()
    return json

@app.route("/get_test", methods = ['POST'])
def get_test():
    
    #json = '[{"url" : "https://link.springer.com/journal/468","imagePath" : "https://media.springernature.com/w92/springer-static/cover/journal/468.jpg","title" : "Trees","issn" : "0931-1890","type" : "Hybrid (Transformative Journal)","price" : "","impactFactor" : "2.888","otherMetric" : "2.798","nameOtherMetric" : "Five year impact factor","acceptanceRate" : "","timeDecision" : "52 days","timePublication" : "","timeReview" : "","quartil" : "()","sjr_ranking":"0.658","predator" : "NO"},{"url" : "https://link.springer.com/journal/11295","imagePath" : "https://media.springernature.com/w92/springer-static/cover/journal/11295.jpg","title" : "Tree Genetics & Genomes","issn" : "1614-2950","type" : "Hybrid (Transformative Journal)","price" : "","impactFactor" : "2.398","otherMetric" : "2.625","nameOtherMetric" : "Five year impact factor","acceptanceRate" : "","timeDecision" : "11 days","timePublication" : "","timeReview" : "","quartil" : "()","sjr_ranking":"0.604","predator" : "NO"},{"url" : "https://link.springer.com/journal/114","imagePath" : "https://media.springernature.com/w92/springer-static/cover/journal/114.jpg","title" : "The Science of Nature","issn" : "0028-1042","type" : "Hybrid (Transformative Journal)","price" : "","impactFactor" : "2.427","otherMetric" : "2.645","nameOtherMetric" : "Five year impact factor","acceptanceRate" : "","timeDecision" : "14 days","timePublication" : "","timeReview" : "","quartil" : "()","sjr_ranking":"0.735","predator" : "NO"},{"url" : "https://link.springer.com/journal/12110","imagePath" : "https://media.springernature.com/w92/springer-static/cover/journal/12110.jpg","title" : "Human Nature","issn" : "1045-6767","type" : "Hybrid (Transformative Journal)","price" : "","impactFactor" : "2.75","otherMetric" : "3.684","nameOtherMetric" : "Five year impact factor","acceptanceRate" : "","timeDecision" : "33 days","timePublication" : "","timeReview" : "","quartil" : "()","sjr_ranking":"0.741","predator" : "NO"},{"url" : "https://annforsci.biomedcentral.com","imagePath" : "//media.springernature.com/lw960/springer-cms/rest/v1/content/20257884/data/v2","title" : "Annals of Forest Science","issn" : "1297-966X","type" : "Open Access","price" : "$2190.00","impactFactor" : "3.775","otherMetric" : "4.055","nameOtherMetric" : "5-year Impact Factor ","acceptanceRate" : "","timeDecision" : "","timePublication" : "","timeReview" : "","quartil" : "()","sjr_ranking":"0.802","predator" : "NO"},{"url" : "https://www.mdpi.com/journal/jzbg","imagePath" : "https://pub.mdpi-res.com/img/journals/jzbg-logo.png?8600e93ff98dbf14","title" : "Journal of Zoological and Botanical Gardens","issn" : "2673-5636","type" : "Open Access","price" : "1000CHF","impactFactor" : "0.0","otherMetric" : "0.0","nameOtherMetric" : "","acceptanceRate" : "","timeDecision" : "20.1 days","timePublication" : "4.6 days","timeReview" : "","quartil" : "()","sjr_ranking":"None","predator" : "MDPI"},{"url" : "https://ethnobiomed.biomedcentral.com","imagePath" : "//media.springernature.com/lw450/springer-cms/rest/v1/content/17966792/data/v3","title" : "Journal of Ethnobiology and Ethnomedicine","issn" : "1746-4269","type" : "Open Access","price" : "$3090.00","impactFactor" : "3.404","otherMetric" : "4.044","nameOtherMetric" : "5-year Impact Factor ","acceptanceRate" : "","timeDecision" : "1.7 weeks","timePublication" : "","timeReview" : "","quartil" : "()","sjr_ranking":"0.644","predator" : "NO"},{"url" : "https://www.journals.elsevier.com/applied-and-computational-harmonic-analysis","imagePath" : "https://ars.els-cdn.com/content/image/X10635203.jpg","title" : "Applied and Computational Harmonic Analysis","issn" : "1063-5203","type" : "Supports open access","price" : "","impactFactor" : "2.974","otherMetric" : "5.7","nameOtherMetric" : "CiteScore","acceptanceRate" : "","timeDecision" : "","timePublication" : "1.3 weeks","timeReview" : "","quartil" : "()","sjr_ranking":"1.301","predator" : "NO"},{"url" : "https://www.mdpi.com/journal/resources","imagePath" : "https://pub.mdpi-res.com/img/journals/resources-logo.png?8600e93ff98dbf14","title" : "Resources","issn" : "2079-9276","type" : "Open Access","price" : "1600CHF","impactFactor" : "0.0","otherMetric" : "6.4","nameOtherMetric" : "Citescore","acceptanceRate" : "","timeDecision" : "19.3 days","timePublication" : "4.7 days","timeReview" : "","quartil" : "()","sjr_ranking":"0.742","predator" : "MDPI"},{"url" : "https://bmcmusculoskeletdisord.biomedcentral.com","imagePath" : "//media.springernature.com/lw450/springer-cms/rest/v1/content/23223628/data/v3","title" : "BMC Musculoskeletal Disorders","issn" : "1471-2474","type" : "Open Access","price" : "$2790.00","impactFactor" : "2.562","otherMetric" : "3.021","nameOtherMetric" : "5-year Impact Factor ","acceptanceRate" : "","timeDecision" : "6.6 weeks","timePublication" : "","timeReview" : "","quartil" : "()","sjr_ranking":"0.669","predator" : "NO"},{"url" : "https://www.journals.elsevier.com/biosystems-engineering","imagePath" : "https://ars.els-cdn.com/content/image/X15375110.jpg","title" : "Biosystems Engineering","issn" : "1537-5110","type" : "Supports open access","price" : "","impactFactor" : "5.002","otherMetric" : "8.7","nameOtherMetric" : "CiteScore","acceptanceRate" : "13%","timeDecision" : "","timePublication" : "","timeReview" : "7.6 weeks","quartil" : "()","sjr_ranking":"1.017","predator" : "NO"},{"url" : "https://www.journals.elsevier.com/applied-mathematics-and-computation","imagePath" : "https://ars.els-cdn.com/content/image/X00963003.jpg","title" : "Applied Mathematics and Computation","issn" : "0096-3003","type" : "Supports open access","price" : "","impactFactor" : "4.397","otherMetric" : "7.6","nameOtherMetric" : "CiteScore","acceptanceRate" : "","timeDecision" : "3.7 weeks","timePublication" : "2.3 weeks","timeReview" : "5.1 weeks","quartil" : "()","sjr_ranking":"1.038","predator" : "NO"},{"url" : "https://www.journals.elsevier.com/archives-of-rehabilitation-research-and-clinical-translation","imagePath" : "https://ars.els-cdn.com/content/image/X25901095.jpg","title" : "Archives of Rehabilitation Research and Clinical Translation","issn" : "2590-1095","type" : "Open access","price" : "$2500","impactFactor" : "4.06","otherMetric" : "0.0","nameOtherMetric" : "","acceptanceRate" : "","timeDecision" : "","timePublication" : "2.2 weeks","timeReview" : "","quartil" : "()","sjr_ranking":"None","predator" : "NO"},{"url" : "https://www.journals.elsevier.com/applied-geography","imagePath" : "https://ars.els-cdn.com/content/image/X01436228.jpg","title" : "Applied Geography","issn" : "0143-6228","type" : "Supports open access","price" : "","impactFactor" : "4.732","otherMetric" : "8.3","nameOtherMetric" : "CiteScore","acceptanceRate" : "","timeDecision" : "","timePublication" : "2 weeks","timeReview" : "","quartil" : "()","sjr_ranking":"1.169","predator" : "NO"},{"url" : "https://www.journals.elsevier.com/child-abuse-and-neglect","imagePath" : "https://ars.els-cdn.com/content/image/X01452134.jpg","title" : "Child Abuse & Neglect","issn" : "1873-7757","type" : "Supports open access","price" : "","impactFactor" : "4.863","otherMetric" : "5.9","nameOtherMetric" : "CiteScore","acceptanceRate" : "","timeDecision" : "","timePublication" : "1.8 weeks","timeReview" : "","quartil" : "()","sjr_ranking":"None","predator" : "NO"},{"url" : "https://peh-med.biomedcentral.com","imagePath" : "//media.springernature.com/lw450/springer-cms/rest/v1/content/23369958/data/v1","title" : "Philosophy, Ethics, and Humanities in Medicine","issn" : "1747-5341","type" : "Open Access","price" : "$1590.00","impactFactor" : "2.2","otherMetric" : "2.019","nameOtherMetric" : "5-year Impact Factor ","acceptanceRate" : "","timeDecision" : "49.1 weeks","timePublication" : "","timeReview" : "","quartil" : "()","sjr_ranking":"0.54","predator" : "NO"},{"url" : "https://urbantransformations.biomedcentral.com","imagePath" : "//media.springernature.com/lw450/springer-cms/rest/v1/content/25242830/data/v1","title" : "Urban Transformations","issn" : "2524-8162","type" : "Open Access","price" : "$1040.00","impactFactor" : "0.0","otherMetric" : "0.0","nameOtherMetric" : "","acceptanceRate" : "","timeDecision" : "","timePublication" : "","timeReview" : "","quartil" : "()","sjr_ranking":"None","predator" : "NO"},{"url" : "https://www.journals.elsevier.com/case-reports-in-womens-health","imagePath" : "https://ars.els-cdn.com/content/image/X22149112.jpg","title" : "Case Reports in Womens Health","issn" : "2214-9112","type" : "Open access","price" : "$790","impactFactor" : "0.0","otherMetric" : "0.0", "nameOtherMetric":"", timeReview" : "1 week","quartil" : "()","sjr_ranking":"0.318","predator" : "NO"},{"url" : "https://www.journals.elsevier.com/artificial-intelligence-in-the-life-sciences","imagePath" : "https://ars.els-cdn.com/content/image/X26673185.jpg","title" : "Artificial Intelligence in the Life Sciences","issn" : "2667-3185","type" : "Open access","price" : "","impactFactor" : "0.0","otherMetric" : "0.0","nameOtherMetric" : "","acceptanceRate" : "","timeDecision" : "1.5 weeks","timePublication" : "0.5 weeks","timeReview" : "2.2 weeks","quartil" : "()","sjr_ranking":"None","predator" : "NO"},{"url" : "https://www.journals.elsevier.com/chemico-biological-interactions","imagePath" : "https://ars.els-cdn.com/content/image/X00092797.jpg","title" : "Chemico-Biological Interactions","issn" : "1872-7786","type" : "Supports open access","price" : "","impactFactor" : "5.168","otherMetric" : "9.0","nameOtherMetric" : "CiteScore","acceptanceRate" : "","timeDecision" : "3.5 weeks","timePublication" : "0.9 weeks","timeReview" : "5.2 weeks","quartil" : "()","sjr_ranking":"None","predator" : "NO"}]' 
    json = '[{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=172560&copyownerid=45217","title" : " icSPORTS  2023 : 11th International Conference on Sport Sciences Research and Technology Support","date" : "Nov 16, 2023 - Nov 17, 2023","location" : "Lisbon, Portugal","dueDate" : "Jun 2, 2023","organization" : "icSPORTS","type" : "In-person","tags" : ["information technology", "biotechnology", "health", "computer science"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=144119&copyownerid=167492","title" : " Animal Personality  2021 : The Evolution and Consequences of Animal Personality","date" : "N/A","location" : "N/A","dueDate" : "Nov 26, 2021","organization" : "Personality","type" : "In-person","tags" : ["animal behaviour", "ecology", "evolution", "zoology"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=167993&copyownerid=176666","title" : " Nature Scientific Reports  2022 : Special Issue on Bioinspired Robotic Locomotion","date" : "Jun 1, 2022 - Nov 30, 2022","location" : "n/a","dueDate" : "Nov 30, 2022","organization" : "Reports","type" : "In-person","tags" : ["robotics", "biology", "engineering"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=172685&copyownerid=180500","title" : " TEDEAL  2023 : Terrarium. Earth design: Ecology, Architecture and Landscape,","date" : "N/A","location" : "N/A","dueDate" : "Apr 20, 2023","organization" : "TEDEAL","type" : "In-person","tags" : ["architecture", "design", "landscape"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=164374&copyownerid=170233","title" : " AGRIJ  2023 : Agricultural Science: An International journal ","date" : "N/A","location" : "N/A","dueDate" : "May 13, 2023","organization" : "AGRIJ","type" : "In-person","tags" : ["biological sciences", "environmental", "biodiversity", "physiology"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=169678&copyownerid=174797","title" : " TOCS  2022 : 2022 IEEE Conference on Telecommunications, Optics and Computer Science","date" : "Dec 11, 2022 - Dec 12, 2022","location" : "","dueDate" : "Oct 30, 2022","organization" : "TOCS","type" : "Virtual","tags" : ["telecommunications", "optics", "computer science"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=93681&copyownerid=156881","title" : " CFP - Eco-Comics  2020 : Call for Papers – CLOSURE: The Kiel University e-Journal for Comics Studies #7 (November 2020) / Thematic Section: »Eco-Comics: What Grows in the Gutter?«","date" : "N/A","location" : "N/A","dueDate" : "Mar 1, 2020","organization" : "Comics","type" : "In-person","tags" : ["ecocriticism", "comics studies", "popular culture", "ecology"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=153036&copyownerid=172349","title" : " MUISC-HUMSOS CONGRESS  2022 : TOWARDS SUSTAINABLE SOCIETIES: PROSPECTS AND RETROSPECTS","date" : "Jun 2, 2022 - Jun 4, 2022","location" : "ISTANBUL- TURKEY","dueDate" : "May 9, 2022","organization" : "CONGRESS","type" : "In-person","tags" : ["social sciencies", "economic and administration", "law", "communication"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=168100&copyownerid=176770","title" : " Open Call for Book Chapter Proposals  2022 : Language Society and  the Environment","date" : "N/A","location" : "N/A","dueDate" : "Sep 15, 2022","organization" : "Proposals","type" : "In-person","tags" : ["interdisciplinary", "environmental", "education", "ecolinguistics"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=159344&copyownerid=168534","title" : " ReVIEWING BMC  2022 : Call for Proposals: ReVIEWING Black Mountain College 13","date" : "Oct 7, 2022 - Oct 9, 2022","location" : "Asheville, NC","dueDate" : "Jul 1, 2022","organization" : "BMC","type" : "In-person","tags" : ["art", "art history", "20th century", "black mountain college"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=96303&copyownerid=9913","title" : " IEETeL  2020 : International Workshop on Interactive Environments and Emerging Technologies for eLearning","date" : "Jun 17, 2020 - Jun 17, 2020","location" : "LAquila, Italy","dueDate" : "Jan 31, 2020","organization" : "IEETeL","type" : "In-person","tags" : ["elearning", "technology", "intelligent systems", "collaboration"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=85463&copyownerid=136719","title" : " PJA “Towards Climate Justice. Eco-Strate  2020 : “Towards Climate Justice. Eco-Strategies for Survival” The Polish Journal of Aesthetics No. 58 (3/2020)","date" : "N/A","location" : "N/A","dueDate" : "Mar 31, 2020","organization" : "Strate","type" : "In-person","tags" : ["philosophy", "aesthetics", "climate", "ecology"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=172215&copyownerid=180020","title" : " BICA*AI  2023 : 2023 Annual International Conference on Brain-Inspired Cognitive Architectures for Artificial Intelligence","date" : "Oct 13, 2023 - Oct 15, 2023","location" : "Ningbo,China","dueDate" : "May 18, 2023","organization" : "AI","type" : "In-person","tags" : ["artificial intelligence", "cognitive science", "neuroscience", "social, economic and education"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=171473&copyownerid=175691","title" : " PEMWN  2023 : Performance Evaluation and Modeling in Wired and Wireless Networks","date" : "Sep 27, 2023 - Sep 29, 2023","location" : "Berlin, Germany","dueDate" : "Apr 30, 2023","organization" : "PEMWN","type" : "In-person","tags" : ["architectures", "protocols", "networks", "software"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=61595&copyownerid=96288","title" : " BELYAEV CONFERENCE  2017 : Belyaev Conference - a triumphant event with international participation in commemoration of the centenary of the birth of Academician Dmitri Belyaev","date" : "Aug 7, 2017 - Aug 10, 2017","location" : "Novosibirsk, Russia","dueDate" : "May 15, 2017","organization" : "CONFERENCE","type" : "In-person","tags" : ["biology", "molecular biology", "bioinformatics", "biomedical"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=148454&copyownerid=77697","title" : " COSTA  2021 : The 7th Conference on Sustainable Tourism in Asia","date" : "Dec 6, 2021 - Dec 7, 2021","location" : "Tokyo, Japan","dueDate" : "Nov 15, 2021","organization" : "COSTA","type" : "In-person","tags" : ["tourism", "eco tourism", "hotel management", "post covid-19 tourism"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=113533&copyownerid=105955","title" : " ENVIRONMENT  2021 : The Environment: A Global Interdisciplinary Conference","date" : "Apr 18, 2021 - Apr 19, 2021","location" : "Vienna, Austria","dueDate" : "Sep 25, 2020","organization" : "ENVIRONMENT","type" : "In-person","tags" : ["environment", "ecocriticism", "ecology", "sustainability"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=87137&copyownerid=145340","title" : " IS4SI  2019 : INTERNATIONAL SOCIETY FOR INFORMATION  STUDIES - Where’s the I in AI and the meaning in information?","date" : "Jun 2, 2019 - Jun 6, 2019","location" : "Berkeley, California. USA","dueDate" : "Apr 15, 2019","organization" : "IS4SI","type" : "In-person","tags" : ["artificial intelligence", "neuroscience", "information theory", "information science"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=87136&copyownerid=145340","title" : " IS4SI  2019 : INTERNATIONAL SOCIETY FOR INFORMATION  STUDIES - Where’s the I in AI and the meaning in information?","date" : "Jun 2, 2019 - Jun 6, 2019","location" : "Berkeley, California. USA","dueDate" : "Apr 15, 2019","organization" : "IS4SI","type" : "In-person","tags" : ["artificial intelligence", "neuroscience", "information theory", "information science"]},{"url" : "http://www.wikicfp.com//cfp/servlet/event.showcfp?eventid=91107&copyownerid=39648","title" : " Learning Sustainability  2019 : Learning Sustainability","date" : "N/A","location" : "N/A","dueDate" : "Oct 30, 2019","organization" : "Sustainability","type" : "In-person","tags" : ["learning", "sustainability", "earth", "ecology"]}]'
    return json