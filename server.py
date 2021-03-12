from flask import Flask, render_template, jsonify
from french import FrenchWords
import speech

french_words = FrenchWords()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/card')
def get_card():
    word = french_words.current_card["French"]
    word_eng = french_words.current_card["English"]
    count = french_words.count
    return render_template("card.html", word=word, word_eng=word_eng, count=count)

@app.route('/speaker')
def speaker():
    word = french_words.current_card["French"]
    speech.synthesize_text_file(word)
    speech.play_word()
    return ("nothing")

@app.route('/wrong', methods= ['GET'])
def wrong():
    french_words.next_card()
    word = french_words.current_card["French"]
    word_eng = french_words.current_card["English"]
    return jsonify(word=word, word_eng=word_eng)

@app.route('/right', methods= ['GET'])
def right():

    french_words.is_known()
    word = french_words.current_card["French"]
    word_eng = french_words.current_card["English"]
    count = french_words.count

    return jsonify(word=word, word_eng=word_eng, count=count)

if __name__ == "__main__":
    app.run()