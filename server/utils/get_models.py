import os
from datetime import datetime

MODELS_OWNED_BY = os.getenv('MODELS_OWNED_BY', "organization-owner")


def get_models(config: object) -> list:
    """
    Get list of models from config in format of OpenAI API
    :param config:
    :return:
    """
    models = []
    now = int(datetime.utcnow().timestamp())
    for key in config['models'].keys():
        value = config['models'][key]
        model_object = {
            "id": key,
            "object": "model",
            "created": value.get('created', now),
            "owned_by": value.get('owned_by', MODELS_OWNED_BY),
        }
        models.append(model_object)
    return models


def get_model(config: object, model_name: str) -> object | None:
    """
    Get single a model by id.
    :param config:
    :return:
    """
    now = int(datetime.utcnow().timestamp())
    models = config['models'].keys()
    if model_name not in models:
        return None
    value = config['models'][model_name]
    return {
        "id": model_name,
        "object": "model",
        "created": value.get('created', now),
        "owned_by": value.get('owned_by', MODELS_OWNED_BY),
    }
