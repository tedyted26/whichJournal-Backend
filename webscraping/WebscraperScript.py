import mysql.connector
import BeallsList, BioMedCentral, Elsevier, MDPI, Springer, wikiCFP
import Conference, Journal

mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="root",
  database="whichjournal"
)

add_journal = ("INSERT IGNORE INTO journals "
               "(url, imagePath, title, description, issn, type, price," 
               "impactFactor, quartil, otherMetric, nameOtherMetric, acceptanceRate," 
               "timeDecision, timePublication, timeReview, origin, indexing) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s,"
                "%s, %s, %s, %s, %s,"
                "%s, %s, %s, %s, %s)")

add_conference = ("INSERT IGNORE INTO conferences "
               "(url, title, description, topics, date, location," 
               "organization, type, tags, price) "
               "VALUES (%s, %s, %s, %s, %s, %s,"
                "%s, %s, %s, %s)")

add_beall = ("INSERT IGNORE INTO beall "
               "(name, url, isUpdated, beallsType) "
               "VALUES (%s, %s, %s, %s)")

mycursor = mydb.cursor()

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

# mycursor.execute(add_journal, data_journal)
# result = mycursor.fetchone()

mydb.commit()
mycursor.close()
mydb.close()


