import nltk
from nltk import ne_chunk, pos_tag
from nltk.tokenize import word_tokenize
import re
from nltk.corpus import words
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer 
def preprocessing(text):
    tokenize_text = word_tokenize(text)
    pos_tag_text = pos_tag(tokenize_text)
    chunk_text = ne_chunk(pos_tag_text, binary=True)

    return chunk_text


def get_named_entity(chunk_text):
    prev = None
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
        "which": [""] #Prendre le mot qui vient après
    }
    return switcher.get(argument, None)


def get_response_type(text):
    # Regex to find every word starting by 'wh'
    questions = re.findall(r'\bwh[a-zA-Z]+\b', text.lower())
    responses = []

    for q in questions:
        res = switch_question_type(q)

        if res is not None:
            for r in res:
                responses.append(r)

    return responses


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
"re": "",     # e.g. reconsider, redo, rewrite
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

porter = PorterStemmer()

whitelist = list(wn.words()) + words.words()

def porter_english_plus(word, prefixes=english_prefixes):
    return porter.stem(stem_prefix(word, prefixes, whitelist))


# text = "Which river does the Brooklyn Bridge cross?"
text = "Who created Wikipedia?"
# text = "In which country does the Nile start?"
# text = "What is the highest place of Karakoram?"

chunk_text = preprocessing(text)
named_entity = get_named_entity(chunk_text)
responses = get_response_type(text)

######### TODO
# remove stop word
# remove already used word
# created -> create
# lemmatisation

# 1. exact match
# 2. levenstein owst
# 3. word net similarities

# print(text)
# print(chunk_text)
# print('Named Entity : ' + str(named_entity))
# print('Response type possible : ' + str(responses))

print("impossible with stem_pref : ", stem_prefix("impossible", prefixes=english_prefixes, roots=whitelist))
print("impossible with porter : ", porter_english_plus("impossible"))

print("hyperactive with stem_pref : ", stem_prefix("hyperactive", prefixes=english_prefixes, roots=whitelist))
print("hyperactive with porter : ", porter_english_plus("hyperactive"))

print("midnight with stem_pref : ", stem_prefix("midnight", prefixes=english_prefixes, roots=whitelist))
print("midnight with porter : ", porter_english_plus("midnight"))