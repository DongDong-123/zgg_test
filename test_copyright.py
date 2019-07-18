import os
import random
import time

import xlwt
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from front_login import *
from readConfig import ReadConfig


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
        # Excel写入
        self.row = 0
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.booksheet = self.workbook.add_sheet('Sheet1')
        self.timetemp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())  # 存储Excel表格文件名编号
        # 每个案件的数量
        self.number = 1
        self.report_path = ReadConfig().save_report()
        self.case_count = FunctionName.get_count

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
            back_parm = eval("self.{}()".format(callback))
            self.row = self.row + 1
            time.sleep(0.5)
            self.pay(back_parm)
            time.sleep(0.5)
            self.closed_windows()

        except Exception as e:
            # print("错误信息:", e)
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
        self.save_delete_case(order_number, case_name, case_number, delete_staus)
        self.row = self.row + 1
        # self.driver.refresh()  # 刷新页面

    # 储存删除记录，同一订单多个案件，只存储第一个
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

    # 存储案件类型，案件号
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

   #  # 93 计算机软件著作权登记-36日
   #  def copyright_computer_software_01(self):
   #      # 选择计算机软件著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'计算机软件著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # 36个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='232']/li[1]/a").click()
   #
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 94 计算机软件著作权登记-20日
   #  def copyright_computer_software_02(self):
   #      # 选择计算机软件著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'计算机软件著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # # 20个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='232']/li[2]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 95 计算机软件著作权登记-15日
   #  def copyright_computer_software_03(self):
   #      # 选择计算机软件著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'计算机软件著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # # 15个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='232']/li[3]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 96 计算机软件著作权登记-10日
   #  def copyright_computer_software_04(self):
   #      # 选择计算机软件著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'计算机软件著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # # 10个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='232']/li[4]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 97 计算机软件著作权登记-5日
   #  def copyright_computer_software_05(self):
   #      # 选择计算机软件著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'计算机软件著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # # 5个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='232']/li[5]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 98 计算机软件著作权登记-3日
   #  def copyright_computer_software_06(self):
   #      # 选择计算机软件著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'计算机软件著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # # 3个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='232']/li[6]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 99 美术作品著作权登记-30日
   #  def copyright_art_works_01(self):
   #      # 选择美术作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'美术作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # 30个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='231']/li[1]/a").click()
   #
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 100 美术作品著作权登记-20日
   #  def copyright_art_works_02(self):
   #      # 选择美术作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'美术作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # # 20个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='231']/li[2]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 101 美术作品著作权登记-15日
   #  def copyright_art_works_03(self):
   #      # 选择美术作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'美术作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # # 15个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='231']/li[3]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 102 美术作品著作权登记-10日
   #  def copyright_art_works_04(self):
   #      # 选择美术作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'美术作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # # 10个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='231']/li[4]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 103 美术作品著作权登记-5日
   #  def copyright_art_works_05(self):
   #      # 选择美术作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'美术作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # # 5个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='231']/li[5]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 104 美术作品著作权登记-3日
   #  def copyright_art_works_06(self):
   #      # 选择美术作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'美术作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 服务类型：
   #      # # 3个工作日
   #      self.driver.find_element_by_xpath("//ul[@p='231']/li[6]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 105 文字作品著作权登记-30日
   #  def copyright_writings_01(self):
   #      # 选择文字作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'文字作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[1]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 105 文字作品著作权登记-20日
   #  def copyright_writings_02(self):
   #      # 选择文字作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'文字作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[2]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 105 文字作品著作权登记-15日
   #  def copyright_writings_03(self):
   #      # 选择文字作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'文字作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[3]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 105 文字作品著作权登记-10日
   #  def copyright_writings_04(self):
   #      # 选择文字作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'文字作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[4]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 105 文字作品著作权登记-5日
   #  def copyright_writings_05(self):
   #      # 选择文字作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'文字作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[5]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 105 文字作品著作权登记-3日
   #  def copyright_writings_06(self):
   #      # 选择文字作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'文字作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[6]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 106 汇编作品著作权登记-30日
   #  def copyright_compilation_01(self):
   #      # 选择汇编作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'汇编作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[1]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   # # 106 汇编作品著作权登记-20日
   #  def copyright_compilation_02(self):
   #      # 选择汇编作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'汇编作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[2]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 106 汇编作品著作权登记-15日
   #  def copyright_compilation_03(self):
   #      # 选择汇编作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'汇编作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[3]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 106 汇编作品著作权登记-10日
   #  def copyright_compilation_04(self):
   #      # 选择汇编作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'汇编作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[4]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 106 汇编作品著作权登记-5日
   #  def copyright_compilation_05(self):
   #      # 选择汇编作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'汇编作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[5]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 106 汇编作品著作权登记-3日
   #  def copyright_compilation_06(self):
   #      # 选择汇编作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'汇编作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[6]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 107 摄影作品著作权登记-30日
   #  def copyright_photography_01(self):
   #      # 选择摄影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'摄影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[1]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 107 摄影作品著作权登记-20日
   #  def copyright_photography_02(self):
   #      # 选择摄影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'摄影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[2]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 107 摄影作品著作权登记-15日
   #  def copyright_photography_03(self):
   #      # 选择摄影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'摄影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[3]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 107 摄影作品著作权登记-10日
   #  def copyright_photography_04(self):
   #      # 选择摄影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'摄影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[4]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 107 摄影作品著作权登记-5日
   #  def copyright_photography_05(self):
   #      # 选择摄影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'摄影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[5]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 107 摄影作品著作权登记-3日
   #  def copyright_photography_06(self):
   #      # 选择摄影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'摄影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[6]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 108 电影作品著作权登记-30日
   #  def copyright_movie_works_01(self):
   #      # 选择电影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'电影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[1]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 108 电影作品著作权登记-20日
   #  def copyright_movie_works_02(self):
   #      # 选择电影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'电影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[2]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 108 电影作品著作权登记-15日
   #  def copyright_movie_works_03(self):
   #      # 选择电影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'电影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[3]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 108 电影作品著作权登记-10日
   #  def copyright_movie_works_04(self):
   #      # 选择电影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'电影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[4]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 108 电影作品著作权登记-5日
   #  def copyright_movie_works_05(self):
   #      # 选择电影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'电影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[5]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 108 电影作品著作权登记-3日
   #  def copyright_movie_works_06(self):
   #      # 选择电影作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'电影作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[6]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 109 音乐作品著作权登记-30日
   #  def copyright_music_works_01(self):
   #      # 选择音乐作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'音乐作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[1]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 109 音乐作品著作权登记-20日
   #  def copyright_music_works_02(self):
   #      # 选择音乐作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'音乐作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[2]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 109 音乐作品著作权登记-15日
   #  def copyright_music_works_03(self):
   #      # 选择音乐作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'音乐作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[3]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 109 音乐作品著作权登记-10日
   #  def copyright_music_works_04(self):
   #      # 选择音乐作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'音乐作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[4]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 109 音乐作品著作权登记-5日
   #  def copyright_music_works_05(self):
   #      # 选择音乐作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'音乐作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[5]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 109 音乐作品著作权登记-3日
   #  def copyright_music_works_06(self):
   #      # 选择音乐作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'音乐作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[6]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 110 曲艺作品著作权登记-30日
   #  def copyright_quyi_works_01(self):
   #      # 选择曲艺作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'曲艺作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[1]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 110 曲艺作品著作权登记-20日
   #  def copyright_quyi_works_02(self):
   #      # 选择曲艺作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'曲艺作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[2]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 110 曲艺作品著作权登记-15日
   #  def copyright_quyi_works_03(self):
   #      # 选择曲艺作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'曲艺作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[3]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 110 曲艺作品著作权登记-10日
   #  def copyright_quyi_works_04(self):
   #      # 选择曲艺作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'曲艺作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[4]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 110 曲艺作品著作权登记-5日
   #  def copyright_quyi_works_05(self):
   #      # 选择曲艺作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'曲艺作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[5]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
   #  # 110 曲艺作品著作权登记-3日
   #  def copyright_quyi_works_06(self):
   #      # 选择曲艺作品著作权登记
   #      locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
   #      WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
   #      aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
   #      ActionChains(self.driver).move_to_element(aa).perform()
   #      self.driver.find_element_by_link_text(u'曲艺作品著作权登记').click()
   #      # 切换至新窗口
   #      windows = self.driver.window_handles
   #      self.driver.switch_to_window(windows[-1])
   #      # 案件类型：
   #      self.driver.find_element_by_xpath("//ul[@id='ulType']/li[6]/a").click()
   #      # 数量加减
   #      # self.number_add()
   #      # # self.number_minus()
   #      self.apply_now()
   #      self.commit_order()
   #
   #      return windows
   #
