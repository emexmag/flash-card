
import pandas
import random
import os.path
from sqlalchemy import or_


my_path = os.path.abspath(os.path.dirname(__file__))
words_to_learn_path = os.path.join(my_path, "data/words_to_learn.csv")
common_words_path = os.path.join(my_path,"data/french_1000_common.csv")


class FrenchWords:

    def __init__(self, db, Base):
            self.current_card = {}
            self.to_learn = []
            self.count=0
            self.db=db
            self.Base = Base
            self.user_id = 0

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
        print(self.user_id)
        results = self.db.session.query(French).join(Words, French.id == Words.word_id, isouter=True).filter(or_(Words.user_id == None,Words.user_id !=self.user_id)).all()
        print(results)
        for result in results:
            dict = {column.name: getattr(result, column.name) for column in result.__table__.columns}
            self.to_learn.append(dict)

        self.next_card()
        self.count = len(self.to_learn)
        print(self.to_learn)

    def set_id(self,id):
        self.user_id = id

    def is_known(self):
        self.Base.prepare(self.db.engine, reflect=True)
        Words = self.Base.classes.words_learned

        insert = Words(word_id = self.current_card["id"], user_id=self.user_id)
        self.db.session.add(insert)
        self.db.session.commit()
        self.to_learn.remove(self.current_card)
        self.count = len(self.to_learn)
        self.next_card()

    def next_card(self):
        self.current_card = random.choice(self.to_learn)


