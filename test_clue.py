import os
import random
import time

import xlwt
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from front_login import *
from readConfig import ReadConfig

driver = webdriver.Chrome()
driver.maximize_window()
driver.get(ReadConfig().get_root_url())


class FunctionName(type):
    def __new__(cls, name, bases, attrs, *args, **kwargs):
        count = 0
        attrs["__Func__"] = []
        for k, v in attrs.items():
            # 专利
            if "patent_" in k:
                attrs["__Func__"].append(k)
                count += 1
            # 商标
            elif "trademark_" in k:
                attrs["__Func__"].append(k)
                count += 1
            # 版权
            elif "copyright_" in k:
                attrs["__Func__"].append(k)
                count += 1
            elif "highnew_" in k:
                attrs["__Func__"].append(k)
                count += 1

            elif "taocan_" in k:
                attrs["__Func__"].append(k)
                count += 1

        attrs["__FuncCount__"] = count
        return type.__new__(cls, name, bases, attrs)

    def get_count(cls):
        pass


class Execute(object, metaclass=FunctionName):
    def __init__(self):
        # 读取配置文件中的 账号密码
        self.USER = ReadConfig().get_user()
        self.PASSWORD = ReadConfig().get_password()
        # 登录
        self.driver = driver
        # self.driver = front_login(self.USER, self.PASSWORD)
        # Excel写入
        self.row = 0
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.booksheet = self.workbook.add_sheet('Sheet1')
        self.timetemp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())  # 存储Excel表格文件名编号
        # 每个案件的数量
        self.number = 1
        self.report_path = ReadConfig().save_report()
        self.case_count = FunctionName.get_count
        self.phone = 16619923387
        self.file_name = self.save_clue_log(("手机号", "线索内容", "发送状态", "其他"))


    def execute_function(self, callback):
        try:
            back_parm = eval("self.{}()".format(callback))
            # self.save_clue_log(eval("self.{}()".format(callback)))
            # for elem in eval("self.{}()".format(callback)):
            #     print("elem:", elem)
            self.row = self.row + 1
            self.save_clue_log(back_parm)
            # time.sleep(0.5)
            time.sleep(0.5)

        except Exception as e:
            print("错误信息:", e)
            print("e的类型", type(e))
            self.write_error_log(callback)
            time.sleep(0.5)
            self.write_error_log(str(e))

    def write_error_log(self, info):
        error_log_path = os.path.join(self.report_path,
                                      "error_log_{}.log".format(time.strftime("%Y-%m-%d", time.localtime())))
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write("{}: ".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + info + "\n")

    def open_windows(self):
        drivers = webdriver.Chrome()
        drivers.maximize_window()
        drivers.get(ReadConfig().get_root_url())
        return drivers

    def save_clue_log(self, args):
        # 获取案件名称、案件号
        # self.booksheet.write(self.row, 0, row1)
        # self.booksheet.write(self.row, 1, row2)
        if args:
            n = 0
            # self.booksheet.write(self.row, n, n + 1)
            # n += 1
            for elem in args:
                self.booksheet.write(self.row, n, elem)
                self.booksheet.col(n).width = 300 * 28
                n += 1

        # self.booksheet.write(self.row, 3, row4)
        # first_col = self.booksheet.col(0)
        # sec_col = self.booksheet.col(1)
        # third_col = self.booksheet.col(2)
        # fouth_col = self.booksheet.col(3)
        # first_col.width = 250 * 28
        # sec_col.width = 300 * 28
        # third_col.width = 300 * 28
        # fouth_col.width = 150 * 28
        path = os.path.join(self.report_path, "clue_{}.xls".format(self.timetemp))
        self.workbook.save(path)


    # 关闭窗口
    def closed_windows(self):
        self.driver.close()
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        self.driver.close()
        self.driver.switch_to_window(windows[0])

    def check_rasult(self):
        result = self.driver.find_element_by_xpath("(.//div[@class='them-edit-dialog']/div[@class='comm']/p)").text
        print("result", result, type(result))
        if "您的查询资料已提交" in result:
            res = "True"
        else:
            res = "False"
        return res

    # 软件开发
    def patent_clue_36(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'软件开发').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 随机选择一个类型
        num = random.randint(1, 5)
        text = "软件开发需求"
        self.driver.find_element_by_class_name("soft-textarea").send_keys(text)
        # demand = self.driver.find_element_by_xpath("(.//textarea)").text

        self.driver.find_element_by_xpath("(.//ul[@class='soft-optaion fl']/label[{}]/li)".format(num)).click()
        time.sleep(0.5)
        price = self.driver.find_element_by_xpath("(.//ul[@class='soft-optaion fl']/label[{}]/li)".format(num)).text
        time.sleep(0.5)

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']//h3)").text
        self.driver.find_element_by_id("yourphone").send_keys(self.phone)
        self.driver.find_element_by_id("yourname").send_keys(case_name + text + "-" + price)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # result = self.driver.find_element_by_link_text(u'您的查询资料已提交， 顾问会尽快电话告诉您查询结果')

        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res, text, price)

    # 研发立项支持
    def patent_clue_02(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'研发立项支持').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 您的查询资料已提交， 顾问会尽快电话告诉您查询结果
        # result = self.driver.find_element_by_link_text(u'您的查询资料已提交， 顾问会尽快电话告诉您查询结果')

        # class ="them-edit-dialog"
        # result = self.driver.find_element_by_xpath("(.//div[@class='them-edit-dialog']/div[@class='comm']/p)").text
        # print("result", result, type(result))

        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)


if __name__ == "__main__":
    temp = Execute()
    for callback_label in range(temp.__FuncCount__):
        callback = temp.__Func__[callback_label]
        print("开始执行：", callback)
        temp.execute_function(callback)
        print("{}执行完毕".format(callback))
