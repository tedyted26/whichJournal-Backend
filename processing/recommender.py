import logging
import mysql.connector
import datetime
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from processing import doc_processing
import os
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_selection import mutual_info_classif
import db


class recommender_class:
  def __init__(self, logger):
    self.logger = logger

    self.logger.info('Creating recommender') 
  
  def recommend(self, title, desc, keywords, table = "journals", top = 20):
    self.logger.info('Recommending '+ table)
    
    if not os.path.isfile('processing/tf_' + table + '_matrix.csv'):
       self.logger.error('File not found: processing/tf_' + table + '_matrix.csv')
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
    tf_matrix_csv = np.loadtxt('processing/tf_' + table + '_matrix.csv', delimiter=',')    

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

    self.logger.info('Ordering list...')
    sorted_results = dict(sorted(results_dic.items(), key=lambda item: item[1], reverse=True)[:top])
    
    self.logger.info('Done')

    return sorted_results

  def getDictionary(self, table):
    mycursor = db.get_cursor()
    if mycursor == None:
      self.logger.critical("Couldn't connect to DB. Error in Mysql.connector.cursor") 
    else:
      mycursor.execute("SELECT * FROM "+table+"_dictionary") 
      result = mycursor.fetchall()

    return result

  def getResultsDictionaryWithIds(self, table, results):
    results_dic = {}
    mycursor = db.get_cursor()
    if mycursor == None:
      self.logger.critical("Couldn't connect to DB. Error in Mysql.connector.cursor")
      return

    column_name = table.removesuffix("s") + "_id"
  
    jc_order = 1    
    for row in results:
      if row[0] == 0.0:
        jc_order += 1
        continue
      
      mycursor.execute("SELECT "+column_name+" FROM "+table+"_order WHERE id="+str(jc_order)) 
      jc_id = mycursor.fetchall()[0][0]

      results_dic[jc_id]=row[0]
      jc_order += 1

    return results_dic
       

# m = recommender()
# m.recommend("Digital Economy and Sustainable Development", "This is the description of the text", "This may be empty or not, but it is very important", table="conferences")

