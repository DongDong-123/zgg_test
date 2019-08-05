import os
import random
import time

import xlwt
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from front_login import *
from readConfig import ReadConfig
from db import DbOperate


class Common(object):
    def __init__(self):
        # 读取配置文件中的 账号密码
        self.USER = ReadConfig().get_user()
        self.PASSWORD = ReadConfig().get_password()
        # 登录
        self.driver = front_login(self.USER, self.PASSWORD)
        # self.driver = deepcopy(self.driver)
        # Excel写入
        self.row = 0
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.booksheet = self.workbook.add_sheet('Sheet1')
        self.timetemp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())  # 存储Excel表格文件名编号
        # 每个案件的数量
        self.number = 1
        self.report_path = ReadConfig().save_report()
        self.excel_number(("案件名称", "案件号", "详情页价格", "下单页价格", "下单页总价格", "支付页总价格", "价格状态"))
        # self.dboperate = DbOperate()
        self.windows = None
        # self.db = "copyright"
        self.screen_path = ReadConfig().save_screen()

    # 增加案件数量
    def number_add(self):
        if self.number > 1:
            for i in range(self.number):
                self.driver.find_element_by_xpath("//a[@class='add']").click()
        else:
            self.driver.find_element_by_xpath("//a[@class='add']").click()

    # 减少案件数量至1
    def number_minus(self):
        while self.number > 1:
            self.driver.find_element_by_xpath("//a[@class='jian']").click()

    # 执行下单
    def execute_function(self, callback):
        try:
            eval("self.{}()".format(callback))
        except Exception as e:
            print("错误信息:", e)
            self.write_error_log(callback)
            time.sleep(0.5)
            self.write_error_log(str(e))

    def write_error_log(self, info):
        error_log_path = os.path.join(self.report_path,
                                      "error_log_{}.log".format(time.strftime("%Y-%m-%d", time.localtime())))
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write("{}: ".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + info + "\n")

    # 立即申请
    def apply_now(self):
        self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()

    # 处理价格字符
    def process_price(self, price):
        if "￥" in price:
            price = price.replace("￥", '')
        return price

    # 提交订单
    def commit_order(self):
        locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
        WebDriverWait(self.driver, 30, 1).until(EC.element_to_be_clickable(locator))
        case_name = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[1]").text
        case_number = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[3]").text
        case_price = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[4]").text
        totalprice = self.driver.find_element_by_xpath("//div[@class='totalPrice']/div/b").text
        totalprice = self.process_price(totalprice)
        self.driver.find_element_by_id('lnkPay').click()
        # 返回价格
        return case_name, case_number, case_price, totalprice

    # 支付
    def pay(self, windows):
        pay_totalprice = self.driver.find_element_by_xpath("//div[@class='totalPrice']/div/b").text
        self.driver.find_element_by_id('lnkPay').click()
        self.driver.switch_to_window(windows[-1])
        self.driver.find_element_by_xpath("//div[@class='wczfBtn']/input").click()
        return self.process_price(pay_totalprice)

    # 关闭窗口
    # def closed_windows(self, num):
    #     self.windows = self.driver.window_handles
    #     self.driver.switch_to_window(self.windows[-1])
    #     self.driver.close()
    #     self.windows = self.driver.window_handles
    #     if len(self.windows) > 1:
    #         self.driver.switch_to_window(self.windows[num])
    #     else:
    #         self.driver.switch_to_window(self.windows[0])
    def closed_windows(self, num):
        self.windows = self.driver.window_handles
        for n in range(num + 1, len(self.windows)):
            self.driver.switch_to_window(self.windows[n])
            self.driver.close()
        self.windows = self.driver.window_handles
        self.driver.switch_to_window(self.windows[num])

    # 存储案件类型，案件号
    def excel_number(self, infos):
        # 获取案件名称、案件号
        if infos:
            n = 0
            for info in infos:
                self.booksheet.write(self.row, n, info)
                self.booksheet.col(n).width = 300 * 28
                n += 1
            path = os.path.join(self.report_path, "report_{}.xls".format(self.timetemp))
            self.workbook.save(path)

    # 二维码窗口截图
    def qr_shotscreen(self, name):
        current_window = self.driver.current_window_handle
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 等待二维码加载
        locator = (By.XPATH, "//canvas")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))

        path = self.screen_path
        self.driver.save_screenshot(path + self.timetemp +name + ".png")
        print("二维码截图成功")
        self.driver.switch_to_window(current_window)
