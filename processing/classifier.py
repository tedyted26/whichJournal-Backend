import datetime
import logging
import mysql.connector
import jellyfish
from processing import predator_enum
import db

class classifier_class:
    def __init__(self, logger):
        self.logger = logger

        self.logger.info('Creating classifier') 
    
    # journal_dict is a dictionary in which the key corresponds to the id of the journal from db, and the value is result of the recommendation
    def classify_predators(self, journal_dict):
        self.logger.info('Classifying predators') 

        mycursor = db.get_cursor()
    
        if mycursor == None:
            self.logger.critical("Couldn't connect to DB. Error in Mysql.connector.Cursor")
            return {}
        
        self.logger.info('Checking '+ str(len(journal_dict)) + ' journals')

        id_string_list = "("
        for id in journal_dict:
            id_string_list += str(id) + ","
        id_string_list = id_string_list.removesuffix(",") + ")"

        self.logger.info('Ids are '+ id_string_list)

        mycursor.execute("SELECT id, url, title, origin FROM journals WHERE id IN " + id_string_list)
        journals_result = mycursor.fetchall()

        mycursor.execute("SELECT url, `name` FROM beall")
        bealls_urls_with_names = mycursor.fetchall()

        self.logger.info('Classifying...')
        for row in journals_result:
            id = row[0]
            url = row[1]
            title = row[2]
            origin = row[3]

            if origin == 'MDPI':
                classification = predator_enum.Predator.MDPI.value
            else:
                classification = self.check_bealls(bealls_urls_with_names, url, title)
            
            rec = journal_dict[id]
            journal_dict[id] = [rec, classification]
        self.logger.info('DONE')
        
        return journal_dict

    def check_bealls(self, bealls_urls_with_names, url, title):
        # return "NO" for no similarity
        # return "YES" for some similarity

        for row in bealls_urls_with_names:
            modified_url = row[0]
            name = row[1]

            distance_url = jellyfish.jaro_winkler(modified_url, url)
            distance_title = jellyfish.jaro_winkler(name, title)
            
            if distance_url > 0.9 or distance_title > 0.95:
                return predator_enum.Predator.YES.value
            
        return predator_enum.Predator.NO.value






