import os
import random
import time

import xlwt
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from front_login import *
from readConfig import ReadConfig
from copy import deepcopy
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
        self.db = "case"

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
    def closed_windows(self):
        print("=================0==============")
        print(self.windows)
        n = len(self.windows)
        while n > 1:
            print('打印windows1', self.windows)
            self.driver.switch_to_window(self.windows[-1])
            print("===================1=============")
            self.driver.close()
            del self.windows[-1]
            n -= 1
            self.driver.switch_to_window(self.windows[0])
            print('打印windows2', self.windows)
            print("=====================2=============")

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

    # =======================业务类型=================================
    # 国内商标
    def trademark_adviser_register(self):
        all_type = [u'专属顾问注册', u'专属加急注册', u'专属双享注册', u'专属担保注册']
        for trademark_type in all_type:
            if self.dboperate.is_member(self.db, trademark_type):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(trademark_type).click()
                    # 切换至新窗口
                    windows = self.driver.window_handles
                    self.driver.switch_to_window(windows[-1])

                    self.apply_now()
                    # 切换至选择商标分类页面
                    self.windows = self.driver.window_handles
                    self.driver.switch_to_window(self.windows[-1])
                    num = random.randint(1, 45)
                    # num = 35
                    time.sleep(1)
                    target = self.driver.find_element_by_xpath(
                        ".//ul[@class='statuslist']/li[@idx='{}']".format(num))
                    self.driver.execute_script("arguments[0].scrollIntoView();", target)
                    time.sleep(0.5)
                    self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[{}]".format(num)).click()

                    time.sleep(0.5)
                    while not self.driver.find_element_by_id("costesNum").is_displayed():
                        time.sleep(0.5)
                    # 获取详情页 价格
                    # detail_price = self.driver.find_element_by_xpath("(.//div[@class='info-checkedtop']/p/span)").text
                    detail_price = self.driver.find_element_by_xpath("(.//div[@class='bottomin']/p[1]/span)").text
                    # print("商标页价格", total_price)
                    detail_price = self.process_price(detail_price)

                    print("详情页价格", detail_price)
                    self.driver.find_element_by_xpath("//div[@id='bottombg']/div/span").click()

                    case_name, case_number, case_price, totalprice = self.commit_order()
                    # return windows, [case_name, case_number, detail_price, case_price, totalprice]
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
                    # 删除已执行的类型
                    self.dboperate.del_elem(self.db, trademark_type)
                    time.sleep(1)
                    self.closed_windows()
                except Exception as e:
                    print('错误信息', e)
                    self.driver.switch_to_window(self.windows[0])

    # 国际商标
    def trademark_international(self):
        all_type = [u'美国商标注册', u'日本商标注册', u'韩国商标注册', u'台湾商标注册', u'香港商标注册', u'德国商标注册',
                    u'欧盟商标注册', u'马德里国际商标', u'非洲知识产权组织']
        for international_type in all_type:
            if self.dboperate.is_member(self.db, international_type):
                # print(self.dboperate.is_member(international_type))
                try:
                    locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(international_type).click()
                    # 切换至新窗口
                    self.windows = self.driver.window_handles
                    self.driver.switch_to_window(self.windows[-1])
                    # 商标分类
                    self.driver.find_element_by_xpath("//a[@class='theme-fl']").click()
                    time.sleep(0.5)
                    self.driver.find_element_by_xpath("//ul[@class='theme-ul']/li[1]/p").click()
                    sleep(0.5)
                    self.driver.find_element_by_xpath("//div[@class='theme-btn']/a[3]").click()
                    time.sleep(0.5)
                    while not self.driver.find_element_by_id("totalfee").is_displayed():
                        time.sleep(0.5)
                    # 获取详情页 价格
                    detail_price = self.driver.find_element_by_xpath(
                        "(.//div[@class='sames']//label[@id='totalfee'])").text
                    print("详情页价格", detail_price)

                    self.apply_now()
                    case_name, case_number, case_price, totalprice = self.commit_order()
                    # return windows, [case_name, case_number, detail_price, case_price, totalprice]
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
                    self.dboperate.del_elem(self.db, international_type)
                    time.sleep(1)
                    print(self.windows)
                    self.closed_windows()
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])

    # 共用部分
    def trademark_famous_brand(self):
        all_type = [u'申请商标更正', u'出具商标注册证明申请', u'补发商标注册证申请', u'商标转让', u'商标注销', u'商标变更', u'商标诉讼', u'证明商标注册',
                    u'集体商标注册', u'驰名商标认定']
        for trademark in all_type:
            if self.dboperate.is_member(self.db, trademark):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(trademark).click()
                    # 切换至新窗口
                    self.windows = self.driver.window_handles
                    self.driver.switch_to_window(self.windows[-1])
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
                    self.dboperate.del_elem(self.db, trademark)
                    time.sleep(1)
                    self.closed_windows()
                except Exception as e:
                    print('错误信息', e)
                    self.driver.switch_to_window(self.windows[0])

        time.sleep(1)

    # 商标驳回复审-（普通，双保）
    def trademark_ordinary_reject(self):
        this_type = u'商标驳回复审'
        if self.dboperate.is_member(self.db, this_type):
            locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
            WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
            aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
            ActionChains(self.driver).move_to_element(aa).perform()
            self.driver.find_element_by_link_text(this_type).click()
            # 切换至新窗口
            self.windows = self.driver.window_handles
            self.driver.switch_to_window(self.windows[-1])
            # 服务类型
            for num in [1, 2]:
                try:
                    time.sleep(0.5)
                    self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[@t='{}']/a".format(num)).click()
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
                    # return windows, [case_name, case_number, detail_price, case_price, totalprice]
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
                    self.closed_windows()
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[1])
            self.closed_windows()
            self.dboperate.del_elem(self.db, this_type)
            time.sleep(1)

    # 商标异议 （异议申请、异议答辩）
    def trademark_objection_apply(self):
        this_type = u'商标异议'
        if self.dboperate.is_member(self.db, this_type):
            locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
            WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
            aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
            ActionChains(self.driver).move_to_element(aa).perform()
            self.driver.find_element_by_link_text(this_type).click()
            # 切换至新窗口
            self.windows = self.driver.window_handles
            self.driver.switch_to_window(self.windows[-1])
            # 业务方向:异议申请、异议答辩、不予注册复审
            for num in [22721, 22722]:
                try:
                    self.driver.find_element_by_xpath("//li[@pt='{}']/a".format(num)).click()
                    # 数量加减
                    # self.number_add()
                    # # self.number_minus()
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
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[1])
            self.closed_windows()
            self.dboperate.del_elem(self.db, this_type)
            time.sleep(1)

    # 商标撤三答辩--（商标撤三申请、商标撤三答辩）
    def trademark_brand_revoke_answer(self):
        this_type = u'商标撤销'
        if self.dboperate.is_member(self.db, this_type):
            locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
            WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
            aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
            ActionChains(self.driver).move_to_element(aa).perform()
            self.driver.find_element_by_link_text(this_type).click()
            # 切换至新窗口
            self.windows = self.driver.window_handles
            self.driver.switch_to_window(self.windows[-1])
            # 业务方向:商标撤三申请、商标撤三答辩
            for num in range(1, 3):
                try:
                    self.driver.find_element_by_xpath("//ul[@p='2273']/li[{}]/a".format(num)).click()
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
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[1])
            self.closed_windows()
            self.dboperate.del_elem(self.db, this_type)
            time.sleep(1)

    # 商标无效宣告--（商标无效宣告、商标无效宣告答辩）
    def trademark_brand_invalid_declare(self):
        this_type = u'商标无效'
        if self.dboperate.is_member(self.db, this_type):
            locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
            WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
            aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
            ActionChains(self.driver).move_to_element(aa).perform()
            self.driver.find_element_by_link_text(this_type).click()
            # 切换至新窗口
            self.windows = self.driver.window_handles
            self.driver.switch_to_window(self.windows[-1])
            # 业务方向:商标无效宣告、商标无效宣告答辩
            for num in range(1, 3):
                try:
                    self.driver.find_element_by_xpath("//ul[@p='2279']/li[{}]/a".format(num)).click()
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
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[1])
            self.closed_windows()
            self.dboperate.del_elem(self.db, this_type)
            time.sleep(1)

    # 商标续展--（续展申请、宽展申请、补发续展证明）
    def trademark_brand_extension_01(self):
        this_type = u'商标续展'
        if self.dboperate.is_member(self.db, this_type):
            locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
            WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
            aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
            ActionChains(self.driver).move_to_element(aa).perform()
            self.driver.find_element_by_link_text(this_type).click()
            # 切换至新窗口
            self.windows = self.driver.window_handles
            self.driver.switch_to_window(self.windows[-1])
            # 业务方向:续展申请、宽展申请、补发续展证明
            for num in range(1, 4):
                try:
                    self.driver.find_element_by_xpath("//ul[@p='2274']/li[{}]/a".format(num)).click()
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
                    pay_total_price = self.pay(self.windows)
                    all_info.append(pay_total_price)
                    print(all_info, pay_total_price)
                    if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_total_price) and \
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
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[1])
            self.closed_windows()
            self.dboperate.del_elem(self.db, this_type)
            time.sleep(1)

    # 商标许可备案 --(许可备案、变更（被）许可人名称、许可提前终止)
    def trademark_brand_permit(self):
        this_type = u'商标许可备案'
        if self.dboperate.is_member(self.db, this_type):
            locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
            WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
            aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
            ActionChains(self.driver).move_to_element(aa).perform()
            self.driver.find_element_by_link_text(this_type).click()
            # 切换至新窗口
            self.windows = self.driver.window_handles
            self.driver.switch_to_window(self.windows[-1])
            # 业务方向:许可备案、变更（被）许可人名称、许可提前终止
            for num in range(1, 4):
                try:
                    self.driver.find_element_by_xpath("//ul[@p='2278']/li[{}]/a".format(num)).click()
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
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[1])
            self.closed_windows()
            self.dboperate.del_elem(self.db, this_type)
            time.sleep(1)
