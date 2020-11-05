from nltk import ne_chunk, pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import re
import spacy_model.en_core_web_sm.en_core_web_sm as en_core_web_sm


def preprocessing(tokenize_text):
    pos_tag_text = pos_tag(tokenize_text)
    chunk_text = ne_chunk(pos_tag_text, binary=True)

    return chunk_text


def get_named_entity(text):
    nlp = en_core_web_sm.load()
    doc = nlp(text)

    named_entity = []

    for ent in doc.ents:
        # print(ent.text, ent.label_)
        named_entity.append(ent.text)

    return named_entity


def switch_question_type(argument):
    switcher = {
        "what": ["place", "org"],
        "where": ["place"],
        "why": [""],
        "who": ["person", "org"],
        "whose": [""],
        "when": ["time"],
        "which": [""]  # Prendre le mot qui vient après
    }
    return switcher.get(argument, None)


# Regex to find every word starting by 'wh'
def get_response_type(text):
    questions = re.findall(r'\bwh[a-zA-Z]+\b', text.lower())
    responses = []

    for q in questions:
        res = switch_question_type(q)

        if res is not None:
            for r in res:
                responses.append(r)

    return responses, questions


def lemmatizer(word):
    import nltk
    lemma = nltk.wordnet.WordNetLemmatizer()
    return lemma.lemmatize(word)


def remove_stop_word(tokenize_text):
    stop_words = stopwords.words('english')
    stop_words.append('?')
    filtered_sentence = [w for w in tokenize_text if not w in stop_words]
    return filtered_sentence


def remove_already_used_word(tokenise_text_without_sw, words):
    filtered_text = []
    for w in tokenise_text_without_sw:
        if w.lower() not in words and w not in words:
            filtered_text.append(w)

    return filtered_text


def get_answers(question_index, questions):
    question = questions[question_index]

    ############################ TEXT PROCESSING ############################

    tokenize_text = word_tokenize(question)
    chunk_text = preprocessing(tokenize_text)

    # Get named entity using spacy
    named_entity = get_named_entity(question)
    named_entity_normalized = []

    # Get the type of response we could have
    responses, questions_words = get_response_type(question)

    # Tokenize sentence without stop word
    tokenize_text_sw = remove_stop_word(tokenize_text)

    # List of words we already treated
    used_words = [w for w in questions_words]
    used_words += [w for w in named_entity]

    # list of word we did not use yet
    unused_words = remove_already_used_word(tokenize_text_sw, used_words)

    # list of the unused word chunked and lemmatized
    # unused_lemmatized_words[x][0] : the stem word
    # unused_lemmatized_words[x][1] : the tag of the word
    unused_lemmatized_words = []
    for word in unused_words:
        for chunk in chunk_text:
            if chunk[0] == word:
                lemm = lemmatizer(chunk[0])
                chunk_tuple = (lemm, chunk[1])
                unused_lemmatized_words.append(chunk_tuple)  # lemmatized
                # unused_stem_words.append(chunk)

    # Sorted list of the unused word, we want to get the most useful word
    unused_word_ranking = []

    # The most useful tag would be the verb
    for word in unused_lemmatized_words:
        if (word[1] == 'VBZ' or word[1] == 'JJS' or word[1] == 'NN'
                or word[1] == 'NNS' or word[1] == 'VBG' or word[1] == 'VBD'):
            unused_word_ranking.append(word[0])

    res = ""
    if len(named_entity) > 0:
        res = named_entity[0].replace(" ", "_")
        for i in range(1, len(named_entity)):
            print(named_entity[i].replace(" ", "_"))
            res += "_" + named_entity[i].replace(" ", "_")

    dbo = ""
    if len(unused_word_ranking) > 0:
        # The string we will use for the query
        dbo = unused_word_ranking[0]
        for i in range(1, len(unused_word_ranking)):
            dbo += unused_word_ranking[i].capitalize()

    print(question)

    print('\nNamed Entity : ' + str(named_entity))
    print('Response type possible : ' + str(responses))
    print('Unused lemmatized words : ' + str(unused_lemmatized_words))
    print('Unused word ranked by tag : ' + str(unused_word_ranking))

    ############################ Query ############################

    from SPARQLWrapper import SPARQLWrapper, JSON

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    query = None

    if res != "" and dbo != "":
        query = """
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX res: <http://dbpedia.org/resource/>
        SELECT DISTINCT ?uri 
        WHERE {
        res:""" + res + """ dbo:""" + dbo + """ ?uri .
        }"""

    print(query)

    if query is not None:
        answers_query = []
        sparql.setQuery(query)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results["results"]["bindings"]:
            print(result["uri"]["value"])
            answers_query.append(result["uri"]["value"])

        return answers_query
    return []


questions = [
    "Which river does the Brooklyn Bridge cross?",
    "Who created Wikipedia?",
    "In which country does the Nile start?",
    "What is the highest place of Karakoram?",
    "Who designed the Brooklyn Bridge?",
    "Who created Goofy?",
    "Who is the mayor of New York City?",
    "Through which countries does the Yenisei river flow?",
    "Which museum exhibits The Scream by Munch?",
    "Which states border Illinois?",
    "Who was the wife of US president Lincoln?",
    "In which programming language is GIMP written?",
    "In which country is the Limerick Lake?",
    "Who developed the video game World of Warcraft?",
    "Who owns Aldi?",
    "What is the area code of Berlin?",
    "When was the Battle of Gettysburg?",
    "What are the official languages of the Philippines?",
    "Give me the homepage of Forbes.",
    "Which awards did WikiLeaks win?",
    "Give me all actors starring in Last Action Hero.",
    "Who is the owner of Universal Studios?",
    "What did Bruce Carver die from?"

]

answers = [
    ["http://dbpedia.org/resource/East_River"],
    ["http://dbpedia.org/resource/Jimmy_Wales", "http://dbpedia.org/resource/Larry_Sanger"],
    ["http://dbpedia.org/resource/Ethiopia", "http://dbpedia.org/resource/Ethiopia"],
    ["http://dbpedia.org/resource/K2"],
    ["http://dbpedia.org/resource/John_A._Roebling", "http://dbpedia.org/resource/John_Augustus_Roebling"],
    ["http://dbpedia.org/resource/Art_Babbitt"],
    ["http://dbpedia.org/resource/Michael_Bloomberg"],
    ["http://dbpedia.org/resource/Mongolia", "http://dbpedia.org/resource/Russia"],
    ["http://dbpedia.org/resource/National_Gallery_of_Norway", "http://dbpedia.org/resource/National_Gallery,_Oslo"],
    ["http://dbpedia.org/resource/Kentucky", "http://dbpedia.org/resource/Missouri",
     "http://dbpedia.org/resource/Wisconsin", "http://dbpedia.org/resource/Indiana",
     "http://dbpedia.org/resource/Iowa"],
    ["http://dbpedia.org/resource/Mary_Todd_Lincoln"],
    ["http://dbpedia.org/resource/C_(programming_language)", "http://dbpedia.org/resource/GTK+"],
    ["http://dbpedia.org/resource/Canada"],
    ["http://dbpedia.org/resource/Blizzard_Entertainment"],
    ["http://dbpedia.org/resource/Karl_Albrecht", "http://dbpedia.org/resource/Theo_Albrecht"],
    ["030"],
    ["1863-07-03"],
    ["http://dbpedia.org/resource/Filipino_language"],
    ["http://www.forbes.com"],
    ["http://dbpedia.org/resource/Index_on_Censorship",
     "http://dbpedia.org/resource/Amnesty_International_UK_Media_Awards",
     "http://dbpedia.org/resource/Sam_Adams_Award"],
    ["http://dbpedia.org/resource/Arnold_Schwarzenegger", "http://dbpedia.org/resource/Anthony_Quinn",
     "http://dbpedia.org/resource/F._Murray_Abraham", "http://dbpedia.org/resource/Art_Carney",
     "http://dbpedia.org/resource/Austin_O'Brien", "http://dbpedia.org/resource/Tom_Noonan",
     "http://dbpedia.org/resource/Bridgette_Wilson", "http://dbpedia.org/resource/Charles_Dance",
     "http://dbpedia.org/resource/Robert_Prosky"],
    ["http://dbpedia.org/resource/General_Electric", "http://dbpedia.org/resource/MCA_Inc.",
     "http://dbpedia.org/resource/Seagram", "http://dbpedia.org/resource/Comcast",
     "http://dbpedia.org/resource/NBCUniversal", "http://dbpedia.org/resource/Vivendi",
     "http://dbpedia.org/resource/Independent_business"],
    ["http://dbpedia.org/resource/Cancer"]

]

system_answers = []

for i in range(len(questions)):
    system_answers.append(get_answers(i, questions))


nb_gold_standard_answers = len(answers)

nb_system_answers = 0
for a in system_answers:
    if len(a) > 0:
        nb_system_answers += 1


nb_correct_system_answers = 0
for i in range(len(answers)):
    j = 0
    for a in system_answers[i]:
        if a in answers[i]:
            j += 1
    if j > 0 and j == len(answers[i]):
        nb_correct_system_answers += 1

recall = nb_correct_system_answers/nb_gold_standard_answers
precision = nb_correct_system_answers/nb_system_answers
f_measure = (2 * precision * recall)/(precision + recall)

print('Number of system answers : ' + str(nb_system_answers))
print('Number of correct system answers : ' + str(nb_correct_system_answers))
print('Number of gold standard answers : ' + str(nb_gold_standard_answers))
print('\nRecall : ' + str(recall))
print('Precision : ' + str(precision))
print('F-measure : ' + str(f_measure))




