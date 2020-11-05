# This is the work of Chris TRAMIER and Mael GIESE

# TLN-MIAGE-IA2

We have several functions to process the text, then we tokenize it.

We get the named entity using spacy, we get the type of response we could have, Tokenize sentence without stop word, we separate the words depending on the use we'll have.

Then we have a list of the unused word chunked and lemmatized. We want to get the most useful word so we have a function to select the most importants terms.

We build our queries with all our results, then we print and stock the answers in a variable. We display all of them in the end with the stats.

# A result example : 

```
Who is the owner of Universal Studios?

Named Entity : ['Universal Studios']
Response type possible : ['person', 'org']
Unused lemmatized words : [('owner', 'NN')]
Unused word ranked by tag : ['owner']

        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX res: <http://dbpedia.org/resource/>
        SELECT DISTINCT ?uri
        WHERE {
        res:Universal_Studios dbo:owner ?uri .
        }
Our answer : 
http://dbpedia.org/resource/Comcast
```
