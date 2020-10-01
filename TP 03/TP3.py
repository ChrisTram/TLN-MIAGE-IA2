import nltk
nltk.download('words')

def preprocessing(text):
    tokenize_text = nltk.word_tokenize(text)
    pos_tag_text = nltk.pos_tag(tokenize_text)

    return pos_tag_text


text = "God is Great! I won a lottery."
text = preprocessing(text)
print(nltk.ne_chunk(text, binary=True))
