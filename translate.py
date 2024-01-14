import requests
import yaml
import pandas as pd

class Translator():
    def __init__(self,config_path,target):
        self.config_path = config_path
        self.target = target
        self.config = self.load_api_key()
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
    def load_api_key(self):
        try:
            with open(self.config_path, 'r') as config_file:
                config = yaml.safe_load(config_file)
                return config['API_KEY']
        except FileNotFoundError:
            print(f"Config file not found at {self.config_path}")
            return None
        except yaml.YAMLError as e:
            print(f"Error parsing YAML in {self.config_path}: {e}")
            return None
    def detect_language(self, query):
        url = f"{self.base_url}/detect"
        payload = {
            'q' : query,
            'key' : self.config
        }
        response = requests.post(url = url, data = payload).json()
        result = response['data']
        languages = [detection[0]['language'] for detection in result['detections'] if detection]
        return ",".join(languages)

    def code_to_language(self,lang_code):
        df = pd.read_csv('languages.csv')
        try:
            result = df.loc[df['Code'] == lang_code]['Language'].iloc[0]
            return result
        except IndexError:
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def translate(self,string):
        url = self.base_url
        payload = {
            'q' : string,
            'key' : self.config,
            'target' : self.target
        }
        response = requests.post(url = url, data = payload).json()
        data = response['data']
        translations_info = [(translation['translatedText'], translation['detectedSourceLanguage']) for translation in data.get('translations', [])]
        if translations_info:
            translated_texts, source_languages = zip(*translations_info)
            full_source = []
            for i in source_languages:
                full_source.append(self.code_to_language(i)) 
            translated_texts_str = ', '.join(translated_texts)
            source_languages_str = ', '.join(full_source)
        return translated_texts_str, source_languages_str

if __name__ == "__main__":
    ins = Translator(config_path = "/Users/pavan/MyProjects/Translator Bot/config.yaml",target = 'te')
    query = input("Enter Sentence: ")
    detected_language = ins.detect_language(query)
    print(f"Source: {detected_language}") 
    translation,source = ins.translate(query)
    print(f"{translation} (from {source})")  


