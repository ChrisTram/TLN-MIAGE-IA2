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
"anti": "",    # e.g. anti-goverment, anti-racist, anti-war
"auto": "",    # e.g. autobiography, automobile
"de": "",      # e.g. de-classify, decontaminate, demotivate
"dis": "",     # e.g. disagree, displeasure, disqualify
"down": "",    # e.g. downgrade, downhearted
"extra": "",   # e.g. extraordinary, extraterrestrial
"hyper": "",   # e.g. hyperactive, hypertension
"il": "",     # e.g. illegal
"im": "",     # e.g. impossible
"in": "",     # e.g. insecure
"ir": "",     # e.g. irregular
"inter": "",  # e.g. interactive, international
"mega": "",   # e.g. megabyte, mega-deal, megaton
"mid": "",    # e.g. midday, midnight, mid-October
"mis": "",    # e.g. misaligned, mislead, misspelt
"non": "",    # e.g. non-payment, non-smoking
"over": "",  # e.g. overcook, overcharge, overrate
"out": "",    # e.g. outdo, out-perform, outrun
"post": "",   # e.g. post-election, post-warn
"pre": "",    # e.g. prehistoric, pre-war
"pro": "",    # e.g. pro-communist, pro-democracy
"re-": "",     # e.g. re-consider, re-do, re-write
"semi": "",   # e.g. semicircle, semi-retired
"sub": "",    # e.g. submarine, sub-Saharan
"super": "",   # e.g. super-hero, supermodel
"tele": "",    # e.g. television, telephathic
"trans": "",   # e.g. transatlantic, transfer
"ultra": "",   # e.g. ultra-compact, ultrasound
"un": "",      # e.g. under-cook, underestimate
"up": "",      # e.g. upgrade, uphill
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

# text = "which river does the Brooklyn Bridge cross?"
# text = "In which country does the Nile start?"
text = "What is the highest place of Karakoram?"


tokenize_text = word_tokenize(text)
chunk_text = preprocessing(tokenize_text)
named_entity = get_named_entity(chunk_text)
named_entity_normalized = []
for name in named_entity:
    named_entity_normalized.append("_".join( name.split() ))
responses, questions_words = get_response_type(text)

# Tokenize sentence without stop word
tokenize_text_sw = remove_stop_word(tokenize_text)

# List of words we already treated
used_words = [w for w in questions_words]
used_words += [w for w in named_entity]

unused_words = remove_already_used_word(tokenize_text_sw, used_words)

stem_words= []
for word in unused_words:
    stem_words.append(snowball_stemmer(word))

print(text)
print(tokenize_text)
print(chunk_text)
print('\nNamed Entity : ' + str(named_entity))
print('Response type possible : ' + str(responses))

# print(text)
# print(chunk_text)
# print('Named Entity : ' + str(named_entity))
# print('Response type possible : ' + str(responses))

#print("running with stem_pref : ", stem_prefix("running", prefixes=english_prefixes, roots=whitelist))
#print("running with snowball : ", snowball_stemmer("running"))
#
#print("hyperactive with stem_pref : ", stem_prefix("hyperactive", prefixes=english_prefixes, roots=whitelist))
#print("hyperactive with snowball : ", snowball_stemmer("hyperactive"))
#
#print("midnight with stem_pref : ", stem_prefix("midnight", prefixes=english_prefixes, roots=whitelist))
#print("midnight with snowball : ", snowball_stemmer("midnight"))
#
#print("generously with stem_pref : ", stem_prefix("generously", prefixes=english_prefixes, roots=whitelist))
#print("generously with snowball : ", snowball_stemmer("generously"))
#
#print("generously with stem_pref : ", stem_prefix("generously", prefixes=english_prefixes, roots=whitelist))
#print("generously with snowball : ", snowball_stemmer("generously"))
#
#print("creating with stem_pref : ", stem_prefix("creating", prefixes=english_prefixes, roots=whitelist))
#print("creating with snowball : ", snowball_stemmer("creating"))

from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

query = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX res: <http://dbpedia.org/resource/>
SELECT DISTINCT ?uri 
WHERE {
res:"""+ named_entity_normalized[0] + """ dbo:crosses ?uri .
}"""

sparql.setQuery(query)

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    print(result["uri"]["value"])

# Set root in script folder
import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


import xml.etree.ElementTree as etree

parser = etree.XMLParser(encoding='utf-8', recover=True)

with open("./questions.xml", 'r') as xml_file:
    xml_tree = etree.parse(xml_file, parser)
for assetType in xml_tree.findall("//query"):
    print(assetType)

#Nous avons remarqué que ntlk se trompe sur certains Names Entiy, comme Nile