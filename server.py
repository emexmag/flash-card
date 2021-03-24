from french import FrenchWords
import speech
from flask import Flask, render_template, redirect, url_for, flash, jsonify
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import UserRegisterForm, UserLoginForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "any-secret-code-will-do")
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",  "sqlite:///french.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLES

class FrenchdbWords(db.Model):
    __tablename__ = "french_words"
    id = db.Column(db.Integer, primary_key=True)
    french = db.Column(db.String(250), unique=True, nullable=False)
    english = db.Column(db.String(250), unique=True, nullable=False)
    french_words = relationship("WordsLearned", back_populates="words")

class WordsLearned(db.Model):
    __tablename__ = "words_learned"
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('french_words.id'))
    words = relationship("FrenchdbWords", back_populates="french_words")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    learner = relationship("User", back_populates="user_words")

class User(UserMixin,db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(1000))
    user_words = relationship("WordsLearned", back_populates="learner")

db.create_all()

french_words = FrenchWords()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/card')
@login_required
def get_card():
    word = french_words.current_card["French"]
    word_eng = french_words.current_card["English"]
    count = french_words.count
    return render_template("card.html", word=word, word_eng=word_eng, count=count)

@app.route('/speaker')
@login_required
def speaker():
    word = french_words.current_card["French"]
    speech.synthesize_text_file(word)
    speech.play_word()
    return ("nothing")

@app.route('/wrong', methods= ['GET'])
@login_required
def wrong():
    french_words.next_card()
    word = french_words.current_card["French"]
    word_eng = french_words.current_card["English"]
    return jsonify(word=word, word_eng=word_eng)

@app.route('/right', methods= ['GET'])
@login_required
def right():

    french_words.is_known()
    word = french_words.current_card["French"]
    word_eng = french_words.current_card["English"]
    count = french_words.count

    return jsonify(word=word, word_eng=word_eng, count=count)

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
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
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
            return redirect(url_for('home'))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
