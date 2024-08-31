import yaml
from singleton_meta import SingletonMeta


class ConfigLoader(metaclass=SingletonMeta):
    def __init__(self, config_path='src/config.yml'):
        self.config_path = config_path
        self._config = None

    def load(self):
        if self._config is None:
            with open(self.config_path, 'r') as file:
                self._config = yaml.safe_load(file)
                self.validate()  # Automatically validate after loading
        return self._config

    def validate(self):
        """Validates the configuration file."""
        required_spider_keys = {'name', 'type', 'module', 'domain'}
        if 'spiders' not in self._config:
            raise ValueError(
                "Configuration file must contain a 'spiders' section.")

        for category, spiders in self._config['spiders'].items():
            if not isinstance(spiders, list):
                raise ValueError(f"Spiders under '{category}' must be a list.")

            for spider in spiders:
                missing_keys = required_spider_keys - spider.keys()
                if missing_keys:
                    raise ValueError(f"Spider {spider.get(
                        'name', 'unknown')} is missing required keys: {missing_keys}")


if __name__ == "__main__":
    # Example usage:
    config = ConfigLoader().load()

    print(config)
