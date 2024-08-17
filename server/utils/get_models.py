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
