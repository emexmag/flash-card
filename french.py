
import pandas
import random

class FrenchWords:

    def __init__(self):
            self.current_card = {}
            self.to_learn = {}
            self.count=0
            self.load_data()


    def load_data(self):
        try:
            data = pandas.read_csv("data/words_to_learn.csv")
        except FileNotFoundError:
            original_data = pandas.read_csv("data/french_1000_common.csv", sep=";")
            self.to_learn = original_data.to_dict(orient="records")
        else:
            self.to_learn = data.to_dict(orient="records")
        finally:
            self.next_card()
            self.count = len(self.to_learn)

    def is_known(self):
        self.to_learn.remove(self.current_card)
        data = pandas.DataFrame(self.to_learn)
        data.to_csv("data/words_to_learn.csv", index=False)
        self.count = len(self.to_learn)
        self.next_card()
        return

    def next_card(self):
        self.current_card = random.choice(self.to_learn)


