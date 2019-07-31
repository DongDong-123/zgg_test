

# test
# from copyright import Execute
from test_patent import Execute
# from test_trademarkt import Execute
# from test_one import Execute
#
# from test_clue import Execute

import os
import time
from readConfig import ReadConfig
from db import DbOperate
import random


class Operate:
    # def __init__(self):
    #     self.dboperate = DbOperate()

    def create(self):
        # from New_place_order import Execute
        # from test_one import Execute
        # from test_point import Execute
        from trademark import Execute
        # from copyright import Execute
        # self.dboperate.add(ReadConfig().get_trademake_type())
        response = Execute()

        for callback_label in range(response.__FuncCount__):
            callback = response.__Func__[callback_label]
            print("开始执行：", callback)
            response.execute_function(callback)
            self.execute_log(callback, "execute")
            time.sleep(1)
            print("{}执行完毕".format(callback))

    def execute_log(self, param, name):
        report_path = ReadConfig().save_report()
        error_log_path = os.path.join(report_path,
                                      "{}_log{}.log".format(name, time.strftime("%Y-%m-%d", time.localtime())))
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write("{}: ".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + param + "\n")

    def read_exe_log(self, path):
        with open(path, 'r', encoding="utf-8") as f:
            f.read()

    def send_clue(self):
        # from send_clue import Execute
        from test_clue import Execute

        response = Execute()
        for callback_label in range(response.__FuncCount__):
            callback = response.__Func__[callback_label]
            print("开始执行：", callback)
            response.execute_function(callback)
            self.execute_log(callback, "send_clue")
            time.sleep(1)
            print("{}发送完毕".format(callback))
            time.sleep(5)

# 删除
def delete():
    from delete_unpay_case import Execute
    test = Execute()
    num = test.get_code_num()
    for i in range(num):
        test.delete_order()
    print("删除完毕，共删除{}个".format(num))


# 随机获取类型
def random_list(num, lis):
    res = []
    for num in range(num):
        index = random.randint(34)
        res.append(lis[index])
    return res


def run():
    qq = Operate()
    qq.create()
    print("下单完毕")


def send_clue():
    all_type = ReadConfig().get_clue_type()
    # 随机数量
    num = 5
    all_type = random_list(num, all_type)
    DbOperate().add("clue", all_type)
    qq = Operate()
    qq.send_clue()
    print("线索发送完毕")


if __name__ == '__main__':
    run()
    # send_clue()
    # delete()
