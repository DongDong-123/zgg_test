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
        self.file_name = self.excel_number(("案件名称", "案件号", "详情页价格", "下单页价格", "下单页总价格", "支付页总价格", "价格状态"))

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
        try:
            back_parm, all_info = eval("self.{}()".format(callback))
            self.row = self.row + 1
            time.sleep(0.5)
            pay_totalPrice = self.pay(back_parm)
            all_info.append(pay_totalPrice)
            print(all_info, pay_totalPrice)
            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalPrice) and \
                    float(all_info[4]) == float(all_info[2]):
                status = 'True'
            else:
                status = "False"
            all_info.append(status)
            self.excel_number(all_info)
            time.sleep(0.5)
            self.closed_windows()
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

    # 获取未支付订单数
    def get_code_num(self):
        self.driver.get("{}/user/casemanage.html?state=1".format(ReadConfig().get_user_url()))
        num = self.driver.find_element_by_xpath("//div[@class='fl']/a[2]/span").text
        return int(num)

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

    # # 1 发明专利-标准服务
    # def patent_invention_normal(self):
    #     # 选择发明专利
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'发明专利').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #
    #     # 服务类型选择，次处不选，使用默认值
    #     # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()
    #     # 增值服务类型选择
    #     # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     # 获取下单页价格
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 2 发明专利-标准服务-加急撰写
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
    #
    #     # 服务类型选择
    #     # self.driver.find_element_by_xpath(".//li[@class='focr1 selected']/a").click()
    #     # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
    #     # ActionChains(self.driver).move_to_element(aa).perform()
    #     # # self.number_minus()
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    # #
    # # 3 发明专利-加强版
    # def patent_invention_strengthen(self):
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
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
    #     # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
    #     # ActionChains(self.driver).move_to_element(aa).perform()
    #     # self.number_minus()
    #     # 增值服务类型选择
    #     # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 4 发明专利-加强版-加急撰写
    # def patent_invention_strengthen_urgent(self):
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
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
    #     # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
    #     # ActionChains(self.driver).move_to_element(aa).perform()
    #     # self.number_minus()
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # # 5 发明专利-专家版
    # def patent_invention_expert(self):
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
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
    #     # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
    #     # ActionChains(self.driver).move_to_element(aa).perform()
    #     # self.number_minus()
    #     # 增值服务类型选择
    #     # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # # 6 发明专利-专家版-加急撰写
    # def patent_invention_expert_urgent(self):
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
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
    #     # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
    #     # ActionChains(self.driver).move_to_element(aa).perform()
    #     # self.number_minus()
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 7 发明专利-专家版-担保授权
    # def patent_invention_expert_guarantee(self):
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
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
    #     # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
    #     # ActionChains(self.driver).move_to_element(aa).perform()
    #     # self.number_minus()
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # # 8 实用新型-标准版
    # # def patent_utility_normal(self):
    # #     # 选择实用新型
    # #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    # #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    # #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    # #     ActionChains(self.driver).move_to_element(aa).perform()
    # #     self.driver.find_element_by_link_text(u'实用新型').click()
    # #     # 切换至新窗口
    # #     windows = self.driver.window_handles
    # #     self.driver.switch_to_window(windows[-1])
    # #     # 服务类型选择
    # #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
    # #
    # #     # 增值服务类型选择
    # #     # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    # #
    # #     # 数量加1
    # #     # self.number_add()
    # #     # 数量减1
    # #     # # self.number_minus()
    # #     # 判断价格是否加载成功
    # #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    # #         time.sleep(0.5)
    # #     # 获取详情页 价格
    # #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    # #     print("详情页价格", detail_price)
    # #
    # #     self.apply_now()
    # #     case_name, case_number, case_price, totalPrice = case_name, case_number, case_price, totalPrice = self.commit_order()
    # #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 9 实用新型-标准版-加急撰写
    # def patent_utility_normal_urgent(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'实用新型').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 服务类型选择
    #     # self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
    #     # # self.number_minus()
    #
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath("(.//li[@t=2]/a)[1]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 10 实用新型-加强版
    # def patent_utility_strengthen(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'实用新型').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 服务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
    #     # # self.number_minus()
    #
    #     # 增值服务类型选择
    #     # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # # 11 实用新型-加强版-加急撰写
    # def patent_utility_strengthen_urgent(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'实用新型').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 服务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
    #     # # self.number_minus()
    #
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # # 12 实用新型-专家版
    # def patent_utility_expert(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'实用新型').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 服务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
    #     # # self.number_minus()
    #
    #     # 增值服务类型选择
    #     # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 13 实用新型-专家版-加急撰写
    # def patent_utility_expert_urgent(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'实用新型').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 服务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
    #     # # self.number_minus()
    #
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 14 实用新型-专家版-担保授权
    # def patent_utility_expert_guarantee(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'实用新型').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 服务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
    #     # # self.number_minus()
    #
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 15 外观设计-单一产品-标准版
    # def patent_design_single_normal(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'外观设计').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 业务类型选择
    #     # self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
    #
    #     # 服务类型选择
    #     # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 16 外观设计-单一产品-担保授权
    # def patent_design_single_guarantee(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'外观设计').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 业务类型选择
    #     # self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
    #
    #     # 服务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='liguarantee']/a").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # 17 外观设计-成套产品-标准版
    def patent_design_complete_normal(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'外观设计').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()

        # 服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        # 判断价格是否加载成功
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # # 18 外观设计-成套产品-担保授权
    # def patent_design_complete_guarantee(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'外观设计').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 业务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
    #
    #     # 服务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='liguarantee']/a").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 19 外观设计-GUI外观-标准版
    # def patent_design_GUI_normal(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'外观设计').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 业务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
    #
    #     # 服务类型选择
    #     # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()
    #
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # # 20 外观设计-GUI外观-担保授权
    # def patent_design_GUI_guarantee(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'外观设计').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 业务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
    #
    #     # 服务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='liguarantee']/a").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # 21 同日申请-标准版
    def patent_oneday_normal(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'发明新型同日申请').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        # 判断价格是否加载成功
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # # 22 同日申请-标准版-加急撰写
    # def patent_oneday_urgent(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'发明新型同日申请').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 服务类型选择
    #     # self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
    #     # # self.number_minus()
    #
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath("(.//li[@t=4]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 23 同日申请-加强版
    # def patent_oneday_strengthen(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'发明新型同日申请').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 服务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
    #     # # self.number_minus()
    #
    #     # 增值服务类型选择
    #     # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # # 24 同日申请-加强版-加急撰写
    # def patent_oneday_strengthen_urgent(self):
    #     # 选择实用新型
    #     locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'发明新型同日申请').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 服务类型选择
    #     self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
    #     # # self.number_minus()
    #
    #     # 增值服务类型选择
    #     self.driver.find_element_by_xpath("(.//li[@t=4]/a)[2]").click()
    #
    #     # 数量加1
    #     # self.number_add()
    #     # 数量减1
    #     # # self.number_minus()
    #     # 判断价格是否加载成功
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     self.apply_now()
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]
    #
    # 25 同日申请-专家版
    def patent_oneday_expert(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'发明新型同日申请').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        # 判断价格是否加载成功
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 26 同日申请-专家版-加急撰写
    def patent_oneday_expert_urgent(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'发明新型同日申请').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        self.driver.find_element_by_xpath("(.//li[@t=4]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        # 判断价格是否加载成功
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 27 同日申请-专家版-担保授权
    def patent_oneday_expert_guarantee(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'发明新型同日申请').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        self.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        # 判断价格是否加载成功
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 28 审查意见答复-发明专利
    def patent_examine_invention(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'审查意见答复').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath(".//ul[@p='16']/li[1]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        # 判断价格是否加载成功
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 29 审查意见答复-实用新型
    def patent_examine_utility(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'审查意见答复').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath(".//ul[@p='16']/li[2]/a").click()
        time.sleep(0.5)
        # # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        # 判断价格是否加载成功
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 30 审查意见答复-外观设计
    def patent_examine_design(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'审查意见答复').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath(".//ul[@p='16']/li[3]/a").click()
        time.sleep(0.5)
        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        # 判断价格是否加载成功
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 31 PCT国际申请
    def patent_PCT(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'PCT国际申请').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        # self.driver.find_element_by_xpath(".//ul[@p='16']/li[3]/a").click()
        # # # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # # self.number_minus()
        # 判断价格是否加载成功
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.driver.find_element_by_xpath(".//a[@id='gjzlapply']").click()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 32 查新检索-国内评估
    def patent_clue_domestic(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'查新检索').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
        # # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        # 判断价格是否加载成功
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 33 查新检索-全球评估
    def patent_clue_global(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'查新检索').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
        time.sleep(0.5)
        # # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 34 第三方公众意见-无需检索
    def patent_public_noneed(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'第三方公众意见').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 35 第三方公众意见-需要检索
    def patent_public_need(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'第三方公众意见').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
        time.sleep(0.5)

        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 36 授权前景分析-发明专利
    def patent_warrant_invention(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'授权前景分析').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 37 授权前景分析-实用新型
    def patent_warrant_utility(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'授权前景分析').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
        time.sleep(0.5)

        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 38 授权前景分析-外观设计
    def patent_warrant_design(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'授权前景分析').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
        time.sleep(0.5)

        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # # 39 专利稳定性分析-发明专利
    def patent_stable_invention(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利稳定性分析').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 40 专利稳定性分析-实用新型
    def patent_stable_utility(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利稳定性分析').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
        time.sleep(0.5)

        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 41 专利稳定性分析-外观设计
    def patent_stable_design(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利稳定性分析').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 42 专利权评价报告-实用新型
    def patent_evaluate_utility(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利权评价报告').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath(".//ul[@p='19']/li[1]/a").click()
        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 43 专利权评价报告-外观设计
    def patent_evaluate_design(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利权评价报告').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath(".//ul[@p='19']/li[2]/a").click()
        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 44 专利申请复审-发明专利
    def patent_review_invention(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利申请复审').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath(".//ul[@p='13']/li[1]/a").click()

        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 45 专利申请复审-实用新型
    def patent_review_utility(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利申请复审').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath(".//ul[@p='13']/li[2]/a").click()
        time.sleep(0.5)

        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 46 专利申请复审-外观设计
    def patent_review_design(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利申请复审').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        self.driver.find_element_by_xpath(".//ul[@p='13']/li[3]/a").click()
        time.sleep(0.5)

        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 47 电商侵权处理
    def patent_online_retailers(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'电商侵权处理').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        # self.driver.find_element_by_xpath(".//ul[@p='16']/li[3]/a").click()
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 48 著录项目变更
    def patent_description(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'著录项目变更').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        # self.driver.find_element_by_xpath(".//ul[@id='ul1']/li[1]/a").click()
        self.driver.find_element_by_xpath(".//ul[@id='ul1']/li[2]/a").click()
        self.driver.find_element_by_xpath(".//ul[@id='ul1']/li[3]/a").click()
        time.sleep(0.5)
        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 49 专利权恢复
    def patent_recovery(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利权恢复').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        # self.driver.find_element_by_xpath(".//ul[@p='16']/li[3]/a").click()
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 50 代缴专利年费
    def patent_replace(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'代缴专利年费').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        # self.driver.find_element_by_xpath(".//ul[@p='16']/li[3]/a").click()
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        self.driver.find_element_by_xpath(".//a[@class='apply-btn button']").click()

        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 51 专利实施许可备案
    def patent_permit(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利实施许可备案').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        # self.driver.find_element_by_xpath(".//ul[@p='16']/li[3]/a").click()
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 52 专利质押备案
    def patent_pledge(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利质押备案').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        # self.driver.find_element_by_xpath(".//ul[@p='16']/li[3]/a").click()
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 53 集成电路布图设计
    def patent_circuit(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'集成电路布图设计').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 业务类型选择
        # self.driver.find_element_by_xpath(".//ul[@p='16']/li[3]/a").click()
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        # num = 35
        time.sleep(1)
        target = self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[{}]".format(num))
        self.driver.execute_script("arguments[0].scrollIntoView();", target)
        self.driver.find_element_by_xpath(".//ul[@class='statuslist']/li[45]").click()

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

        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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

        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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

        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 61 美国商标注册
    def trademark_USA_brand(self):
        # 选择美国商标注册
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'美国商标注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
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
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 62 日本商标注册
    def trademark_Japan_brand(self):
        # 选择日本商标注册
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'日本商标注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
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
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 63 韩国商标注册
    def trademark_Korea_brand(self):
        # 选择韩国商标注册
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'韩国商标注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
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
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 64 台湾商标注册
    def trademark_Taiwan_brand(self):
        # 选择台湾商标注册
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'台湾商标注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
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
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 65 香港商标注册
    def trademark_Hongkong_brand(self):
        # 选择香港商标注册
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'香港商标注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
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
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 66 德国商标注册
    def trademark_Germany_brand(self):
        # 选择德国商标注册
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'德国商标注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
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
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 67 欧盟商标注册
    def trademark_EU_brand(self):
        # 选择欧盟商标注册
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'欧盟商标注册').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
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
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 68 马德里商标注册
    def trademark_Madrid_brand(self):
        # 选择马德里国际商标
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'马德里国际商标').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
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
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 69 非洲知识产权组织
    def trademark_Africa_knowledge(self):
        # 选择非洲知识产权组织
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'非洲知识产权组织').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
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
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)


        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)


        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)


        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)


        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)


        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)


        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)


        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)


        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)


        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

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
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)


        self.apply_now()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

        # 93 计算机软件著作权登记-36日

    # 111 国家高新企业认定-标准
    def highnew_enterprise_standard(self):
        # 选择国家高新企业认定
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'国家高新企业认定').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
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
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 112 国家高新企业认定-担保
    def highnew_enterprise_guarantee(self):
        # 选择国家高新企业认定
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'国家高新企业认定').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 案件类型
        self.driver.find_element_by_xpath(".//ul[@id='ulType']/li[2]/a").click()
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
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # # 113 商标设计套餐
    # def taocan_design_package(self):
    #     # 选择商标设计套餐
    #     locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
    #     WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #     aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar']/h2)[6]")
    #     ActionChains(self.driver).move_to_element(aa).perform()
    #     self.driver.find_element_by_link_text(u'商标设计套餐').click()
    #     # 切换至新窗口
    #     windows = self.driver.window_handles
    #     self.driver.switch_to_window(windows[-1])
    #     # 数量加减
    #     # self.number_add()
    #     # # self.number_minus()
    #     self.apply_now()
    #     # 选择商标分类
    #     self.driver.find_element_by_xpath("(.//a[@class='theme-fl-meal'])[1]").click()
    #     time.sleep(1)
    #     self.driver.find_element_by_xpath("(.//ul[@id='ulclass']/li[1])[1]").click()
    #     self.driver.find_element_by_xpath("(.//a[@class='qd'])[1]").click()
    #
    #     time.sleep(0.5)
    #     while not self.driver.find_element_by_id("totalfee").is_displayed():
    #         time.sleep(0.5)
    #     # 获取详情页 价格
    #     detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #     print("详情页价格", detail_price)
    #
    #     # 提交
    #     self.driver.find_element_by_xpath(".//a[@class='submit-btn']").click()
    #
    #     case_name, case_number, case_price, totalPrice = self.commit_order()
    #     return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 114 商标保护套餐
    def taocan_protect_package(self):
        # 选择商标设计套餐
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar']/h2)[6]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标保护套餐').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        # 选择商标分类
        self.driver.find_element_by_xpath("(.//a[@class='theme-fl-meal'])[2]").click()
        time.sleep(1)
        self.driver.find_element_by_xpath("(.//ul[@id='ulclass']/li[1])[2]").click()
        self.driver.find_element_by_xpath("(.//a[@class='qd'])[2]").click()

        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.driver.find_element_by_xpath(".//a[@class='submit-btn']").click()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]

    # 115 商标复审套餐
    def taocan_review_package(self):
        # 选择商标设计套餐
        locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar']/h2)[6]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'商标复审套餐').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 数量加减
        # self.number_add()
        # # self.number_minus()
        self.apply_now()
        # 选择商标分类
        self.driver.find_element_by_xpath("(.//a[@class='theme-fl-meal'])[3]").click()
        time.sleep(1)
        self.driver.find_element_by_xpath("(.//ul[@id='ulclass']/li[1])[3]").click()
        self.driver.find_element_by_xpath("(.//a[@class='qd'])[3]").click()
        time.sleep(0.5)
        while not self.driver.find_element_by_id("totalfee").is_displayed():
            time.sleep(0.5)
        # 获取详情页 价格
        detail_price = self.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
        print("详情页价格", detail_price)

        self.driver.find_element_by_xpath(".//a[@class='submit-btn']").click()
        case_name, case_number, case_price, totalPrice = self.commit_order()
        return windows, [case_name, case_number, detail_price, case_price, totalPrice]
