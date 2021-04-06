
import pandas
import random
import os.path
from sqlalchemy import or_


my_path = os.path.abspath(os.path.dirname(__file__))
common_words_path = os.path.join(my_path, "data/5000_wordlist_french.csv")

class FrenchWords:

    def __init__(self):
            self.current_card = {}
            self.to_learn = []
            self.count = 0
            self.user_id = 0

    def load_words(self, words):

        self.to_learn = [word for word in words]
        self.next_card()
        self.count = len(self.to_learn)

    def set_id(self, user_id):
        self.user_id = user_id

    def is_known(self):

        self.to_learn.remove(self.current_card)
        self.count = len(self.to_learn)
        self.next_card()

    def next_card(self):
        self.current_card = random.choice(self.to_learn)

class LoadData:
    def __init__(self, db, Base, user_id):
            self.to_learn = []
            self.count = 0
            self.db = db
            self.Base = Base
            self.user_id = user_id

    def load_from_table(self):
        self.Base.prepare(self.db.engine, reflect=True)
        French = self.Base.classes.french_words
        Words = self.Base.classes.words_learned

        results=self.db.session.query(French).first()
        # if table is empty, load table with csv data

        if results == None:
            original_data = pandas.read_csv(common_words_path, sep=";")
            original_data.to_sql("french_words", con=self.db.engine,if_exists="append",index=False)
            self.db.session.commit()

        results = self.db.session.query(French).join(Words, French.id == Words.word_id, isouter=True).filter(or_(Words.user_id == None,Words.user_id !=self.user_id)).all()

        for result in results:
            dict = {column.name: getattr(result, column.name) for column in result.__table__.columns}
            self.to_learn.append(dict)

        self.count = len(self.to_learn)

    def save_known(self, current_card):
        self.Base.prepare(self.db.engine, reflect=True)
        Words = self.Base.classes.words_learned
        insert = Words(word_id = current_card["id"], user_id=self.user_id)
        self.db.session.add(insert)
        self.db.session.commit()
