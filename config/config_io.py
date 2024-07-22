import json
class configIO:
    def __init__(self) -> None:
        pass
    def load_config(self,file_path:str):
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    def write_config(self,file_path,data):
        with open(file_path, 'w') as config_file:
            json.dump(data, config_file)
    def change_config(self,file_path,key,change_data):
        data = self.load_config(file_path)
        data[key] = change_data
        self.write_config(file_path,data)
