# -*- coding: utf-8 -*-
# @Time    : 2019/4/12 20:08
# @Author  : Wu_xiaokai
# @Email   : wuxiaokai@zgg.com

import time, random
from selenium.webdriver.common.action_chains import ActionChains
from front_login import *
from selenium.webdriver.support.ui import WebDriverWait
import xlrd, xlwt
from readConfig import ReadConfig
import os
from selenium.webdriver.common.keys import Keys


# class Function:
#     def __init__(self):
#         # 读取配置文件中的 账号密码
#         self.USER = ReadConfig().get_user()
#         self.PASSWORD = ReadConfig().get_password()
#         # 登录
#         self.driver = front_login(self.USER, self.PASSWORD)
#         # Excel写入
#         self.row = 0
#         self.workbook = xlwt.Workbook(encoding='utf-8')
#         self.booksheet = self.workbook.add_sheet('Sheet1')
#         self.timetemp = round(time.time())  # 存储Excel表格文件名编号
#         # 每个案件的数量
#         self.number = 1
#         self.report_path = ReadConfig().save_report()
#
#
#     # 增加案件数量
#     def number_add(self):
#         if self.number > 1:
#             for i in range(self.number):
#                 self.driver.find_element_by_xpath("//a[@class='add']").click()
#         else:
#             self.driver.find_element_by_xpath("//a[@class='add']").click()
#
#     # 减少案件数量至1
#     def number_minus(self):
#         while self.number > 1:
#             self.driver.find_element_by_xpath("//a[@class='jian']").click()
#
#     # 执行下单
#     def execute_function(self, callback):
#         try:
#             back_parm = eval("self.{}()".format(callback))
#             self.row = self.row + 1
#             self.pay(back_parm)
#             self.closed_windows()
#         except Exception as e:
#             print("错误信息:", e)
#
#     # 记录错误日志
#     def write_error_log(self, error):
#         error_log_path = os.path.join(self.report_path,
#                                       "error_log{}.log".format(time.strftime("%Y-%m-%d", time.localtime())))
#         with open(error_log_path, "a", encoding="utf-8") as f:
#             f.write(error)
#
#     # 立即申请
#     def apply_now(self):
#         self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()
#
#     # 提交订单
#     def commit_order(self):
#         locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
#         WebDriverWait(self.driver, 30, 1).until(EC.element_to_be_clickable(locator))
#         self.excel_number()
#         self.driver.find_element_by_id('lnkPay').click()
#
#     # 支付
#     def pay(self, windows):
#         self.driver.find_element_by_id('lnkPay').click()
#         self.driver.switch_to_window(windows[-1])
#         self.driver.find_element_by_xpath("//div[@class='wczfBtn']/input").click()
#
#     # 关闭窗口
#     def closed_windows(self):
#         self.driver.close()
#         windows = self.driver.window_handles
#         self.driver.switch_to_window(windows[-1])
#         self.driver.close()
#         self.driver.switch_to_window(windows[0])
#
#     # 删除未支付订单
#     def delete_order(self):
#         self.driver.get("{}/user/casemanage.html?state=1".format(ReadConfig().get_user_url()))
#         locator = (By.LINK_TEXT, u'删除')
#         # 等待页面加载完毕
#         WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
#         # 读取订单号
#         order_number = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[1]/span[1]").text
#         # 多个案件一个订单，只获取到了第一个案件号
#         case_name = self.driver.find_element_by_xpath("//tr/td[@class='case-mess']/span[1]").text
#         case_number = self.driver.find_element_by_xpath("//tr/td[@class='case-mess']/span[3]").text
#
#         print("order_number", order_number)
#         print("case_info", case_name)
#         print("case_info", case_number)
#         self.driver.find_element_by_link_text(u"删除").click()
#         self.driver.find_element_by_link_text(u"确定").click()
#         # 必须等一会，才能获取弹框
#         sleep(0.5)
#         # 关闭弹框
#         aler = self.driver.switch_to.alert
#         delete_staus = aler.text
#         print('delete_staus', delete_staus)
#         aler.accept()
#         # 存储
#         self.save_delete_case(order_number, case_name, case_number, delete_staus)
#         self.row = self.row + 1
#         # self.driver.refresh()  # 刷新页面
#
#     # 储存删除记录，同一订单多个案件，只存储第一个
#     def save_delete_case(self, row1, row2, row3, row4):
#         # 获取案件名称、案件号
#         self.booksheet.write(self.row, 0, row1)
#         self.booksheet.write(self.row, 1, row2)
#         self.booksheet.write(self.row, 2, row3)
#         self.booksheet.write(self.row, 3, row4)
#         first_col = self.booksheet.col(0)
#         sec_col = self.booksheet.col(1)
#         third_col = self.booksheet.col(2)
#         fouth_col = self.booksheet.col(3)
#         first_col.width = 250 * 28
#         sec_col.width = 300 * 28
#         third_col.width = 300 * 28
#         fouth_col.width = 150 * 28
#         path = os.path.join(self.report_path, "delete_{}.xls".format(self.timetemp))
#         self.workbook.save(path)
#
#     # 存储案件类型，案件号
#     def excel_number(self):
#         # 获取案件名称、案件号
#         case_name = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[1]").text
#         case_number = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[3]").text
#         case_price = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[4]").text
#         self.booksheet.write(self.row, 0, case_name)
#         self.booksheet.write(self.row, 1, case_number)
#         self.booksheet.write(self.row, 2, case_price)
#         first_col = self.booksheet.col(0)
#         sec_col = self.booksheet.col(1)
#         third_col = self.booksheet.col(2)
#         first_col.width = 300 * 28
#         sec_col.width = 300 * 28
#         third_col.width = 100 * 28
#         path = os.path.join(self.report_path, "report_{}.xls".format(self.timetemp))
#         self.workbook.save(path)


class FunctionName(type):

    def __new__(cls, name, bases, attrs, *args, **kwargs):
        count = 0
        attrs["__Func__"] = []
        for k, v in attrs.items():
            # print("k", k)
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

        attrs["__FuncCount__"] = count
        return type.__new__(cls, name, bases, attrs)


class Execute(object, FunctionName):
    def __init__(self):
        # 读取配置文件中的 账号密码
        self.USER = ReadConfig().get_user()
        self.PASSWORD = ReadConfig().get_password()
        # 登录
        self.driver = front_login(self.USER, self.PASSWORD)
        self.row = 0
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.booksheet = self.workbook.add_sheet('Sheet1')
        self.timetemp = round(time.time())
        self.report_path = ReadConfig().save_report()

    def get_function_name(self, callback):
        print("===================11=====================")
        back_parm = eval("self.{}()".format(callback))
        print("callback:", callback)
        print("===================22=====================")
        self.row = self.row + 1
        self.pay(back_parm)
        # 如果不关闭窗口，需要切换tab到首页
        self.closed_windows()
        print("===========================3===================")

    # 删除订单
    # def delete_order(self):
    #     self.driver.get("https://user.zgg.com/user/casemanage.html?state=1")
    #     locator = (By.LINK_TEXT, u'删除')
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #
    #     self.driver.find_element_by_link_text(u"删除").click()
    #     self.driver.find_element_by_link_text(u"确定").click()
    #     # 必须等一会，才能获取弹框
    #     sleep(0.5)
    #
    #     # 关闭弹框
    #     aler = self.driver.switch_to.alert
    #     print('ces',aler.text)
    #     aler.accept()
    #     # self.driver.refresh()
    #     # sleep(3)
    #


    # 通用立即申请
    def apply_now(self):
        self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()

    # 提交订单
    def commit_order(self):
        locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
        WebDriverWait(self.driver, 30, 1).until(EC.element_to_be_clickable(locator))
        self.excel_number()
        self.driver.find_element_by_id('lnkPay').click()

    # 支付
    def pay(self, windows):
        self.driver.find_element_by_id('lnkPay').click()
        self.driver.switch_to_window(windows[-1])
        self.driver.find_element_by_xpath("//div[@class='wczfBtn']/input").click()

    # 关闭窗口
    def closed_windows(self):
        self.driver.close()
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        self.driver.close()
        self.driver.switch_to_window(windows[0])

    def excel_number(self):
        # 获取案件名称、案件号
        case_name = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[1]").text
        case_number = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[3]").text
        case_price = self.driver.find_element_by_xpath("//tr[@class='tr-comm']/td[4]").text
        self.booksheet.write(self.row, 0, case_name)
        self.booksheet.write(self.row, 1, case_number)
        self.booksheet.write(self.row, 2, case_price)
        first_col = self.booksheet.col(0)
        sec_col = self.booksheet.col(1)
        third_col = self.booksheet.col(2)
        first_col.width = 300 * 28
        sec_col.width = 300 * 28
        third_col.width = 100 * 28
        path = os.path.join(self.report_path, "report_{}.xls".format(self.timetemp))
        self.workbook.save(path)

    # 删除未支付订单
    def delete_order(self):
        self.driver.get("https://user.zgg.com/user/casemanage.html?state=1")
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
        print("case_info2", case_number)
        self.driver.find_element_by_link_text(u"删除").click()
        self.driver.find_element_by_link_text(u"确定").click()
        # 必须等一会，才能获取弹框
        sleep(0.5)
        # 关闭弹框
        aler = self.driver.switch_to.alert
        delete_staus = aler.text
        print('ces', aler.text)
        aler.accept()
        self.save_delete_case(order_number, case_name, case_number,delete_staus)
        self.row = self.row + 1
        # self.driver.refresh()  # 刷新页面

    def save_delete_case(self, row1, row2, row3, row4):
        # 获取案件名称、案件号
        self.booksheet.write(self.row, 0, row1)
        self.booksheet.write(self.row, 1, row2)
        self.booksheet.write(self.row, 2, row3)
        self.booksheet.write(self.row, 3, row4)
        first_col = self.booksheet.col(0)
        sec_col = self.booksheet.col(1)
        third_col = self.booksheet.col(2)
        fouth_col = self.booksheet.col(3)
        first_col.width = 250 * 28
        sec_col.width = 300 * 28
        third_col.width = 300 * 28
        fouth_col.width = 150 * 28
        path = os.path.join(self.report_path, "delete_{}.xls".format(self.timetemp))
        self.workbook.save(path)

    # 1 发明专利-标准服务
    def patent_invention_normal(self):
        # 选择发明专利
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'发明专利').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # 数量加1
        # self.driver.find_element_by_xpath("//a[@class='add']").click()
        # 数量减1
        # self.driver.find_element_by_xpath("//a[@class='jian']").click()

        # 立即申请
        self.apply_now()
        # 提交订单
        self.commit_order()

        return windows

    # 2 发明专利-标准服务-加急撰写
    # def patent_invention_normal_urgent(self):
    #     # 选择发明专利
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'发明专利').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 服务类型选择
    #     # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()
    #     # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
    #     # ActionChains(self.driver).move_to_element(aa).perform()
    #     # self.driver.find_element_by_xpath("//a[@class='jian']").click()
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.driver.find_element_by_xpath("//a[@class='add']").click()
    #     # 数量减1
    #     # self.driver.find_element_by_xpath("//a[@class='jian']").click()
    #
    #     # 立即申请
    #     self.apply_now()
    #     # 提交订单
    #     self.commit_order()
    #
    #     # 立即支付
    #     # self.pay(windows)
    #     return windows

    # 55 专属加急注册
    def trademark_urgent_register(self):
        # locator = (By.XPATH, "(.//div[@class='isnav-first']/div[@class='fl isnaMar'])[2]")
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专属加急注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # 立即申请
        self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()
        # 切换至选择商标分类页面
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        num = random.randint(1, 45)
        num = 35
        time.sleep(1)
        target = self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[{}]".format(num))
        self.driver.execute_script("arguments[0].scrollIntoView();", target)
        self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[45]").click()

        # 立即申请
        self.driver.find_element_by_xpath("//div[@id='bottombg']/div/span").click()
        # 提交订单
        locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
        WebDriverWait(self.driver, 30, 1).until(EC.element_to_be_clickable(locator))
        self.excel_number()
        self.driver.find_element_by_id('lnkPay').click()

        return windows

    # # # 56 专属双享注册
    # # def trademark_double_register(self):
    # #     # 选择发明专利
    # #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    # #     ActionChains(self.driver).move_to_element(aa).perform()
    # #     self.driver.find_element_by_link_text(u'专属双享注册').click()
    # #     # 切换至新窗口
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     # 服务类型选择
    # #     # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()
    # #
    # #     # 增值服务类型选择
    # #     # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    # #
    # #     # 立即申请
    # #     self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()
    # #     # 切换至选择商标分类页面
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     num = random.randint(1, 45)
    # #     num = 35
    # #     time.sleep(1)
    # #     target = self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[{}]".format(num))
    # #     self.driver.execute_script("arguments[0].scrollIntoView();", target)
    # #     self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[45]").click()
    # #
    # #     # 立即申请
    # #     self.driver.find_element_by_xpath("//div[@id='bottombg']/div/span").click()
    # #     # 提交订单
    # #     locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
    # #     WebDriverWait(self.driver, 30, 1).until(EC.element_to_be_clickable(locator))
    # #     self.excel_number(self.driver, self.row)
    # #     self.driver.find_element_by_id('lnkPay').click()
    # #
    # #     # 立即支付
    # #     self.pay(windows)
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     self.driver.close()
    # #     self.driver.switch_to_window(windows[0])
    # #     windows = self.driver.window_handles
    # #
    # # # 58 驰名商标注册
    # # def trademark_famous_brand(self):
    # #     # 选择发明专利
    # #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    # #     ActionChains(self.driver).move_to_element(aa).perform()
    # #     self.driver.find_element_by_link_text(u'驰名商标认定').click()
    # #     # 切换至新窗口
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     # 服务类型选择
    # #     # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()
    # #
    # #     # 增值服务类型选择
    # #     # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    # #
    # #     # 立即申请
    # #     self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()
    # #
    # #     # 提交订单
    # #     locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
    # #     WebDriverWait(self.driver, 30, 1).until(EC.element_to_be_clickable(locator))
    # #     self.excel_number(self.driver, self.row)
    # #     self.driver.find_element_by_id('lnkPay').click()
    # #
    # #     # 立即支付
    # #     self.pay(windows)
    # #     # windows = self.driver.window_handles
    # #     # self.driver.switch_to_window(windows[-1])
    # #     # self.driver.close()
    # #     # self.driver.switch_to_window(windows[0])
    # #     # windows = self.driver.window_handles
    # #
    # # # 97 计算机软件著作权登记-5日
    # # def copyright_computer_software_05(self):
    # #     # 选择计算机软件著作权登记
    # #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
    # #     ActionChains(self.driver).move_to_element(aa).perform()
    # #     self.driver.find_element_by_link_text(u'计算机软件著作权登记').click()
    # #     # 切换至新窗口
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     # 服务类型：
    # #     # 36个工作日
    # #     # self.driver.find_element_by_xpath("//ul[@p='232']/li[1]/a").click()
    # #     # # 20个工作日
    # #     # self.driver.find_element_by_xpath("//ul[@p='232']/li[2]/a").click()
    # #     # # 15个工作日
    # #     # self.driver.find_element_by_xpath("//ul[@p='232']/li[3]/a").click()
    # #     # # 10个工作日
    # #     # self.driver.find_element_by_xpath("//ul[@p='232']/li[4]/a").click()
    # #     # # 5个工作日
    # #     self.driver.find_element_by_xpath("//ul[@p='232']/li[5]/a").click()
    # #     # # 3个工作日
    # #     # self.driver.find_element_by_xpath("//ul[@p='232']/li[6]/a").click()
    # #     # 数量加减
    # #     # self.driver.find_element_by_xpath("//a[@class='add']").click()
    # #     # self.driver.find_element_by_xpath("//a[@class='jian']").click()
    # #     # 立即申请
    # #     self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()
    # #     # 提交订单
    # #     locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     self.excel_number(self.driver, self.row)
    # #     self.driver.find_element_by_id('lnkPay').click()
    # #
    # #     # 立即支付
    # #     self.pay(windows)
    # #
    # # # 101 美术作品著作权登记-15日
    # # def copyright_art_works_03(self):
    # #     # 选择美术作品著作权登记
    # #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
    # #     ActionChains(self.driver).move_to_element(aa).perform()
    # #     self.driver.find_element_by_link_text(u'美术作品著作权登记').click()
    # #     # 切换至新窗口
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     # 服务类型：
    # #     # 36个工作日
    # #     # self.driver.find_element_by_xpath("//ul[@p='231']/li[1]/a").click()
    # #     # # 20个工作日
    # #     # self.driver.find_element_by_xpath("//ul[@p='231']/li[2]/a").click()
    # #     # # 15个工作日
    # #     self.driver.find_element_by_xpath("//ul[@p='231']/li[3]/a").click()
    # #     # # 10个工作日
    # #     # self.driver.find_element_by_xpath("//ul[@p='231']/li[4]/a").click()
    # #     # # 5个工作日
    # #     # self.driver.find_element_by_xpath("//ul[@p='231']/li[5]/a").click()
    # #     # # 3个工作日
    # #     # self.driver.find_element_by_xpath("//ul[@p='231']/li[6]/a").click()
    # #     # 数量加减
    # #     # self.driver.find_element_by_xpath("//a[@class='add']").click()
    # #     # self.driver.find_element_by_xpath("//a[@class='jian']").click()
    # #     # 立即申请
    # #     self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()
    # #     # 提交订单
    # #     locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     self.excel_number(self.driver, self.row)
    # #     self.driver.find_element_by_id('lnkPay').click()
    # #
    # #     # 立即支付
    # #     self.pay(windows)
    # #
    # # # 111 国家高新企业认定-标准
    # # def highNew_enterprise_standard(self):
    # #     # 选择国家高新企业认定
    # #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
    # #     ActionChains(self.driver).move_to_element(aa).perform()
    # #     self.driver.find_element_by_link_text(u'国家高新企业认定').click()
    # #     # 切换至新窗口
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     # 数量加减
    # #     # self.driver.find_element_by_xpath("//a[@class='add']").click()
    # #     # self.driver.find_element_by_xpath("//a[@class='jian']").click()
    # #     # 立即申请
    # #     self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()
    # #     # 提交订单
    # #     locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     self.excel_number(self.driver, self.row)
    # #     self.driver.find_element_by_id('lnkPay').click()
    # #
    # #     # 立即支付
    # #     self.pay(windows)
    # #
    # # # 112 国家高新企业认定-担保
    # # def highNew_enterprise_guarantee(self):
    # #     # 选择国家高新企业认定
    # #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
    # #     ActionChains(self.driver).move_to_element(aa).perform()
    # #     self.driver.find_element_by_link_text(u'国家高新企业认定').click()
    # #     # 切换至新窗口
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     # 案件类型
    # #     self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[2]/a").click()
    # #     # 数量加减
    # #     # self.driver.find_element_by_xpath("//a[@class='add']").click()
    # #     self.driver.find_element_by_xpath("//a[@class='jian']").click()
    # #     # 立即申请
    # #     self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()
    # #     # 提交订单
    # #     locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     self.excel_number(self.driver, self.row)
    # #     self.driver.find_element_by_id('lnkPay').click()
    # #
    # #     # 立即支付
    # #     self.pay(windows)
    # #
    # # # 113 商标设计套餐
    # # def taoCan_design_package(self):
    # #     # 选择商标设计套餐
    # #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar']/h2)[6]")
    # #     ActionChains(self.driver).move_to_element(aa).perform()
    # #     self.driver.find_element_by_link_text(u'商标设计套餐').click()
    # #     # 切换至新窗口
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     # 数量加减
    # #     # self.driver.find_element_by_xpath("//a[@class='add']").click()
    # #     # self.driver.find_element_by_xpath("//a[@class='jian']").click()
    # #     # 立即申请
    # #     self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]").click()
    # #     # 选择商标分类
    # #     self.driver.find_element_by_xpath("(.//a[@class='theme-fl-meal'])[1]").click()
    # #     time.sleep(1)
    # #     self.driver.find_element_by_xpath("(.//ul[@id='ulclass']/li[1])[1]").click()
    # #     self.driver.find_element_by_xpath("(.//a[@class='qd'])[1]").click()
    # #     self.driver.find_element_by_xpath(".//a[@class='submit-btn']").click()
    # #
    # #     # 提交订单
    # #     locator = (By.XPATH, "(//parent::li[div[@class='selected-b']])[1]")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     self.excel_number(self.driver, self.row)
    # #     self.driver.find_element_by_id('lnkPay').click()
    # #
    # #     # 立即支付
    # #     self.pay(window
    #
    # # def trademark_reissue_brand(self):
    # #     # 选择补发商标注册证申请
    # #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    # #     ActionChains(self.driver).move_to_element(aa).perform()
    # #     self.driver.find_element_by_link_text(u'补发商标注册证申请').click()
    # #     # 切换至新窗口
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     # 数量加减
    # #     # self.driver.find_element_by_xpath("//a[@class='add']").click()
    # #     # self.driver.find_element_by_xpath("//a[@class='jian']").click()
    # #     # 立即申请
    # #     self.apply_now()
    # #     # 提交订单
    # #     self.commit_order()
    # #
    # #     return windows

    # 93 计算机软件著作权登记-36日
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
        # 36个工作日
        self.driver.find_element_by_xpath("//ul[@p='232']/li[1]/a").click()
        # # 20个工作日
        # self.driver.find_element_by_xpath("//ul[@p='232']/li[2]/a").click()
        # # 15个工作日
        # self.driver.find_element_by_xpath("//ul[@p='232']/li[3]/a").click()
        # # 10个工作日
        # self.driver.find_element_by_xpath("//ul[@p='232']/li[4]/a").click()
        # # 5个工作日
        # self.driver.find_element_by_xpath("//ul[@p='232']/li[5]/a").click()
        # # 3个工作日
        # self.driver.find_element_by_xpath("//ul[@p='232']/li[6]/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows


def create():
    crawler = Execute()
    for callback_label in range(crawler.__FuncCount__):
        callback = crawler.__Func__[callback_label]
        print("test", callback)
        crawler.get_function_name(callback)


def delete():
    crawler = Execute()
    for i in range(2):
        crawler.delete_order()




if __name__ == '__main__':
    # 专利
    create()
    # delete()
    # 商标
    # run(trademark)
    # 版权
    # run(copyright)

