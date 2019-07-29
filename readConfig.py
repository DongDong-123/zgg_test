import configparser
import os

curPath = os.path.dirname(os.path.realpath(__file__))
cfgPath = os.path.join(curPath, "config.ini")


class ReadConfig:
    def __init__(self):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(cfgPath, encoding='utf-8')

    def get_user(self):
        return self.cfg.get("account", "USER")

    def get_password(self):
        return self.cfg.get("account", "PASSWORD")

    def save_report(self):
        return self.cfg.get("path", "REPORT")

    def get_root_url(self):
        return self.cfg.get("URL", "URL")

    def get_user_url(self):
        return self.cfg.get("URL", "USER_URL")

    def redis_host(self):
        return self.cfg.get("REDIS", "HOST")

    def redis_password(self):
        return self.cfg.get("REDIS", "PASSWORD")

    def get_trademake_type(self):
        return self.cfg.get("TRADEMARK", "trademark_international")


if __name__ == "__main__":
    res = ReadConfig()
    print(res.redis_host())
    print(res.redis_password())