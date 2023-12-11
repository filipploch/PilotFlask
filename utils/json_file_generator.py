import json


class JSONFileGenerator:
    def __init__(self, data):
        self.data = data

    def generate_and_save_file(self, file_name):
        try:
            with open('../static/json/' + file_name, 'w', encoding='utf-8') as json_file:
                json.dump(self.data, json_file, indent=2)
            print(f'File "{file_name}" successfully created and saved.')
        except Exception as e:
            print(f'Error: {e}')