class FileReader:
    @staticmethod
    def execute(file_path: str):
        with open(file_path, "r") as file:
            content = file.read()

        return content
