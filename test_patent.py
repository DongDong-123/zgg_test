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
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 2 发明专利-标准服务-加急撰写
    def patent_invention_normal_urgent(self):
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
        # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
        # ActionChains(self.driver).move_to_element(aa).perform()
        # # self.number_minus()
        # 增值服务类型选择
        self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 3 发明专利-加强版
    def patent_invention_strengthen(self):
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
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
        # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
        # ActionChains(self.driver).move_to_element(aa).perform()
        # self.number_minus()
        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 4 发明专利-加强版-加急撰写
    def patent_invention_strengthen_urgent(self):
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
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
        # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
        # ActionChains(self.driver).move_to_element(aa).perform()
        # self.number_minus()
        # 增值服务类型选择
        self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()
        self.apply_now()
        self.commit_order()

        return windows

    # 5 发明专利-专家版
    def patent_invention_expert(self):
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
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
        # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
        # ActionChains(self.driver).move_to_element(aa).perform()
        # self.number_minus()
        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 6 发明专利-专家版-加急撰写
    def patent_invention_expert_urgent(self):
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
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
        # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
        # ActionChains(self.driver).move_to_element(aa).perform()
        # self.number_minus()
        # 增值服务类型选择
        self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 7 发明专利-专家版-担保授权
    def patent_invention_expert_guarantee(self):
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
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
        # aa1=self.driver.find_element_by_xpath("//div[@class='ui-zlsq-gwc']/a[1]")
        # ActionChains(self.driver).move_to_element(aa).perform()
        # self.number_minus()
        # 增值服务类型选择
        self.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 8 实用新型-标准版
    def patent_utility_normal(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'实用新型').click()
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

        self.apply_now()
        self.commit_order()

        return windows

    # 9 实用新型-标准版-加急撰写
    def patent_utility_normal_urgent(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'实用新型').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        # self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        self.driver.find_element_by_xpath("(.//li[@t=2]/a)[1]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 10 实用新型-加强版
    def patent_utility_strengthen(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'实用新型').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 11 实用新型-加强版-加急撰写
    def patent_utility_strengthen_urgent(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'实用新型').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 12 实用新型-专家版
    def patent_utility_expert(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'实用新型').click()
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

        self.apply_now()
        self.commit_order()

        return windows

    # 13 实用新型-专家版-加急撰写
    def patent_utility_expert_urgent(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'实用新型').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        # 服务类型选择
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 14 实用新型-专家版-担保授权
    def patent_utility_expert_guarantee(self):
        # 选择实用新型
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'实用新型').click()
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

        self.apply_now()
        self.commit_order()

        return windows

    # 15 外观设计-单一产品-标准版
    def patent_design_single_normal(self):
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
        # self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()

        # 服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 16 外观设计-单一产品-担保授权
    def patent_design_single_guarantee(self):
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
        # self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()

        # 服务类型选择
        self.driver.find_element_by_xpath("//*[@id='liguarantee']/a").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

    # 18 外观设计-成套产品-担保授权
    def patent_design_complete_guarantee(self):
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
        self.driver.find_element_by_xpath("//*[@id='liguarantee']/a").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 19 外观设计-GUI外观-标准版
    def patent_design_GUI_normal(self):
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
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()

        # 服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=1]/a)[2]").click()

        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 20 外观设计-GUI外观-担保授权
    def patent_design_GUI_guarantee(self):
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
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[3]/a").click()

        # 服务类型选择
        self.driver.find_element_by_xpath("//*[@id='liguarantee']/a").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

    # 22 同日申请-标准版-加急撰写
    def patent_oneday_urgent(self):
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
        # self.driver.find_element_by_xpath("//*[@id='ulType']/li[1]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        self.driver.find_element_by_xpath("(.//li[@t=4]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 23 同日申请-加强版
    def patent_oneday_strengthen(self):
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
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 24 同日申请-加强版-加急撰写
    def patent_oneday_strengthen_urgent(self):
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
        self.driver.find_element_by_xpath("//*[@id='ulType']/li[2]/a").click()
        # # self.number_minus()

        # 增值服务类型选择
        self.driver.find_element_by_xpath("(.//li[@t=4]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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
        # # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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
        # # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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

        self.driver.find_element_by_xpath(".//a[@id='gjzlapply']").click()
        self.commit_order()

        return windows

    # 32 查新线索-国内评估
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

        self.apply_now()
        self.commit_order()

        return windows

    # 33 查新线索-全球评估
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
        # # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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
        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

    # 39 专利稳定性分析-发明专利
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

        self.apply_now()
        self.commit_order()

        return windows

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
        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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
        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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
        # self.number_minus()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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
        # self.number_minus()

        # 增值服务类型选择
        # self.driver.find_element_by_xpath("(.//li[@t=2]/a)[2]").click()

        # 数量加1
        # self.number_add()
        # 数量减1
        # # self.number_minus()

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.driver.find_element_by_xpath(".//a[@class='apply-btn button']").click()

        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows

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

        self.apply_now()
        self.commit_order()

        return windows
