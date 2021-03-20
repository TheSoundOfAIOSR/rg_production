import json
import common.log
import pathlib as pl
from types import SimpleNamespace
from sys import argv

config_path = pl.Path(argv[0]).parent.absolute() / pl.Path("config.json")


class ConfigEncoder(json.JSONEncoder):
    """ JSONEncoder serialization class inheritant """

    def default(self, obj):
        """ Function that converts all Config objects to __dict__ """
        if isinstance(obj, SimpleNamespace):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


class Config(SimpleNamespace):

    config = None

    def __init__(self, **kwargs):
        super(Config, self).__init__(**kwargs)

    @staticmethod
    def load_config(reload: bool = False):
        """
        Function loads all kinds of .json file and converts it into class with members described by keys and their values
        Args:
        Parameters
        ----------
        reload : bool, optional
            Do you want to reload `config.js` file?

        Usage
        -----
        ...
        config = Config.load_config()
        pitchshift(..., target_sr=config.sampling_rate)
        ```
        """
        if not (config_path and config_path.exists() and config_path.is_file()):
            raise FileNotFoundError("config.js file not found")
        if Config.config and not reload:
            return Config.config
        Config.config = json.load(
            config_path.open(), object_hook=lambda data: Config(**data)
        )
        return Config.config

    def export_config(self) -> None:
        """
        Function serializes config object to .json and exports it to file
        Args:

        Usage
        -----
        ...
        config = Config.load_config()
        config.sampling_rate = 100
        config.export_config()
        ```
        """

        if not config:
            logger.error("No config object created, unable to export")
            return
        json.dump(self.config, config_path.open(mode="wt"), cls=ConfigEncoder)


if __name__ == "__main__":
    config = Config.load_config()
    print(config.saved_devices.cum)
    # config.sampling_rate = 100
    # config.export_config()
