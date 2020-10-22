import nltk
from nltk import ne_chunk, pos_tag
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from nltk.corpus import words
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer


def preprocessing(tokenize_text):
    pos_tag_text = pos_tag(tokenize_text)
    chunk_text = ne_chunk(pos_tag_text, binary=True)

    return chunk_text


def get_named_entity(chunk_text):
    continuous_chunk = []
    current_chunk = []

    for i in chunk_text:
        if type(i) == nltk.Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue
    if current_chunk:
        named_entity = " ".join(current_chunk)
        if named_entity not in continuous_chunk:
            continuous_chunk.append(named_entity)
            current_chunk = []

    return continuous_chunk


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


# From https://dictionary.cambridge.org/grammar/british-grammar/word-formation/prefixes
english_prefixes = {
    "anti": "",  # e.g. anti-goverment, anti-racist, anti-war
    "auto": "",  # e.g. autobiography, automobile
    "de": "",  # e.g. de-classify, decontaminate, demotivate
    "dis": "",  # e.g. disagree, displeasure, disqualify
    "down": "",  # e.g. downgrade, downhearted
    "extra": "",  # e.g. extraordinary, extraterrestrial
    "hyper": "",  # e.g. hyperactive, hypertension
    "il": "",  # e.g. illegal
    "im": "",  # e.g. impossible
    "in": "",  # e.g. insecure
    "ir": "",  # e.g. irregular
    "inter": "",  # e.g. interactive, international
    "mega": "",  # e.g. megabyte, mega-deal, megaton
    "mid": "",  # e.g. midday, midnight, mid-October
    "mis": "",  # e.g. misaligned, mislead, misspelt
    "non": "",  # e.g. non-payment, non-smoking
    "over": "",  # e.g. overcook, overcharge, overrate
    "out": "",  # e.g. outdo, out-perform, outrun
    "post": "",  # e.g. post-election, post-warn
    "pre": "",  # e.g. prehistoric, pre-war
    "pro": "",  # e.g. pro-communist, pro-democracy
    "re-": "",  # e.g. re-consider, re-do, re-write
    "semi": "",  # e.g. semicircle, semi-retired
    "sub": "",  # e.g. submarine, sub-Saharan
    "super": "",  # e.g. super-hero, supermodel
    "tele": "",  # e.g. television, telephathic
    "trans": "",  # e.g. transatlantic, transfer
    "ultra": "",  # e.g. ultra-compact, ultrasound
    "un": "",  # e.g. under-cook, underestimate
    "up": "",  # e.g. upgrade, uphill
}

lemmatizer = WordNetLemmatizer()


def stem_prefix(word, prefixes, roots):
    original_word = word
    word = lemmatizer.lemmatize(word)
    for prefix in sorted(prefixes, key=len, reverse=True):
        # Use subn to track the no. of substitution made.
        # Allow dash in between prefix and root. 
        word, nsub = re.subn("{}[\-]?".format(prefix), "", word)
        if nsub > 0 and word in roots:
            return word
    return original_word


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


def stem_suffix(word, suffixes, roots):
    original_word = word
    word = lemmatizer.lemmatize(word)
    for suffix in sorted(suffixes, key=len, reverse=True):
        # Use subn to track the no. of substitution made.
        # Allow dash in between prefix and root.
        word, nsub = re.subn("{}[\-]?".format(suffix), "", word)
        if nsub > 0 and word in roots:
            return word
    return original_word


whitelist = list(wn.words()) + words.words()
stemmer = SnowballStemmer("english")


def snowball_with_prefix_stemmer(word, prefixes=english_prefixes):
    return SnowballStemmer("english").stem(stem_prefix(word, prefixes, whitelist))


def snowball_stemmer(word, prefixes=english_prefixes):
    return SnowballStemmer("english").stem(word)


############################ TEXT PROCESSING ############################
questions = [
    "Quelle cours d'eau est traversé par le pont de Brooklyn?",
    "Who created Wikipedia?",
    "In which country does the Nile start?",
    "What is the highest place of Karakoram?",
    "Who designed the Brooklyn Bridge?",
    "Who created Goofy?",
    "Who is the mayor of New York City?",
    "Through which countries does the Yenisei river flow?",
    "Which museum exhibits The Scream by Munch?",
    "Which states border Illinois?",
    "Who was the wife of U.S. president Lincoln?",
    "In which programming language is GIMP written?",
    "In which country is the Limerick Lake?",
    "Who developed the video game World of Warcraft?"
    "Who owns Aldi?",
    "What is the area code of Berlin?",
    "When was the Battle of Gettysburg?",
    "What are the official languages of the Philippines?",
    "Give me the homepage of Forbes.",
    "Which awards did WikiLeaks win?",
    "Give me all actors starring in Last Action Hero.",
    "Who is the owner of Universal Studios?",
    "What did Bruce Carver die from?",

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

question = questions[10]
answer = answers[10]

tokenize_text = word_tokenize(question)
chunk_text = preprocessing(tokenize_text)
named_entity = get_named_entity(chunk_text)
named_entity_normalized = []

for name in named_entity:
    named_entity_normalized.append("_".join(name.split()))
responses, questions_words = get_response_type(question)

# Tokenize sentence without stop word
tokenize_text_sw = remove_stop_word(tokenize_text)

# List of words we already treated
used_words = [w for w in questions_words]
used_words += [w for w in named_entity]

# list of word we did not use yet
unused_words = remove_already_used_word(tokenize_text_sw, used_words)

# list of the unused word chunked and stemmed
# unused_stem_words[x][0] : the stem word
# unused_stem_words[x][1] : the tag of the word
unused_stem_words = []
for word in unused_words:
    for chunk in chunk_text:
        if chunk[0] == word:
            stem = snowball_stemmer(chunk[0])
            chunk_tuple = (stem, chunk[1])
            unused_stem_words.append(chunk_tuple)

# Sorted list of the unused word, we want to get the most useful word
unused_word_ranking = []

# The most useful tag would be the verb
for word in unused_stem_words:
    if word[1] == 'VBZ':
        unused_word_ranking.append(word[0])

# The second most useful tag would be JJS
for word in unused_stem_words:
    if word[1] == 'JJS':
        unused_word_ranking.append(word[0])

for word in unused_stem_words:
    if word[1] == 'NN':
        unused_word_ranking.append(word[0])

print(question)
print(tokenize_text)
print(chunk_text)

print('\nNamed Entity : ' + str(named_entity))
print('Response type possible : ' + str(responses))
print('Unused stem words : ' + str(unused_stem_words))
print('Unused word ranked by tag : ' + str(unused_word_ranking))

############################ Query ############################

from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

query = None

if len(named_entity_normalized) != 0 and len(unused_word_ranking) != 0:
    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX res: <http://dbpedia.org/resource/>
    SELECT DISTINCT ?uri 
    WHERE {
    res:""" + named_entity_normalized[0] + """ dbo:""" + unused_word_ranking[0] + """ ?uri .
    }"""

    print(query)

sparql.setQuery(query)

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

print('Our answer : ')

for result in results["results"]["bindings"]:
    print(result["uri"]["value"])


print('\nTrue answer : \n' + str(answer))
# Nous avons remarqué que ntlk se trompe sur certains Names Entiy, comme Nile
