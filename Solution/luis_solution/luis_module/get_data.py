import pandas as pd

class LuisData:
    def __init__(self,data_path : str):
        self.data_path = data_path
        self.df_data = None

    def load_data(self):
        self.df_data = pd.read_json(self.data_path)
        pass

    def get_data(self):
        pass

    def get_turns(self):
        pass

    def transform_data(self):
        pass

    def create_data_luis(self):
        pass
