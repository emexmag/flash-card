from french import FrenchWords
import speech
from flask import Flask, render_template, redirect, url_for, flash, jsonify, Response
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import UserRegisterForm, UserLoginForm
from sqlalchemy.ext.automap import automap_base
import os
import sys

my_path = os.path.abspath(os.path.dirname(__file__))
credentials_path = os.path.join(my_path, "data/french-306416-fa272493f67b.json")
output_path = os.path.join(my_path, "static/output.ogg")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "any-secret-code-will-do")
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///french.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Base = automap_base()

##CONFIGURE TABLES

class FrenchdbWords(db.Model):
    __tablename__ = "french_words"
    id = db.Column(db.Integer, primary_key=True)
    word_fr = db.Column(db.String(250), nullable=False)
    word_en = db.Column(db.String(250), nullable=False)
    phrase_fr = db.Column(db.String(1000), nullable=False)
    phrase_en = db.Column(db.String(100), nullable=False)

class WordsLearned(db.Model):
    __tablename__ = "words_learned"
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('french_words.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(UserMixin,db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(1000))

db.create_all()

french_words_objects = {}

def add_user():
    french_words = FrenchWords(db, Base)
    french_words.set_id(current_user.id)
    french_words.load_from_table()
    french_words_objects[str(current_user.id)] = french_words
    print(french_words_objects)
    sys.stdout.flush()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/card')
@login_required
def get_card():
    word = french_words_objects[str(current_user.id)].current_card["word_fr"]
    word_eng = french_words_objects[str(current_user.id)].current_card["word_en"]
    card_id = french_words_objects[str(current_user.id)].current_card["id"]
    count = french_words_objects[str(current_user.id)].count
    phrase_fr = french_words_objects[str(current_user.id)].current_card["phrase_fr"]
    phrase_en = french_words_objects[str(current_user.id)].current_card["phrase_en"]
    return render_template("card.html", word=word, word_eng=word_eng, count=count, card_id=card_id, phrase_fr=phrase_fr, phrase_en=phrase_en)

@app.route('/speaker')
@login_required
def speaker():
    word = french_words_objects[str(current_user.id)].current_card["word_fr"]
    phrase = french_words_objects[str(current_user.id)].current_card["phrase_fr"]
    text=f"{word}...Exemple de phrase...{phrase}"
    speech.synthesize_text_file(text, current_user.id)
    return jsonify(word=word)

@app.route("/ogg")
def streamogg():

    return Response(speech.generate(current_user.id), mimetype="audio/ogg")

@app.route('/wrong', methods= ['GET'])
@login_required
def wrong():
    french_words_objects[str(current_user.id)].next_card()
    word = french_words_objects[str(current_user.id)].current_card["word_fr"]
    word_eng = french_words_objects[str(current_user.id)].current_card["word_en"]
    card_id = french_words_objects[str(current_user.id)].current_card["id"]
    phrase_fr = french_words_objects[str(current_user.id)].current_card["phrase_fr"]
    phrase_en = french_words_objects[str(current_user.id)].current_card["phrase_en"]
    return jsonify(word=word, word_eng=word_eng, card_id=card_id, phrase_fr=phrase_fr, phrase_en=phrase_en)

@app.route('/right', methods= ['GET'])
@login_required
def right():

    french_words_objects[str(current_user.id)].is_known()
    word = french_words_objects[str(current_user.id)].current_card["word_fr"]
    word_eng = french_words_objects[str(current_user.id)].current_card["word_en"]
    card_id = french_words_objects[str(current_user.id)].current_card["id"]
    count = french_words_objects[str(current_user.id)].count
    phrase_fr = french_words_objects[str(current_user.id)].current_card["phrase_fr"]
    phrase_en = french_words_objects[str(current_user.id)].current_card["phrase_en"]
    return jsonify(word=word, word_eng=word_eng, count=count, card_id=card_id, phrase_fr=phrase_fr, phrase_en=phrase_en)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET','POST'])
def register():
    form = UserRegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        add_user()
        return redirect(url_for('home'))

    return render_template("register.html", form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again or register.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            add_user()
            return redirect(url_for('home'))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    french_words_objects.pop(str(current_user.id))
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
