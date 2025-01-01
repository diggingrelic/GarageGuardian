from config import LogConfig

def log(message):
    if LogConfig.DEBUG:
        print(message)