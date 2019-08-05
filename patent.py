import os
import random
import time

import xlwt
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from readConfig import ReadConfig
from db import DbOperate
from Common import Common
from front_login import *

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
        # self.common = Common()
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
        self.db = "case"
        self.windows = None
        self.dboperate = DbOperate()

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
        for n in range(num + 1, len(self.windows)):
            self.driver.switch_to_window(self.windows[n])
            self.driver.close()
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

    # 12 专利申请复审,审查意见答复 -（发明专利，实用新型，外观设计）
    def patent_review_invention(self):
        all_type = [u'专利申请复审', u'审查意见答复']
        type_code = ["patent_recheck", "patent_answer"]
        ul_index = [13, 16]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    windows = self.driver.window_handles
                    self.driver.switch_to_window(windows[-1])
                    # 业务类型选择
                    for num in range(1, 4):
                        self.driver.find_element_by_xpath(
                            ".//ul[@p='{}']/li[{}]/a".format(ul_index[index], num)).click()
                        # 数量加1
                        # self.number_add()
                        # 数量减1
                        # # self.number_minus()
                        while not self.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.driver.find_element_by_xpath(
                            "(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.apply_now()
                        case_name, case_number, case_price, totalprice = self.commit_order()

                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.row = self.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.pay(windows)
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
                        self.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                        time.sleep(1)
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
        time.sleep(1)

    # 查新检索-国内评估，全球评估,第三方公众意见-无需检索，需要检索
    def patent_clue_domestic_1(self):
        all_type = [u'查新检索', u'第三方公众意见']
        type_code = ["patent_clue", "patent_public"]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    windows = self.driver.window_handles
                    self.driver.switch_to_window(windows[-1])
                    # 业务类型选择
                    for num in range(1, 3):
                        self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[{}]/a".format(num)).click()
                        # 数量加1
                        # self.number_add()
                        # 数量减1
                        # # self.number_minus()
                        while not self.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.driver.find_element_by_xpath(
                            "(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.apply_now()
                        case_name, case_number, case_price, totalprice = self.commit_order()

                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.row = self.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.pay(windows)
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
                        self.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                        time.sleep(1)
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
        time.sleep(1)

    # 1 发明专利-标准服务
    def patent_invention_normal(self):
        all_type = [u'发明专利', u'实用新型', u'发明新型同日申请']
        type_code = ["patent", "utility", "oneday"]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    windows = self.driver.window_handles
                    self.driver.switch_to_window(windows[-1])
                    for num in range(7, 8):
                        print("num:", num)
                        # 服务类型选择，
                        if num < 4:
                            self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[{}]/a".format(num)).click()
                        elif num == 4:
                            self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[1]/a").click()
                            # 消除悬浮窗的影响
                            temp = self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[2]/a")
                            ActionChains(self.driver).move_to_element(temp).perform()
                            self.driver.find_element_by_xpath(".//div[@class='ui-increment-zl']//li[1]/a").click()
                        elif num == 5:
                            self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[2]/a").click()
                            self.driver.find_element_by_xpath(".//div[@class='ui-increment-zl']//li[1]/a").click()
                        elif num == 6:
                            self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[3]/a").click()
                            self.driver.find_element_by_xpath(".//div[@class='ui-increment-zl']//li[1]/a").click()
                        else:
                            self.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()
                        # 数量加1
                        # self.number_add()
                        # 数量减1
                        # # self.number_minus()
                        # 判断价格是否加载成功
                        while not self.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.driver.find_element_by_xpath(
                            "(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.apply_now()
                        # 获取下单页价格
                        case_name, case_number, case_price, totalprice = self.commit_order()
                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.row = self.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.pay(windows)
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
                        self.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                        time.sleep(1)
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
                time.sleep(1)

    # 12 专利授权前景分析,专利稳定性分析 -（发明专利，实用新型，外观设计）
    def patent_warrant_invention_1(self):
        all_type = [u'授权前景分析', u'专利稳定性分析']
        type_code = ["patent_warrant", "patent_stable"]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    windows = self.driver.window_handles
                    self.driver.switch_to_window(windows[-1])
                    # 业务类型选择
                    for num in range(1, 4):
                        self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[{}]/a".format(num)).click()
                        # 数量加1
                        # self.number_add()
                        # 数量减1
                        # # self.number_minus()
                        while not self.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.driver.find_element_by_xpath(
                            "(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.apply_now()
                        case_name, case_number, case_price, totalprice = self.commit_order()

                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.row = self.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.pay(windows)
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
                        self.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                        time.sleep(1)
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
        time.sleep(1)

    # 12 利权评价报告-实用新型，外观设计
    def patent_evaluate_utility(self):
        all_type = [u'专利权评价报告']
        type_code = ["patent_evaluate"]
        ul_index = [19]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    windows = self.driver.window_handles
                    self.driver.switch_to_window(windows[-1])
                    # 业务类型选择
                    for num in range(1, 3):
                        self.driver.find_element_by_xpath(
                            ".//ul[@p='{}']/li[{}]/a".format(ul_index[index], num)).click()
                        # 数量加1
                        # self.number_add()
                        # 数量减1
                        # # self.number_minus()
                        while not self.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.driver.find_element_by_xpath(
                            "(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.apply_now()
                        case_name, case_number, case_price, totalprice = self.commit_order()

                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.row = self.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.pay(windows)
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
                        self.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                        time.sleep(1)
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
        time.sleep(1)

    # # 3 外观设计
    def patent_design(self):
        all_type = [u'外观设计']
        type_code = ["design"]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    windows = self.driver.window_handles
                    self.driver.switch_to_window(windows[-1])
                    for num in range(1, 7):
                        # 服务类型选择，
                        if num <= 3:
                            self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[{}]/a".format(num)).click()
                        elif num == 4:
                            self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[1]/a").click()
                            self.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()
                        elif num == 5:
                            self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[2]/a").click()
                            self.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()
                        elif num == 6:
                            self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[3]/a").click()
                            self.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()
                        # 数量加1
                        # self.number_add()
                        # 数量减1
                        # # self.number_minus()
                        # 判断价格是否加载成功
                        while not self.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.driver.find_element_by_xpath(
                            "(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.apply_now()
                        # 获取下单页价格
                        case_name, case_number, case_price, totalprice = self.commit_order()
                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.row = self.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.pay(windows)
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
                        self.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                        time.sleep(1)
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
                time.sleep(1)

    # 著录项目变更
    def patent_description(self):
        all_type = [u'著录项目变更']
        type_code = ["description"]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.driver).move_to_element(aa).perform()
                    self.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    windows = self.driver.window_handles
                    self.driver.switch_to_window(windows[-1])
                    all_direction = [[1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]

                    # =========随机选择一种类型===========
                    random_type = random.choice(all_direction)
                    random_index = all_direction.index(random_type)
                    all_direction = [random_type]
                    # ===================================
                    for index_2, num in enumerate(all_direction):
                        for temp in num:
                            # 业务类型选择
                            if temp == 1:
                                pass
                            else:
                                self.driver.find_element_by_xpath(".//ul[@id='ul1']/li[{}]/a".format(temp)).click()

                        # 数量加1
                        # self.number_add()
                        # 数量减1
                        # # self.number_minus()
                        # 判断价格是否加载成功
                        while not self.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.driver.find_element_by_xpath(
                            "(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.apply_now()
                        # 获取下单页价格
                        case_name, case_number, case_price, totalprice = self.commit_order()
                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.row = self.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.pay(windows)
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
                        self.closed_windows(1)
                        # 使用随机选择类型时，index_2改为random_index
                        self.dboperate.del_elem(type_code[index], random_index)

                        time.sleep(1)
                except Exception as e:
                    print(e)
                    self.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
                time.sleep(1)

# =========共用部分=========
# def patent_common(self):
#     all_type = [u'电商侵权处理', u'专利权恢复', u'专利实施许可备案', u'专利质押备案', u'集成电路布图设计']
#     for patent_type in all_type:
#         if self.dboperate.is_member(self.db, patent_type):
#             try:
#                 locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
#                 WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
#                 aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
#                 ActionChains(self.driver).move_to_element(aa).perform()
#                 self.driver.find_element_by_link_text(patent_type).click()
#                 # 切换至新窗口
#                 self.windows = self.driver.window_handles
#                 self.driver.switch_to_window(self.windows[-1])
#                 # 判断价格是否加载成功
#                 while not self.driver.find_element_by_id("totalfee").is_displayed():
#                     time.sleep(0.5)
#                 # 获取详情页 价格
#                 detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
#                 print("详情页价格", detail_price)
#                 self.apply_now()
#                 case_name, case_number, case_price, totalprice = self.commit_order()
#                 all_info = [case_name, case_number, detail_price, case_price, totalprice]
#                 self.row = self.row + 1
#                 time.sleep(0.5)
#                 pay_totalprice = self.pay(self.windows)
#                 all_info.append(pay_totalprice)
#                 print(all_info, pay_totalprice)
#                 if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
#                         float(all_info[4]) == float(all_info[2]):
#                     status = 'True'
#                 else:
#                     status = "False"
#                 all_info.append(status)
#                 self.excel_number(all_info)
#                 self.dboperate.del_elem(self.db, patent_type)
#
#                 time.sleep(1)
#                 # self.common.qr_shotscreen(patent_type)
#                 self.closed_windows(0)
#
#             except Exception as e:
#                 print('错误信息', e)
#                 self.driver.switch_to_window(self.windows[0])

# # 代缴专利年费
# def patent_replace(self):
#     all_type = [u'代缴专利年费']
#     for patent_type in all_type:
#         if self.dboperate.is_member(self.db, patent_type):
#             try:
#                 locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
#                 WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
#                 aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
#                 ActionChains(self.driver).move_to_element(aa).perform()
#                 self.driver.find_element_by_link_text(patent_type).click()
#                 # 切换至新窗口
#                 windows = self.driver.window_handles
#                 self.driver.switch_to_window(windows[-1])
#                 while not self.driver.find_element_by_id("totalfee").is_displayed():
#                     time.sleep(0.5)
#                 # 获取详情页 价格
#                 detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
#                 print("详情页价格", detail_price)
#
#                 self.apply_now()
#                 self.driver.find_element_by_xpath(".//a[@class='apply-btn button']").click()
#
#                 case_name, case_number, case_price, totalprice = self.commit_order()
#                 all_info = [case_name, case_number, detail_price, case_price, totalprice]
#                 self.row = self.row + 1
#                 time.sleep(0.5)
#                 pay_totalprice = self.pay(self.windows)
#                 all_info.append(pay_totalprice)
#                 print(all_info, pay_totalprice)
#                 if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
#                         float(all_info[4]) == float(all_info[2]):
#                     status = 'True'
#                 else:
#                     status = "False"
#                 all_info.append(status)
#                 self.excel_number(all_info)
#                 self.dboperate.del_elem(self.db, patent_type)
#
#                 time.sleep(1)
#                 # self.common.qr_shotscreen(patent_type)
#                 self.closed_windows(0)
#
#             except Exception as e:
#                 print('错误信息', e)
#                 self.driver.switch_to_window(self.windows[0])

# # PCT 国际申请-- 特殊处理
# def patent_PCT(self):
#     all_type = [u'PCT国际申请']
#     for patent_type in all_type:
#         if self.dboperate.is_member(self.db, patent_type):
#             try:
#                 locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
#                 WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
#                 aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
#                 ActionChains(self.driver).move_to_element(aa).perform()
#                 self.driver.find_element_by_link_text(patent_type).click()
#                 # 切换至新窗口
#                 self.windows = self.driver.window_handles
#                 self.driver.switch_to_window(self.windows[-1])
#                 # 判断价格是否加载成功
#                 while not self.driver.find_element_by_id("totalfee").is_displayed():
#                     time.sleep(0.5)
#                 # 获取详情页 价格
#                 detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
#                 print("详情页价格", detail_price)
#                 self.driver.find_element_by_link_text(u'立即申请').click()
#                 case_name, case_number, case_price, totalprice = self.commit_order()
#                 all_info = [case_name, case_number, detail_price, case_price, totalprice]
#                 self.row = self.row + 1
#                 time.sleep(0.5)
#                 pay_totalprice = self.pay(self.windows)
#                 all_info.append(pay_totalprice)
#                 print(all_info, pay_totalprice)
#                 if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
#                         float(all_info[4]) == float(all_info[2]):
#                     status = 'True'
#                 else:
#                     status = "False"
#                 all_info.append(status)
#                 self.excel_number(all_info)
#                 self.dboperate.del_elem(self.db, patent_type)
#
#                 time.sleep(1)
#                 # self.common.qr_shotscreen(patent_type)
#                 self.closed_windows(0)
#
#             except Exception as e:
#                 print('错误信息', e)
#                 self.driver.switch_to_window(self.windows[0])
