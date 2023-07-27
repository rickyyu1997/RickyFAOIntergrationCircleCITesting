import logging
import os
import platform



class CustomStreamHandler(logging.StreamHandler):

    def emit(self, record):
        message = self.format(record)
        self.stream.write(message.replace('\n', '\r') + '\n')


def init_root_logger(name):
    logging.basicConfig()
    level = logging.getLevelName(os.environ.get("LOG_LEVEL", "INFO"))

    root = logging.getLogger()
    if platform.system() != "Windows":
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)

        handler = CustomStreamHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s:%(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        root.addHandler(handler)
    root.setLevel(level)



