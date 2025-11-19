import logging
from fluent import handler

def initialize_logging(fluentd_host: str,
                       fluentd_port:int,
                       service_name: str):
    logger = logging.getLogger("affect_pulse")
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fluent_handler = handler.FluentHandler(
        'affect_pulse',
        host=fluentd_host,
        port=fluentd_port,
    )
    formatter = handler.FluentRecordFormatter({
        'message': '%(message)s',
        'level': '%(levelname)s',
        'servicename': service_name,
    })
    fluent_handler.setFormatter(formatter)
    logger.addHandler(fluent_handler)
