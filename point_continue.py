import os

class Read_log:
    def __init__(self):
        self.path = os.getcwd()

    def read(self):
        path = os.path.join(self.path, "report")
        file_list = os.listdir(path)
        aim_file = file_list[-1]
        print(aim_file)

        with open(os.path.join(path, aim_file), 'r', encoding="utf-8") as f:
            content = f.read()
            print(content, type(content))



if __name__ == "__main__":
    res = Read_log()
    res.read()