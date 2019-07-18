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

    # 54 专属顾问注册
    def trademark_adviser_register(self):
        # 选择发明专利
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专属顾问注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        self.apply_now()
        # 切换至选择商标分类页面
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        num = random.randint(1, 45)
        num = 35
        time.sleep(1)
        target = self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[{}]".format(num))
        self.driver.execute_script("arguments[0].scrollIntoView();", target)
        self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[45]").click()

        self.driver.find_element_by_xpath("//div[@id='bottombg']/div/span").click()
        self.commit_order()

        return windows

    # 55 专属加急注册
    def trademark_urgent_register(self):
        # 选择发明专利
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

        self.apply_now()
        # 切换至选择商标分类页面
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        num = random.randint(1, 45)
        num = 35
        time.sleep(1)
        target = self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[{}]".format(num))
        self.driver.execute_script("arguments[0].scrollIntoView();", target)
        self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[45]").click()

        self.driver.find_element_by_xpath("//div[@id='bottombg']/div/span").click()
        self.commit_order()

        return windows

    # 56 专属双享注册
    def trademark_double_register(self):
        # 选择发明专利
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专属双享注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        self.apply_now()
        # 切换至选择商标分类页面
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        num = random.randint(1, 45)
        num = 35
        time.sleep(1)
        target = self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[{}]".format(num))
        self.driver.execute_script("arguments[0].scrollIntoView();", target)
        self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[45]").click()

        self.driver.find_element_by_xpath("//div[@id='bottombg']/div/span").click()
        self.commit_order()

        return windows

    # 57 专属担保注册
    def trademark_guarantee_register(self):
        # 选择发明专利
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专属担保注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        self.apply_now()
        # 切换至选择商标分类页面
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        num = random.randint(1, 45)
        num = 35
        time.sleep(2)
        target = self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[{}]".format(num))
        self.driver.execute_script("arguments[0].scrollIntoView();", target)
        self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[45]").click()

        self.driver.find_element_by_xpath("//div[@id='bottombg']/div/span").click()
        self.commit_order()

        return windows

    # 58 驰名商标注册
    def trademark_famous_brand(self):
        # 选择发明专利
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'驰名商标认定').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        self.apply_now()
        self.commit_order()

        return windows

    # 59 集体商标注册
    def trademark_group_brand(self):
        # 选择发明专利
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'集体商标注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        self.apply_now()
        self.commit_order()

        return windows

    # 60 证明商标注册
    def trademark_prove_brand(self):
        # 选择发明专利
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'证明商标注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        self.apply_now()
        self.commit_order()

        return windows

    # # 61 美国商标注册
    # def trademark_USA_brand(self):
    #     # 选择美国商标注册
    #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'美国商标注册').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 商标分类
    #     self.driver.find_element_by_xpath("//a[@class='theme-fl']").click()
    #     time.sleep(0.5)
    #     self.driver.find_element_by_xpath("//ul[@class='theme-ul']/li[1]/p").click()
    #     sleep(1)
    #     self.driver.find_element_by_xpath("//div[@class='theme-btn']/a[3]").click()
    #     self.apply_now()
    #     self.commit_order()
    #
    #     return windows
    #
    # # 62 日本商标注册
    # def trademark_Japan_brand(self):
    #     # 选择日本商标注册
    #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'日本商标注册').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 商标分类
    #     self.driver.find_element_by_xpath("//a[@class='theme-fl']").click()
    #     time.sleep(0.5)
    #     self.driver.find_element_by_xpath("//ul[@class='theme-ul']/li[1]/p").click()
    #     sleep(1)
    #     self.driver.find_element_by_xpath("//div[@class='theme-btn']/a[3]").click()
    #     self.apply_now()
    #     self.commit_order()
    #
    #     return windows
    #
    # # 63 韩国商标注册
    # def trademark_Korea_brand(self):
    #     # 选择韩国商标注册
    #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'韩国商标注册').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 商标分类
    #     self.driver.find_element_by_xpath("//a[@class='theme-fl']").click()
    #     time.sleep(0.5)
    #     self.driver.find_element_by_xpath("//ul[@class='theme-ul']/li[1]/p").click()
    #     sleep(1)
    #     self.driver.find_element_by_xpath("//div[@class='theme-btn']/a[3]").click()
    #     self.apply_now()
    #     self.commit_order()
    #
    #     return windows
    #
    # # 64 台湾商标注册
    # def trademark_Taiwan_brand(self):
    #     # 选择台湾商标注册
    #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'台湾商标注册').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 商标分类
    #     self.driver.find_element_by_xpath("//a[@class='theme-fl']").click()
    #     time.sleep(0.5)
    #     self.driver.find_element_by_xpath("//ul[@class='theme-ul']/li[1]/p").click()
    #     sleep(1)
    #     self.driver.find_element_by_xpath("//div[@class='theme-btn']/a[3]").click()
    #     self.apply_now()
    #     self.commit_order()
    #
    #     return windows
    #
    # # 65 香港商标注册
    # def trademark_Hongkong_brand(self):
    #     # 选择香港商标注册
    #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'香港商标注册').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 商标分类
    #     self.driver.find_element_by_xpath("//a[@class='theme-fl']").click()
    #     time.sleep(0.5)
    #     self.driver.find_element_by_xpath("//ul[@class='theme-ul']/li[1]/p").click()
    #     sleep(1)
    #     self.driver.find_element_by_xpath("//div[@class='theme-btn']/a[3]").click()
    #     self.apply_now()
    #     self.commit_order()
    #
    #     return windows
    #
    # # 66 德国商标注册
    # def trademark_Germany_brand(self):
    #     # 选择德国商标注册
    #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'德国商标注册').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 商标分类
    #     self.driver.find_element_by_xpath("//a[@class='theme-fl']").click()
    #     time.sleep(0.5)
    #     self.driver.find_element_by_xpath("//ul[@class='theme-ul']/li[1]/p").click()
    #     sleep(1)
    #     self.driver.find_element_by_xpath("//div[@class='theme-btn']/a[3]").click()
    #     self.apply_now()
    #     self.commit_order()
    #
    #     return windows
    #
    # # 67 欧盟商标注册
    # def trademark_EU_brand(self):
    #     # 选择欧盟商标注册
    #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'欧盟商标注册').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 商标分类
    #     self.driver.find_element_by_xpath("//a[@class='theme-fl']").click()
    #     time.sleep(0.5)
    #     self.driver.find_element_by_xpath("//ul[@class='theme-ul']/li[1]/p").click()
    #     sleep(1)
    #     self.driver.find_element_by_xpath("//div[@class='theme-btn']/a[3]").click()
    #     self.apply_now()
    #     self.commit_order()
    #
    #     return windows
    #
    # # 68 马德里商标注册
    # def trademark_Madrid_brand(self):
    #     # 选择马德里国际商标
    #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'马德里国际商标').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 商标分类
    #     self.driver.find_element_by_xpath("//a[@class='theme-fl']").click()
    #     time.sleep(0.5)
    #     self.driver.find_element_by_xpath("//ul[@class='theme-ul']/li[1]/p").click()
    #     sleep(1)
    #     self.driver.find_element_by_xpath("//div[@class='theme-btn']/a[3]").click()
    #     self.apply_now()
    #     self.commit_order()
    #
    #     return windows
    #
    # # 69 非洲知识产权组织
    # def trademark_Africa_knowledge(self):
    #     # 选择非洲知识产权组织
    #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'非洲知识产权组织').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 商标分类
    #     self.driver.find_element_by_xpath("//a[@class='theme-fl']").click()
    #     time.sleep(0.5)
    #     self.driver.find_element_by_xpath("//ul[@class='theme-ul']/li[1]/p").click()
    #     sleep(1)
    #     self.driver.find_element_by_xpath("//div[@class='theme-btn']/a[3]").click()
    #     self.apply_now()
    #     self.commit_order()
    #
    #     return windows

    # 70 商标驳回复审-普通
    def trademark_ordinary_reject(self):
        # 选择商标驳回复审
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标驳回复审').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 71 商标驳回复审-双保
    def trademark_double_reject(self):
        # 选择商标驳回复审
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标驳回复审').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型
        self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[2]").click()
        # 数量加减
        # self.number_add()
        # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 72 商标异议申请
    def trademark_objection_apply(self):
        # 选择商标异议
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标异议').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:异议申请、异议答辩、不予注册复审
        self.driver.find_element_by_xpath("//li[@pt='22721']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 73 商标异议答辩
    def trademark_objection_answer(self):
        # 选择商标异议
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标异议').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:异议申请、异议答辩、不予注册复审

        self.driver.find_element_by_xpath("//li[@pt='22722']/a").click()

        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 74 商标异议不予注册
    def trademark_objection_noregistration(self):
        # 选择商标异议
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标异议').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:异议申请、异议答辩、不予注册复审
        # self.driver.find_element_by_xpath("//li[@pt='22721']/a").click()
        # self.driver.find_element_by_xpath("//li[@pt='22722']/a").click()
        self.driver.find_element_by_xpath("//li[@pt='22723']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 75 商标撤三申请
    def trademark_brand_revoke_apply(self):
        # 选择商标撤销
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标撤销').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:商标撤三申请、商标撤三答辩
        self.driver.find_element_by_xpath("//li[@pt='22731']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 76 商标撤三答辩
    def trademark_brand_revoke_answer(self):
        # 选择商标撤销
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标撤销').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:商标撤三申请、商标撤三答辩
        self.driver.find_element_by_xpath("//li[@pt='22732']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 77 商标无效宣告
    def trademark_brand_invalid_declare(self):
        # 选择商标无效
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标无效').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:商标无效宣告、商标无效宣告答辩
        self.driver.find_element_by_xpath("//li[@pt='22791']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 78 商标无效答辩
    def trademark_brand_invalid_answer(self):
        # 选择商标无效
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标无效').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:商标无效宣告、商标无效宣告答辩
        self.driver.find_element_by_xpath("//li[@pt='22792']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 79 商标诉讼
    def trademark_brand_litigation(self):
        # 选择商标诉讼
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标诉讼').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 80 商标变更
    def trademark_brand_change(self):
        # 选择商标变更
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标变更').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 81 商标续展-续展
    def trademark_brand_extension_01(self):
        # 选择商标续展
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标续展').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:续展申请、宽展申请、补发续展证明
        self.driver.find_element_by_xpath("//li[@pt='22741']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 82 商标续展-宽展
    def trademark_brand_extension_02(self):
        # 选择商标续展
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标续展').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:续展申请、宽展申请、补发续展证明

        self.driver.find_element_by_xpath("//li[@pt='22742']/a").click()

        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 83 商标续展-补发续展
    def trademark_brand_extension_03(self):
        # 选择商标续展
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标续展').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:续展申请、宽展申请、补发续展证明
        # self.driver.find_element_by_xpath("//li[@pt='22741']/a").click()
        # self.driver.find_element_by_xpath("//li[@pt='22742']/a").click()
        self.driver.find_element_by_xpath("//li[@pt='22743']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 84 商标许可备案
    def trademark_brand_permit(self):
        # 选择商标许可备案
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标许可备案').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:许可备案、变更（被）许可人名称、许可提前终止
        self.driver.find_element_by_xpath("//li[@pt='22781']/a").click()
        # self.driver.find_element_by_xpath("//li[@pt='22782']/a").click()
        # self.driver.find_element_by_xpath("//li[@pt='22783']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 85 商标许可备案-变更许可人
    def trademark_brand_permit_01(self):
        # 选择商标许可备案
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标许可备案').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:许可备案、变更（被）许可人名称、许可提前终止
        self.driver.find_element_by_xpath("//li[@pt='22782']/a").click()
        # self.driver.find_element_by_xpath("//li[@pt='22782']/a").click()
        # self.driver.find_element_by_xpath("//li[@pt='22783']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 86 商标许可备案-许可提前终止
    def trademark_brand_permit_02(self):
        # 选择商标许可备案
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标许可备案').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向:许可备案、变更（被）许可人名称、许可提前终止
        self.driver.find_element_by_xpath("//li[@pt='22783']/a").click()
        # self.driver.find_element_by_xpath("//li[@pt='22782']/a").click()
        # self.driver.find_element_by_xpath("//li[@pt='22783']/a").click()
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 87 商标注销
    def trademark_brand_cancel(self):
        # 选择商标注销
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标注销').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 88 申请商标转让
    def trademark_brand_assignment_01(self):
        # 选择商标转让
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标转让').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向：申请商标转让/移转、补发商标转让/移转
        self.driver.find_element_by_xpath("//li[@pt='22771']/a")
        # self.driver.find_element_by_xpath("//li[@pt='22772']/a")
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 89 补发商标转让
    def trademark_brand_assignment_02(self):
        # 选择商标转让
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标转让').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务方向：申请商标转让/移转、补发商标转让/移转
        self.driver.find_element_by_xpath("//li[@pt='22772']/a")
        # self.driver.find_element_by_xpath("//li[@pt='22772']/a")
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 90 补发商标注册证申请
    def trademark_reissue_brand(self):
        # 选择补发商标注册证申请
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'补发商标注册证申请').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 91 出具商标注册证明申请
    def trademark_issue_brand(self):
        # 选择出具商标注册证明申请
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'出具商标注册证明申请').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 92 申请商标更正
    def trademark_brand_amend(self):
        # 选择申请商标更正
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'申请商标更正').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows
