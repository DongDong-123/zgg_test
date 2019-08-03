import os
import random
import time

import xlwt
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from front_login import *
from readConfig import ReadConfig
from db import DbOperate


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
        self.case_count = FunctionName.get_count
        self.excel_number(("案件名称", "案件号", "详情页价格", "下单页价格", "下单页总价格", "支付页总价格", "价格状态"))
        self.dboperate = DbOperate()
        self.windows = None
        self.db = "copyright"
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
    def closed_windows(self, num):
        self.windows = self.driver.window_handles
        self.driver.switch_to_window(self.windows[-1])
        self.driver.close()
        self.windows = self.driver.window_handles
        if len(self.windows) > 1:
            self.driver.switch_to_window(self.windows[num])
        else:
            self.driver.switch_to_window(self.windows[0])

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

    # 计算机软件著作权登记
    def copyright_computer_software_01(self):
        all_type = [u'计算机作品著作权登记']
        type_code = ["computer"]
        for index, copyright_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(u'计算机软件著作权登记').click()
                    # 切换至新窗口
                    self.windows = self.driver.window_handles
                    self.driver.switch_to_window(self.windows[-1])
                    # 服务类型：
                    # 1-6，36个工作日-3个工作日
                    # 随机选择一个类型
                    # for num in [random.randint(range(1, 7))]:
                    for num in range(1, 3):
                        self.driver.find_element_by_xpath("//ul[@p='232']/li[{}]/a".format(num)).click()
                        # 数量加减
                        # self.number_add()
                        # self.number_minus()
                        time.sleep(0.5)
                        while not self.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.apply_now()
                        case_name, case_number, case_price, totalprice = self.commit_order()
                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.row = self.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.pay(self.windows)
                        all_info.append(pay_totalprice)
                        print(all_info, pay_totalprice)
                        if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
                                float(all_info[4]) == float(all_info[2]):
                            status = 'True'
                        else:
                            status = "False"
                        all_info.append(status)
                        self.excel_number(all_info)
                        time.sleep(1)
                        self.driver.back()
                        self.driver.back()
                        self.driver.back()
                        screen_name = "_".join([case_name, case_number, case_price])
                        self.qr_shotscreen(screen_name)
                        self.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])
                self.closed_windows(1)
        time.sleep(1)

    # 美术作品著作权登记-30日
    def copyright_art_works_01(self):
        # 选择美术作品著作权登记
        all_type = [u'美术作品著作权登记']
        type_code = ["art"]
        for index, copyright_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(copyright_type).click()
                    # 切换至新窗口
                    self.windows = self.driver.window_handles
                    self.driver.switch_to_window(self.windows[-1])
                    # 30个工作日
                    for num in range(1, 3):
                        self.driver.find_element_by_xpath("//ul[@p='107538']/li[{}]/a".format(num)).click()
                        # 数量加减
                        # self.number_add()
                        # # self.number_minus()
                        time.sleep(0.5)
                        while not self.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.apply_now()
                        case_name, case_number, case_price, totalprice = self.commit_order()

                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.row = self.row + 1
                        time.sleep(0.5)

                        pay_totalprice = self.pay(self.windows)
                        all_info.append(pay_totalprice)
                        print(all_info, pay_totalprice)
                        if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
                                float(all_info[4]) == float(all_info[2]):
                            status = 'True'
                        else:
                            status = "False"
                        all_info.append(status)
                        self.excel_number(all_info)
                        time.sleep(1)
                        self.driver.back()
                        self.driver.back()
                        self.driver.back()
                        screen_name = "_".join([case_name,case_number,case_price])
                        self.qr_shotscreen(screen_name)
                        self.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])
                self.closed_windows(1)
        time.sleep(1)

    # 文字作品著作权登记-30日
    def copyright_writings_01(self):
        # 选择文字作品著作权登记
        all_type = [u'汇编作品著作权登记', u'文字作品著作权登记', u'摄影作品著作权登记', u'电影作品著作权登记', u'音乐作品著作权登记', u'曲艺作品著作权登记']
        type_code = ["compile", "word", "photography", "film", "music", "drama"]
        for index, copyright_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(copyright_type).click()
                    # 切换至新窗口
                    self.windows = self.driver.window_handles
                    self.driver.switch_to_window(self.windows[-1])
                    # 案件类型：
                    for num in range(1, 2):
                        self.driver.find_element_by_xpath("//ul[@id='ulType']/li[{}]/a".format(num)).click()
                        # 数量加减
                        # self.number_add()
                        # # self.number_minus()
                        time.sleep(0.5)
                        while not self.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.apply_now()
                        case_name, case_number, case_price, totalprice = self.commit_order()

                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.row = self.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.pay(self.windows)
                        all_info.append(pay_totalprice)
                        print(all_info, pay_totalprice)
                        if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
                                float(all_info[4]) == float(all_info[2]):
                            status = 'True'
                        else:
                            status = "False"
                        all_info.append(status)
                        self.excel_number(all_info)

                        time.sleep(1)
                        self.driver.back()
                        self.driver.back()
                        self.driver.back()
                        screen_name = "_".join([case_name, case_number, case_price])
                        self.qr_shotscreen(screen_name)
                        self.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])
                self.closed_windows(1)
        time.sleep(1)

