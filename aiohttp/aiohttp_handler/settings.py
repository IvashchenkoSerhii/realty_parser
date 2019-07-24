import logging
import yaml


FORMAT = '[%(asctime)s] %(levelname)s %(module)s:%(lineno)d %(message)s'
logging.basicConfig(format=FORMAT)

log = logging.getLogger('app')
log.setLevel(logging.DEBUG)


def get_config(CONFIG_ROOT, config_filename):
    with open(CONFIG_ROOT / 'config_base.yaml') as ymlfile:
        config_base = yaml.load(ymlfile, Loader=yaml.FullLoader)

    if config_filename == 'config_base.yaml':
        return config_base

    with open(CONFIG_ROOT / config_filename) as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)
    for key in config_base:
        if config.get(key):
            if isinstance(config[key], dict):
                config_base[key].update(config[key])
            else:
                config_base[key] = config[key]
    return config_base
