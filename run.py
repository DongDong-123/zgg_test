

# test
# from test_copyright import Execute
# from test_patent import Execute
# from test_trademarkt import Execute
# from test_one import Execute
#
# from test_clue import Execute

import os
import time
from readConfig import ReadConfig


class Operate:

    def create(self):
        # from New_place_order import Execute
        from test_one import Execute

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
        from send_clue import Execute
        # from test_clue import Execute
        response = Execute()
        for callback_label in range(response.__FuncCount__):
            callback = response.__Func__[callback_label]
            print("开始执行：", callback)
            response.execute_function(callback)
            self.execute_log(callback, "send_clue")
            time.sleep(1)
            print("{}发送完毕".format(callback))

def run():
    qq = Operate()
    qq.create()
    # print("线索发送完毕")
    # qq.send_clue()


if __name__ == '__main__':
    run()
