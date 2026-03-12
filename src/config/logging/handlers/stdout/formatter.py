from pythonjsonlogger.json import JsonFormatter

from config.logging.log_properties import log_properties_registry


class CustomJsonFormatter(JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        log_properties = log_properties_registry.get()
        if log_properties:
            for key, value in log_properties.flat_dump().items():
                log_record.setdefault(key, value)
