import mysql.connector
import BeallsList, BioMedCentral, Elsevier, MDPI, Springer, wikiCFP
import Conference, Journal
import logging
import datetime

# LOG SETUP

##############################################
date = datetime.datetime.now()
logname = str(date.day) + "-" +str(date.month) + "-" + str(date.year) + "__" + date.strftime("%X").replace(":", "-")

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("webscraping/logs/" + logname + '.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

##############################################

# BBDD CONNECTION

##############################################

try:
  mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="root",
  database="whichjournal"
  )
except mysql.connector.Error:
  logger.critical("Couldn't connect to DB. Error in Mysql.connector")


add_journal = ("INSERT IGNORE INTO journals "
               "(url, imagePath, title, description, issn, type, price," 
               "impactFactor, quartil, otherMetric, nameOtherMetric, acceptanceRate," 
               "timeDecision, timePublication, timeReview, origin, indexing) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s,"
                "%s, %s, %s, %s, %s,"
                "%s, %s, %s, %s, %s)")

add_conference = ("INSERT IGNORE INTO conferences "
               "(url, title, description, topics, date, location, dueDate," 
               "organization, type, tags, price, origin) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s,"
                "%s, %s, %s, %s, %s)")

add_beall = ("INSERT IGNORE INTO beall "
               "(name, url, isUpdated, beallsType) "
               "VALUES (%s, %s, %s, %s)")

mycursor = mydb.cursor()

##############################################

# ONLY EXECUTED ONCE

##############################################
# b_pub = BeallsList.getBeallsPublishers()  # data_beall = (item, b_pub[item], 0, 1)
# b_pub_u = BeallsList.getBeallsPublishersUpdated() # data_beall = (item, b_pub[item], 1, 1)
# b_journals = BeallsList.getBeallsStandaloneJournals() # data_beall = (item, b_pub[item], 0, 2)
# b_journals_u = BeallsList.getBeallsStandaloneJournalsUpdated() # data_beall = (item, b_pub[item], 1, 2)
# b_van = BeallsList.getBeallsVanityPress() # data_beall = (item, b_pub[item], 0, 3)

# for item in b_van:
#   data_beall = (item, b_van[item], 0, 3)
#   mycursor.execute(add_beall, data_beall)
##############################################

# JOURNALS

##############################################

def insert_journals(journal_list:list, origin:str):
    if journal_list == []:
      logger.error(origin + ' Scraping failed')
    else:
      lenght = len(journal_list)
      logger.info("Starting " + origin + "... "+str(lenght)+" total")
      i = 0
      for url in journal_list:
          journal = None
          try:
            if origin == "ELSEVIER":

              mycursor.execute("SELECT id FROM journals WHERE origin = 'Elsevier' AND url = '"+url+"'")
              result = mycursor.fetchall()

              if result != []:
                continue
              journal = Elsevier.getElsevierJournalDetails(url)
            elif origin == "BMC":
              journal = BioMedCentral.getBMCJournalDetails(url)
            elif origin == "SPRINGER":
              journal = Springer.getSpringerJournalDetails(url)
            elif origin == "MDPI":
              journal = MDPI.getMDPIJournalDetails(url)
          except:
            logger.error(str(i+1)+"/"+str(lenght) + " " + origin + " Scraping failed. Url: "+url)

          if journal != None and (journal.title=="" or journal.issn == ""):        
            logger.warning(str(i+1)+"/"+str(lenght) + " Empty Journal: " + url)
          elif journal != None:
            data_journal = (journal.url, journal.imagePath, journal.title, journal.description, journal.issn, 
                            journal.type, journal.price, journal.impactFactor, journal.quartil,
                            journal.otherMetric, journal.nameOtherMetric, journal.acceptanceRate, 
                  journal.timeDecision, journal.timePublication, journal.timeReview, journal.origin, str(journal.indexing))
            try: 
              mycursor.execute(add_journal, data_journal)
              mydb.commit()
            except Exception:
              e = str(type(Exception).__name__)
              logger.error("Insert into DB failed. Origin: "+ origin + ", Url: "+url+" Error: "+ e)
          i = i+1
    logger.info(origin + " Ended")


bmc = []
els = []
mdpi = []
spr = []

#--------BMC--------#
# try:
#   bmc = BioMedCentral.getBMCJournals()
# except:
#   pass

# insert_journals(bmc, "BMC")

#--------ELSEVIER--------#

# try:
#   els = Elsevier.getElsevierJournals(Elsevier.getElsevierPages())
# except:
#   pass

# insert_journals(els, "ELSEVIER")

#--------SPRINGER--------#

# try:
#   spr = Springer.getSpringerJournals()
# except:
#   pass

# insert_journals(spr, "SPRINGER")

#--------MDPI--------#

# try:
#   mdpi = MDPI.getMDPIJournals()
# except:
#   pass

# insert_journals(mdpi, "MDPI")

##############################################

# CONFERENCES

##############################################

def insert_conferences(conference_list:list, origin:str):
    if conference_list == []:
      logger.error(origin + ' Scraping failed')
    else:
      lenght = len(conference_list)
      logger.info("Starting " + origin + "... "+str(lenght)+" total")
      i = 0
      for url in conference_list:
          conference = None
          try:
            if origin == "WIKICFP":         
              mycursor.execute("SELECT id FROM conferences WHERE origin = 'WikiCFP' AND url = 'http://www.wikicfp.com/"+url+"'")
              result = mycursor.fetchall()

              if result != []:
                continue
              
              conference = wikiCFP.getWikiCFPConferenceDetails("http://www.wikicfp.com/" + url)
          except:
            logger.error(str(i+1)+"/"+str(lenght) + " " + origin + " Scraping failed. Url: http://www.wikicfp.com/"+url)

          if conference != None and (conference.titulo=="" or conference.descripcion==""):        
            logger.warning(str(i+1)+"/"+str(lenght) + " Empty Conference: " + url)
          elif conference != None:
            data_conference = (conference.url, conference.titulo, conference.descripcion,  str(conference.temas),
                               conference.fecha, conference.ubicacion, conference.fechaInscripcion, conference.organizacion,
                              conference.tipo,  str(conference.tags), conference.precio, conference.origen)

            try: 
              mycursor.execute(add_conference, data_conference)
              mydb.commit()
            except Exception:
              logger.error("Insert into DB failed. Origin: "+ origin + ", Url: "+url+" Error: "+ str(Exception.__name__))
          i = i+1
    logger.info(origin + " Ended")


wiki = []

#--------WikiCFP--------#
# categories = []
list_conferences = []

# try:
#   categories = wikiCFP.getWikiCFPCategories()
# except:
#   logger.error('WikiCFP Category scraping failed')

for c in wikiCFP.getSavedCategories():
  new_links = []
  try:
    new_links = wikiCFP.getWikiCFPConferences(c)
  except:
    logger.warning('WikiCFP Category page scraping skipped')
  
  if new_links != []:
    wiki.extend(new_links)

insert_conferences(wiki, "WIKICFP")

mycursor.close()
mydb.close()


