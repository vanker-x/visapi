# Created by vank
# DateTime: 2022/10/28-17:33
# Encoding: UTF-8
import logging.config

DEFAULT = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        'default': {
            'format': "%(levelname)s-[%(asctime)s (%(module)s:%(lineno)d)] - %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
        "server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "console": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "server": {
            "handlers": ["server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def setup_config(user_log):
    """
    :param user_log: log配置
    """
    logging.config.dictConfig(DEFAULT)
    if isinstance(user_log, dict) and user_log:
        logging.config.dictConfig(user_log)
