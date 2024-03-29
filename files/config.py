import os
import yaml
from mystuff.functions import generated_data_dir
from datetime import datetime as dt



class BaseModelConfigs:
    def __init__(self):
        self.model_path = None

    def serialize(self):
        class_attributes = {key: value
                            for (key, value)
                            in type(self).__dict__.items()
                            if key not in ['__module__', '__init__', '__doc__', '__annotations__']}
        instance_attributes = self.__dict__

        # first init with class attributes then apply instance attributes overwriting any existing duplicate attributes
        all_attributes = class_attributes.copy()
        all_attributes.update(instance_attributes)

        return all_attributes

    def save(self, name: str = "configs.yaml"):
        if self.model_path is None:
            raise Exception("Model path is not specified")

        # create directory if not exist
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        with open(os.path.join(self.model_path, name), "w") as f:
            yaml.dump(self.serialize(), f)

    @staticmethod
    def load(configs_path: str):
        with open(configs_path, "r") as f:
            configs = yaml.load(f, Loader=yaml.FullLoader)

        config = BaseModelConfigs()
        for key, value in configs.items():
            setattr(config, key, value)

        return config


class ModelConfigs(BaseModelConfigs):
    def __init__(self):
        self.model_path = os.path.join(generated_data_dir(), dt.strftime(dt.now(), "%Y%m%d%H%M"))
        self.vocab = ""
        self.height = 32
        self.width = 128
        self.max_text_length = 0
        self.batch_size = 64
        self.learning_rate = 0.002
        self.train_epochs = 1000



