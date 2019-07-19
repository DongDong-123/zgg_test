import os
import random
import time

import xlwt
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from front_login import *
from readConfig import ReadConfig
from copy import deepcopy

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
        # if callback not in alread:
        # for num in range(1, 7):
        try:
            back_parm, all_info = eval("self.{}()".format(callback))
            # self.row = self.row + 1
            # time.sleep(0.5)
            # pay_totalPrice = self.pay(back_parm)
            # all_info.append(pay_totalPrice)
            # print(all_info, pay_totalPrice)
            # if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalPrice) and \
            #         float(all_info[4]) == float(all_info[2]):
            #     status = 'True'
            # else:
            #     status = "False"
            # all_info.append(status)
            # self.excel_number(all_info)
            # time.sleep(1)
            # self.driver.back()
            # self.driver.back()
            # self.driver.back()
            # time.sleep(2)
            # self.closed_windows()
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
        totalPrice = self.driver.find_element_by_xpath("//div[@class='totalPrice']/div/b").text
        totalPrice = self.process_price(totalPrice)
        self.driver.find_element_by_id('lnkPay').click()
        # 返回价格
        return case_name, case_number, case_price, totalPrice

    # 支付
    def pay(self, windows):
        pay_totalPrice = self.driver.find_element_by_xpath("//div[@class='totalPrice']/div/b").text
        self.driver.find_element_by_id('lnkPay').click()
        self.driver.switch_to_window(windows[-1])
        self.driver.find_element_by_xpath("//div[@class='wczfBtn']/input").click()
        return self.process_price(pay_totalPrice)

    # 关闭窗口
    def closed_windows(self):
        self.driver.close()
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        self.driver.close()
        self.driver.switch_to_window(windows[0])

    # 删除未支付订单
    def delete_order(self):
        self.driver.get("{}/user/casemanage.html?state=1".format(ReadConfig().get_user_url()))
        locator = (By.LINK_TEXT, u'删除')
        # 等待页面加载完毕
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        # 读取订单号
        order_number = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[1]/span[1]").text
        # 多个案件一个订单，只获取到了第一个案件号
        case_name = self.driver.find_element_by_xpath("//tr/td[@class='case-mess']/span[1]").text
        case_number = self.driver.find_element_by_xpath("//tr/td[@class='case-mess']/span[3]").text

        print("order_number", order_number)
        print("case_info", case_name)
        print("case_info", case_number)
        self.driver.find_element_by_link_text(u"删除").click()
        self.driver.find_element_by_link_text(u"确定").click()
        # 必须等一会，才能获取弹框
        sleep(0.5)
        # 关闭弹框
        aler = self.driver.switch_to.alert
        delete_staus = aler.text
        print('delete_staus', delete_staus)
        aler.accept()
        # 存储
        self.row = self.row + 1
        self.save_delete_case((order_number, case_name, case_number, delete_staus))

        # self.driver.refresh()  # 刷新页面

    # 储存删除记录，同一订单多个案件，只存储第一个
    def save_delete_case(self, infos):
        # 获取案件名称、案件号
        n = 0
        for elem in infos:
            self.booksheet.write(self.row, n, elem)
            self.booksheet.col(n).width = 300 * 28
            n += 1
        path = os.path.join(self.report_path, "delete_{}.xls".format(self.timetemp))
        self.workbook.save(path)

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

    def copyright_computer_software_01(self):
        # 选择计算机软件著作权登记
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'计算机软件著作权登记').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型：
        # 1-6，36个工作日-3个工作日
        for num in range(1, 7):
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
            case_name, case_number, case_price, totalPrice = self.commit_order()
            # yield windows, [case_name, case_number, detail_price, case_price, totalPrice]
            all_info = [case_name, case_number, detail_price, case_price, totalPrice]
            self.row = self.row + 1
            time.sleep(0.5)
            pay_totalPrice = self.pay(windows)
            all_info.append(pay_totalPrice)
            print(all_info, pay_totalPrice)
            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalPrice) and \
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

    # 99 美术作品著作权登记-30日
    def copyright_art_works_01(self):
        # 选择美术作品著作权登记
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'美术作品著作权登记').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型：
        # 30个工作日
        for num in range(1, 7):
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
            case_name, case_number, case_price, totalPrice = self.commit_order()
            # return windows, [case_name, case_number, detail_price, case_price, totalPrice]

            all_info = [case_name, case_number, detail_price, case_price, totalPrice]
            self.row = self.row + 1
            time.sleep(0.5)
            pay_totalPrice = self.pay(windows)
            all_info.append(pay_totalPrice)
            print(all_info, pay_totalPrice)
            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalPrice) and \
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

        # 105 文字作品著作权登记-30日

    def copyright_writings_01(self):
        # 选择文字作品著作权登记
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'文字作品著作权登记').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 案件类型：
        for num in range(1, 7):
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
            case_name, case_number, case_price, totalPrice = self.commit_order()
            # return windows, [case_name, case_number, detail_price, case_price, totalPrice]

            all_info = [case_name, case_number, detail_price, case_price, totalPrice]
            self.row = self.row + 1
            time.sleep(0.5)
            pay_totalPrice = self.pay(windows)
            all_info.append(pay_totalPrice)
            print(all_info, pay_totalPrice)
            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalPrice) and \
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

    # 106 汇编作品著作权登记-30日
    def copyright_compilation_01(self):
        # 选择汇编作品著作权登记
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'汇编作品著作权登记').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 案件类型：
        for num in range(1, 7):
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
            case_name, case_number, case_price, totalPrice = self.commit_order()
            # return windows, [case_name, case_number, detail_price, case_price, totalPrice]

            all_info = [case_name, case_number, detail_price, case_price, totalPrice]
            self.row = self.row + 1
            time.sleep(0.5)
            pay_totalPrice = self.pay(windows)
            all_info.append(pay_totalPrice)
            print(all_info, pay_totalPrice)
            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalPrice) and \
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

    # 107 摄影作品著作权登记-30日
    def copyright_photography_01(self):
        # 选择摄影作品著作权登记
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'摄影作品著作权登记').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 案件类型：
        for num in range(1, 7):
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
            case_name, case_number, case_price, totalPrice = self.commit_order()
            # return windows, [case_name, case_number, detail_price, case_price, totalPrice]

            all_info = [case_name, case_number, detail_price, case_price, totalPrice]
            self.row = self.row + 1
            time.sleep(0.5)
            pay_totalPrice = self.pay(windows)
            all_info.append(pay_totalPrice)
            print(all_info, pay_totalPrice)
            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalPrice) and \
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

    # 108 电影作品著作权登记-30日
    def copyright_movie_works_01(self):
        # 选择电影作品著作权登记
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'电影作品著作权登记').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 案件类型：
        for num in range(1, 7):
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
            case_name, case_number, case_price, totalPrice = self.commit_order()
            # return windows, [case_name, case_number, detail_price, case_price, totalPrice]

            all_info = [case_name, case_number, detail_price, case_price, totalPrice]
            self.row = self.row + 1
            time.sleep(0.5)
            pay_totalPrice = self.pay(windows)
            all_info.append(pay_totalPrice)
            print(all_info, pay_totalPrice)
            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalPrice) and \
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

    # 109 音乐作品著作权登记-30日
    def copyright_music_works_01(self):
        # 选择音乐作品著作权登记
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'音乐作品著作权登记').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 案件类型：
        for num in range(1, 7):

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
            case_name, case_number, case_price, totalPrice = self.commit_order()
            # return windows, [case_name, case_number, detail_price, case_price, totalPrice]

            all_info = [case_name, case_number, detail_price, case_price, totalPrice]
            self.row = self.row + 1
            time.sleep(0.5)
            pay_totalPrice = self.pay(windows)
            all_info.append(pay_totalPrice)
            print(all_info, pay_totalPrice)
            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalPrice) and \
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

    # 110 曲艺作品著作权登记-30日
    def copyright_quyi_works_01(self):
        # 选择曲艺作品著作权登记
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'曲艺作品著作权登记').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 案件类型：
        for num in range(1, 7):

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
            case_name, case_number, case_price, totalPrice = self.commit_order()
            # return windows, [case_name, case_number, detail_price, case_price, totalPrice]

            all_info = [case_name, case_number, detail_price, case_price, totalPrice]
            self.row = self.row + 1
            time.sleep(0.5)
            pay_totalPrice = self.pay(windows)
            all_info.append(pay_totalPrice)
            print(all_info, pay_totalPrice)
            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalPrice) and \
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
