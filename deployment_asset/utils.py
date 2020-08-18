from jinja2 import Template
from tempfile import NamedTemporaryFile
from utils.file_reader import FileReader


class KubeadmConfigCreator:
    def __init__(self, kubeadm_config_template_path: str, token_path: str):
        self.__kubeadm_config_template_path = kubeadm_config_template_path
        self.__token = FileReader().execute(token_path)

    def execute(self):
        kubeadm_config_template = self.__load_kubeadm_config_template()
        kubeadm_config = kubeadm_config_template.render(TOKEN=self.__token)
        return self.__write_kubeadmin_config_to_tempfile(kubeadm_config)

    def __load_kubeadm_config_template(self):
        with open(self.__kubeadm_config_template_path, 'r') as file:
            kubeadm_config_template = Template(file.read())

        return kubeadm_config_template

    def __write_kubeadmin_config_to_tempfile(self, kubeadm_config: str):
        with NamedTemporaryFile(mode="w", delete=False) as file:
            file.write(kubeadm_config)

        return file.name
