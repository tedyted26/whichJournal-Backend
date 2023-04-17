import logging
import mysql.connector
import datetime
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import doc_processing
import os
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_selection import mutual_info_classif


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
  

  def recommend(self, title, desc, keywords, table = "journals"):
    if not os.path.isfile('recommender/tf_' + table + '_matrix.csv'):
       self.logger.error('File not found: recommender/tf_' + table + '_matrix.csv')
       return 

    # get diccionary
    dictionary = self.getDictionary(table)

    # get input
    self.logger.info('Adapting input to matrix size...') 

    corpus = [title + " " + title + " "+ desc + " " + keywords + " " + keywords + " " + keywords]
    vectorizer = CountVectorizer(tokenizer = doc_processing.tokenizer)

    X = vectorizer.fit_transform(corpus)
    feature_columns = vectorizer.get_feature_names_out()

    # create a tf_row from input
    tf_input_row = []
    for term in dictionary:
      if term[1] in feature_columns:
          for i in range(X.size):
            word = feature_columns[X.indices[i]]
            if word != "" and term[1] == word:
                tf_input_row.append(str(X.data[i]))         
      else:
          tf_input_row.append('0')

    self.logger.info('Loading matrix...') 

    # get matrix
    tf_matrix_csv = np.loadtxt('recommender/tf_' + table + '_matrix.csv', delimiter=',')    

    self.logger.info('Transforming matrix and input into tf-idf...')

    # converto into tfidf
    tfidf_transformer = TfidfTransformer()
    tfidf_matrix = tfidf_transformer.fit_transform(tf_matrix_csv)
    tfidf_input_row = tfidf_transformer.transform([tf_input_row]) 

    self.logger.info('Calculating cosine similarity...')

    # cosine similarity
    results = cosine_similarity(tfidf_matrix, tfidf_input_row)
    
    self.logger.info('Getting id for each document...')

    # get results in a dictionary with the respective journals_order.id (from database)
    results_dic = self.getResultsDictionaryWithIds(table, results)
    
    self.logger.info('Done')

    self.logger.info('Classifying info...')
    # execute algorithm
    return self.getClassifiedResults(tfidf_matrix, tfidf_input_row)


  def getDictionary(self, table):
    mydb = None
    try:
      mydb = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="root",
      database="whichjournal"
    )
    except mysql.connector.Error:
      self.logger.critical("Couldn't connect to DB. Error in Mysql.connector")
    
    if mydb != None:
      mycursor = mydb.cursor()
      mycursor.execute("SELECT * FROM "+table+"_dictionary") 
      result = mycursor.fetchall()
      mycursor.close()
      mydb.close()
    return result

  def getClassifiedResults(self, matrix, input):
    
    order_id_entry = 1
    info_entries = {}

    #TODO
    # Call clasifier

  def getResultsDictionaryWithIds(self, table, results):
    mydb = None
    try:
      mydb = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="root",
      database="whichjournal"
    )
    except mysql.connector.Error:
      self.logger.critical("Couldn't connect to DB. Error in Mysql.connector")
    
    if mydb == None:
      return {}
    
    mycursor = mydb.cursor() 
    column_name = table.removesuffix("s") + "_id"
  
    jc_order = 1
    results_dic = {}
    for row in results:
      if row[0] == 0.0:
        jc_order += 1
        continue
      
      mycursor.execute("SELECT "+column_name+" FROM "+table+"_order WHERE id="+str(jc_order)) 
      jc_id = mycursor.fetchall()[0][0]

      results_dic[jc_id]=row[0]
      jc_order += 1

    mycursor.close()
    mydb.close()

    return results_dic
       

m = main_recommender()
m.recommend("Digital Economy and Sustainable Development", "This is the description of the text", "This may be empty or not, but it is very important", table="conferences")

