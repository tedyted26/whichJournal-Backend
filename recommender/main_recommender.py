import logging
import mysql.connector
import datetime
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
import doc_processing
import os
import csv


class main_recommender:
  def __init__(self):
    date = datetime.datetime.now()
    logname = str(date.day) + "-" +str(date.month) + "-" + str(date.year) + "__" + date.strftime("%X").replace(":", "-")

    self.logger = logging.getLogger()
    self.logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("recommender/logs/" + logname + '.log')
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    self.logger.addHandler(file_handler)   

    # try:
    #   self.mydb = mysql.connector.connect(
    #   host="127.0.0.1",
    #   user="root",
    #   password="root",
    #   database="whichjournal"
    #   )
    # except mysql.connector.Error:
    #   self.logger.critical("Couldn't connect to DB. Error in Mysql.connector")
  

  def recommend(self, title, desc, keywords, type = "journals"):

    # transform input
    corpus = [title + " " + title + " "+ desc + " " + keywords + " " + keywords + " " + keywords]
    tfidf_vector = TfidfVectorizer(tokenizer = doc_processing.tokenizer)
    X = tfidf_vector.fit_transform(corpus) 

    for i in range(X.shape[1]):
      print(X.data[i])
      print(tfidf_vector.get_feature_names_out()[X.indices[i]])

    matrix = None
    # get matrix
    if os.path.isfile('tf_' + type + '_matrix.csv'): #Compruebo si existe el fichero
        with open ('tf_' + type + '_matrix.csv','r') as f:
          reader = csv.reader(f)
          matrix = list(reader)
        
    # get diccionary
    dictionary = self.getDictionary()

    # result = self.getTestText()
    # title_freq = Counter(title_lemma)

    # documents = []
    # for i in result:
    #   i_text = str(i[3]) + str(i[4])
    #   documents.append(i_text)

    # add words to dictionary if they don't exist
    
    # X = tfidf_vector.fit_transform(documents)  
    # dictionary = tfidf_vector.get_feature_names_out()



    pass

  def getDictionary(self):
    try:
      mydb = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="root",
      database="whichjournal"
    )
    except mysql.connector.Error:
      self.logger.critical("Couldn't connect to DB. Error in Mysql.connector")
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM journals WHERE origin = 'Elsevier' LIMIT 0, 50")
    result = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return result


m = main_recommender()
m.recommend("This tutorial is about Natural Language Processing in spaCy. ", "This is the description of the text", "This may be empty or not, but it is very important")

