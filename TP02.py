
import nltk
from nltk.corpus import brown 
from nltk.corpus import treebank

#text = nltk.word_tokenize("Now we are having a Linguistics class")
#
#print(nltk.pos_tag(text))
#nltk.download('brown')
#nltk.download('universal_tagset')
#nltk.download('treebank')
#brown_news_tagged = brown.tagged_words(categories='news',tagset='universal')
#tag_fd = nltk.FreqDist(tag for (word, tag) in brown_news_tagged) 
#print(tag_fd.most_common())
#text = nltk.Text(word.lower() for word in nltk.corpus.brown.words())
#text.similar('woman')
#print(nltk.corpus.treebank.parsed_sents('wsj_0001.mrg')[1]) 
#nltk.corpus.treebank.parsed_sents('wsj_0001.mrg')[1].draw()

#str = 'S -> NP VP VP -> V NP | V NP PP PP -> P NP V -> "saw" | "ate" | "walked" NP -> "John" | "Mary" | "Bob" | Det N | Det N PP Det -> "a" | "an" | "the" | "my" N -> "man" | "dog" | "cat" | "telescope" | "park" P -> "in" | "on" | "by" | "with"'

grammar1 = nltk.CFG.fromstring("""
S -> NP VP 
VP -> V NP | V NP PP
PP -> P NP 
V -> "saw" | "ate" | "walked" | "chase"
NP -> "John" | "Mary" | "Bob" | Det N | Det N PP
Det -> "a" | "an" | "the" | "my"
N -> "man" | "dog" | "cat" | "dogs" | "cats" | "telescope" | "park"
P -> "in" | "on" | "by" | "with" """)

#sent = "dogs chase cats".split()
#rd_parser = nltk.RecursiveDescentParser(grammar1) 
#for tree in rd_parser.parse(sent): 
#    print(tree)

grammaire = nltk.CFG.fromstring("""
S -> SN SV
SN -> Art Nom
SV -> V SN | V
Nom -> 'chien' | 'chat'
Art -> 'le'
V -> 'mange'
V -> 'dort'
""")

sent = "le chien mange le chat".split()
rd_parser = nltk.RecursiveDescentParser(grammaire) 
for tree in rd_parser.parse(sent): 
    print(tree)

nltk.app.rdparser()