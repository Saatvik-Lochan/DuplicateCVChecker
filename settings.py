import json


class Settings:

    def __init__(self, download_folder_path="",
                 database_folder_path="",
                 default_check_level=75,
                 auto_download_summary=False,
                 include_dev_values=False,
                 csv=False):
        self.download_folder_path = download_folder_path
        self.database_folder_path = database_folder_path
        self.default_check_level = default_check_level
        self.auto_download_summary = auto_download_summary
        self.include_dev_values = include_dev_values
        self.csv = csv

    def json_serialise(self, json_file="settings.json"):
        json_dict = {'download_folder_path': self.download_folder_path,
                     'database_folder_path': self.database_folder_path,
                     'default_check_level': self.default_check_level,
                     'auto_download_summary': self.auto_download_summary,
                     'include_dev_values': self.include_dev_values,
                     'csv': self.csv}

        with open(json_file, "w") as file:
            json.dump(json_dict, file)

    def json_deserialise(self, json_file="settings.json"):
        with open(json_file, "r") as file:
            json_str = file.read()
        json_dict = json.loads(json_str)
        self.download_folder_path = json_dict['download_folder_path']
        self.database_folder_path = json_dict['database_folder_path']
        self.default_check_level = json_dict['default_check_level']
        self.auto_download_summary = json_dict['auto_download_summary']
        self.include_dev_values = json_dict['include_dev_values']
        self.csv = json_dict['csv']
