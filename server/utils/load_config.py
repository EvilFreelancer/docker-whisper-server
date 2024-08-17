import yaml


def load_config(filename: str) -> object:
    file = open(filename).read()
    return yaml.safe_load(file)
