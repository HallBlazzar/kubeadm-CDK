import json


class ConfigLoader:
    def __init__(self, config_path: str):
        self.__config_path = config_path

    def fetch_config_from_json_file(self) -> dict:
        with open(self.__config_path, "r") as config_file:
            config = json.load(config_file)

        return config
