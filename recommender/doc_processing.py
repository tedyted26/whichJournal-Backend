import spacy
from sklearn.feature_extraction.text import CountVectorizer
import os
import csv

def tokenizer(text):
    nlp = spacy.load("en_core_web_sm")
    text_doc = nlp(text.translate({ord(i): " " for i in "0123456789ºª!·$%&/()=|@#~€¬'?¡¿`+^*[]´¨}{,.-;:_<>\n \""}))

    text_lemma = [token.lemma_.lower().strip() for token in text_doc if not token.is_stop and not token.is_punct and not len(token)<2]

    return text_lemma

def update_dictionary_and_matrix(mydb, table:str, entries:int):
  
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM "+table+" ORDER BY id DESC LIMIT "+str(entries))
    new_data = mycursor.fetchall()

    file_name = "tf_"+table+"_matrix.csv"

    vectorizer = CountVectorizer(tokenizer = tokenizer)

    for i in new_data:
        id = i[0]
        title = i[3]
        desc = i[4]

        X = None

        try:
            X = vectorizer.fit_transform([title + " " + desc])
        except:
            pass

        if X == None:
            continue
    
        mycursor.execute("SELECT word FROM "+table+"_dictionary")
        result = mycursor.fetchall()
        columns_db = []
        for u in result:
            columns_db.append(u[0])

        # add words to dictionary
     
        feature_columns = vectorizer.get_feature_names_out()
        new_columns = []

        for c in feature_columns:
            if c not in columns_db and c != "":
                new_columns.append(c)

        if new_columns != []:
            text = "(" + str(new_columns).replace("[", "").replace("]", "").replace(", ","),(") + ");"
            mycursor.execute("INSERT INTO "+table+"_dictionary (word) VALUES "+text)
            mydb.commit()

        if not os.path.exists('recommender/' + file_name):
            with open('recommender/' + file_name, 'w') as file:
                # write initial content to the file
                file.write("")

        # insert frequencies
        row = []
        if new_columns != []:
            columns_db.extend(new_columns)
        for term in columns_db:
            if term in feature_columns:
                for i in range(X.size):
                    word = feature_columns[X.indices[i]]
                    if word != "" and term == word:
                        row.append(str(X.data[i]))         
            else:
                row.append('0')  

        with open('recommender/' + file_name, 'a+', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

        query = "INSERT INTO "+table+"_order ("+table.removesuffix("s")+"_id) VALUES ("+str(id)+");"
        mycursor.execute(query)
        mydb.commit()
    
    mycursor.execute("SELECT count(id) FROM "+table+"_dictionary")
    words = mycursor.fetchall()[0][0]

    # add 0s to rows that have new words
    with open('recommender/' + file_name, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)

    for row in data:
        lenght = len(row)
        if lenght < words:
            for c in range(words - lenght):
                row.append('0')
    
    with open('recommender/' + file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
