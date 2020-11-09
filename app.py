import os
import requests # used to send external HTTP GET requests to grab the specific user-provided URL
import operator
import re
import nltk
from flask import Flask, render_template, request # request is used to handle GET and POST requests within the Flask app
from flask_sqlalchemy import SQLAlchemy
from stop_words import stops 
from collections import Counter
from bs4 import BeautifulSoup


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Result

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == 'POST':
        # get url that the user has entered
        try:
            url = request.form['url']
            r = requests.get(url)
        except:
            errors.append("Unable to get URL. Please make sure it's valid and try again.")
        if r:
            # text processing
            # used beautifulsoup to clean the text, by removing the HTML tags that we got back from the URL
            raw = BeautifulSoup(r.text, 'html.parser').get_text()
            nltk.data.path.append('./nltk_data/') # set the path
            # nltk - Tokenize the raw text (break up the text into individual words)
            tokens = nltk.word_tokenize(raw)
            # Turn the tokens into an nltk text object
            text = nltk.Text(tokens)
            # remove punctuations
            # regular expression that matched anything in the standard alphabet
            nonPunct = re.compile('.*[A-Za-z].*')
            # using a list comprehension, we created a list of words without punctuation or numbers
            raw_words = [w for w in text if nonPunct.match(w)]
            # number of times each word appeared in the list using Counter
            raw_word_count = Counter(raw_words)
            # stop words
            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)
            
            # created a dictionary with the words (as keys) and their associated counts (as values).
            # used the sorted method to get a sorted representation of our dictionary
            # we can use the sorted data to display the words with the highest count at the top of the list, 
            # which means that we won’t have to do that sorting in our Jinja template.
            results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )[:10]
            # save the results
            try:
                result = Result(
                    url=url,
                    result_all=raw_word_count,
                    result_no_stop_words=no_stop_words_count
                )
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to database.")

    return render_template('index.html',errors=errors,results=results)
    

if __name__ == '__main__':
    app.run()