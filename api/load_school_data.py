import json

def load_school_data(file_path='school_data.json'):
    with open(file_path, 'r') as f:
        return json.load(f)
