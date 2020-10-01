import nltk
from nltk import ne_chunk, pos_tag
from nltk.tokenize import word_tokenize
import re


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
        "which": [""]
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


# text = "Which river does the Brooklyn Bridge cross?"
text = "Who created Wikipedia?"
# text = "In which country does the Nile start?"
#text = "What is the highest place of Karakoram?"

chunk_text = preprocessing(text)
named_entity = get_named_entity(chunk_text)
responses = get_response_type(text)

print('Named Entity : ' + str(named_entity))
print('Response type possible : ' + str(responses))
