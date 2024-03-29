import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2
import os
import csv
import re
import docx
import PyPDF2

def tokenizer(text):
    nlp = spacy.load("en_core_web_sm")
    #text_doc = nlp(text.translate({ord(i): " " for i in "0123456789ºª!·$%&/()=|@#~€¬'?¡¿`+^*[]´¨}{,.-;:_<>\n \""}))
    
    text_doc = text.replace("ñ", "n").replace("www", "")
    text_doc = nlp(re.sub('[^a-zA-Z]', ' ', text_doc))
    
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
        if table =="journals":
            title = i[3]
            desc = i[4]
            topics = []
            tags = []
        elif table == "conferences":
            title = i[2]
            desc = i[3]
            topics = i[4]
            tags = i[10]

        X = None

        try:
            X = vectorizer.fit_transform([title + " " + desc + " " + str(topics) + " " + str(tags)])
        except:
            pass

        if X == None:
            continue
    
        mycursor.execute("SELECT word FROM "+table+"_dictionary")
        result = mycursor.fetchall()
        columns_db = []
        for u in result:
            columns_db.append(u[0])

        # get most frequent terms
        feature_columns = vectorizer.get_feature_names_out()

        dict_frequencies = {}
        for i in range(len(X.data)):
            dict_frequencies[X.indices[i]] = X.data[i]
        
        dict_frequencies_sorted = dict(sorted(dict_frequencies.items(), key=lambda item: item[1], reverse = True))
        most_frequent_terms = []
        counter = 0
        for key in dict_frequencies_sorted:  
            if counter > 15:
                break         
            most_frequent_terms.append(feature_columns[key])
            counter += 1

        # add words to dictionary
        new_columns = []

        for c in feature_columns:
            if c not in columns_db and c != "":
                new_columns.append(c)

        if new_columns != []:
            text = "(" + str(new_columns).replace("[", "").replace("]", "").replace(", ","),(") + ");"
            mycursor.execute("INSERT INTO "+table+"_dictionary (word) VALUES "+text)
            mydb.commit()

        if not os.path.exists('processing/' + file_name):
            with open('processing/' + file_name, 'w') as file:
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

        with open('processing/' + file_name, 'a+', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

        query = "INSERT INTO "+table+"_order ("+table.removesuffix("s")+"_id) VALUES ("+str(id)+");"
        mycursor.execute(query)
        mydb.commit()
    
    mycursor.execute("SELECT count(id) FROM "+table+"_dictionary")
    words = mycursor.fetchall()[0][0]

    # add 0s to rows that have new words
    with open('processing/' + file_name, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)

    for row in data:
        lenght = len(row)
        if lenght < words:
            for c in range(words - lenght):
                row.append('0')
    
    with open('processing/' + file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def calculate_information_gain():
    pass

def transform_input_file_into_title_abstract(file):

    text = ""
    abstract = ""
    title = ""
    keywords = ""

    try:
            text = getPdfText(file)           
    except:
            try:
                text = getDocText(file)           
            except:
                raise ValueError('Could not decode the file')

    title_pattern = re.compile(r'(.*)ABSTRACT\b', re.DOTALL | re.IGNORECASE)
    try:
        title_match = title_pattern.search(text)
        title = title_match.group(1)
    except:
        pass

    abstract_pattern = re.compile(r'\bABSTRACT\b(?:\W+\w+){1,200}', re.DOTALL | re.IGNORECASE)
    try:
        abstract_match = abstract_pattern.search(text)
        abstract = abstract_match.group(0)
    except:
        pass

    keywords_pattern = re.compile(r'\bKEYWORDS\b(?:\W+\w+){1,5}', re.DOTALL | re.IGNORECASE)
    try:
        keywords_match = keywords_pattern.search(text)
        keywords = keywords_match.group(0)
    except:
        pass

    return title, abstract, keywords

def getDocText(file):
    doc = docx.Document(file)
    
    raw_text = ""
    for para in doc.paragraphs:
        raw_text += para.text

    return raw_text

def getPdfText(file):
    pdf = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    return text
    


    


# Encoding tries. Not erased in case it is needed again

    # possible_encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'ascii']
    # num_errors = []
    # encoding = ""
    # for e in possible_encodings:
    #     try:
    #         text = codecs.decode(file_contents, e)
    #         encoding = e
    #         num_errors.append(0)
    #         break
    #     except UnicodeDecodeError as error:
    #         num_errors.append(len(error.args[1]))

    # if encoding == "":
    #     min = None
    #     for i in range(len(num_errors)):
    #         if min == None:
    #             min = num_errors[i]
    #         else:
    #             if min > num_errors[i]:
    #                 min = num_errors[i]
    #                 encoding = possible_encodings[i]   
    
    # text = file_contents.decode(encoding)
    # text = file_contents.decode('windows-1252', 'ignore')