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

    def save_screen(self):
        return self.cfg.get("path", "SCREEN_SHOOT")

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

    def get_clue_type(self):
        clue_1_1 = self.cfg.get("CLUE", "clue_1_1")
        clue_1_2 = self.cfg.get("CLUE", "clue_1_2")
        clue_1_3 = self.cfg.get("CLUE", "clue_1_3")
        clue_1_4 = self.cfg.get("CLUE", "clue_1_4")
        clue_2 = self.cfg.get("CLUE", "clue_2")
        clue_5 = self.cfg.get("CLUE", "clue_5")
        clue_5_1 = self.cfg.get("CLUE", "clue_5_1")
        all_clue_type = eval(clue_1_1)+eval(clue_1_2)+eval(clue_1_3)+eval(clue_1_4)+eval(clue_2)+eval(clue_5)+eval(clue_5_1)
        return all_clue_type


if __name__ == "__main__":
    res = ReadConfig()
    print(res.redis_host())
    print(res.redis_password())