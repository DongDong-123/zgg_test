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


# class Delete_case:

alread = ["copyright_computer_software_05", "patent_evaluate_utility", "copyright_compilation_02",
          "trademark_brand_extension_01", "copyright_movie_works_01", "copyright_photography_05",
          "trademark_prove_brand", "patent_pledge", "patent_oneday_normal", "trademark_reissue_brand",
          "trademark_germany_brand", "copyright_computer_software_03", "taocan_design_package", "copyright_writings_01",
          "copyright_music_works_03", "trademark_brand_revoke_apply", "trademark_group_brand", "trademark_prove_brand",
          "patent_examine_invention", "trademark_brand_litigation", "trademark_brand_cancel", "patent_stable_utility",
          "copyright_music_works_05", "patent_review_design", "trademark_guarantee_register", "copyright_quyi_works_01",
          "copyright_movie_works_04", "trademark_ordinary_reject", "patent_review_utility", "copyright_quyi_works_05",
          "patent_evaluate_utility", "trademark_germany_brand", "patent_oneday_expert", "trademark_brand_extension_03",
          "copyright_computer_software_04", "copyright_writings_05", "taocan_review_package",
          "trademark_objection_answer", "copyright_writings_06", "trademark_urgent_register",
          "copyright_movie_works_01", "patent_warrant_invention", "trademark_brand_permit", "copyright_compilation_05",
          "patent_warrant_utility", "patent_oneday_expert_guarantee", "copyright_computer_software_01",
          "trademark_EU_brand", "copyright_photography_06", "copyright_computer_software_06", "patent_replace",
          "copyright_writings_04", "trademark_brand_permit_02", "trademark_korea_brand", "trademark_madrid_brand",
          "patent_permit", "highnew_enterprise_standard", "copyright_music_works_02", "trademark_brand_amend",
          "patent_public_need", "trademark_brand_revoke_answer", "trademark_objection_apply", "patent_circuit",
          "patent_stable_invention"]


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
        # self.excel_number()
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
