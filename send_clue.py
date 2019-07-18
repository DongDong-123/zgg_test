import os
import random
import time

import xlwt
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from front_login import *
from readConfig import ReadConfig

driver = webdriver.Chrome()
driver.maximize_window()
driver.get(ReadConfig().get_root_url())


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
        self.driver = driver
        # self.driver = front_login(self.USER, self.PASSWORD)
        # Excel写入
        self.row = 0
        self.workbook = xlwt.Workbook(encoding='utf-8')
        self.booksheet = self.workbook.add_sheet('Sheet1')
        self.timetemp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())  # 存储Excel表格文件名编号
        # 每个案件的数量
        self.number = 1
        self.report_path = ReadConfig().save_report()
        self.case_count = FunctionName.get_count
        self.phone = 16619923387
        self.file_name = self.save_clue_log(("手机号", "线索内容", "发送状态", "其他"))

    def execute_function(self, callback):
        try:
            back_parm = eval("self.{}()".format(callback))
            # self.save_clue_log(eval("self.{}()".format(callback)))
            # for elem in eval("self.{}()".format(callback)):
            #     print("elem:", elem)
            self.row = self.row + 1
            self.save_clue_log(back_parm)
            # time.sleep(0.5)
            time.sleep(0.5)

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

    def save_clue_log(self, args):
        # 获取案件名称、案件号
        if args:
            n = 0
            # self.booksheet.write(self.row, n, n + 1)
            # n += 1
            for elem in args:
                self.booksheet.write(self.row, n, elem)
                self.booksheet.col(n).width = 300 * 28
                n += 1

        path = os.path.join(self.report_path, "clue_{}.xls".format(self.timetemp))
        self.workbook.save(path)

    # 关闭窗口
    def closed_windows(self):
        self.driver.close()
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])
        self.driver.close()
        self.driver.switch_to_window(windows[0])


    def check_rasult(self):
        result = self.driver.find_element_by_xpath("(.//div[@class='them-edit-dialog']/div[@class='comm']/p)").text
        print("result", result, type(result))
        if "您的查询资料已提交" in result:
            res = "True"
        else:
            res = "False"
        return res


    # 专利布局规划
    def patent_clue_01(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利布局规划').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)

        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])

        return (self.phone, case_name, res)

    # 研发立项支持
    def patent_clue_02(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'研发立项支持').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)

        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 竞争对手监测
    def patent_clue_32(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'竞争对手监测').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 高价值专利培育
    def patent_clue_33(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'高价值专利培育').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 专利价值评估
    def patent_clue_03(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利价值评估').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 专利尽职调查
    def patent_clue_04(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利尽职调查').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 专利价值评估
    def patent_clue_05(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利价值评估').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 专利侵权诉讼
    def patent_clue_06(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利侵权诉讼').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])

        return (self.phone, case_name, res)
    # 优先审查
    def patent_clue_07(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'优先审查').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 海外专利流程管理
    def patent_clue_08(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'海外专利流程管理').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 知识产权海关备案
    def patent_clue_09(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'知识产权海关备案').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()

        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 植物新品种
    def patent_clue_10(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'植物新品种').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # logo设计
    def patent_clue_11(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'logo设计').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 双软认证
    def patent_clue_12(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'双软认证').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # ISO9001质量管理体系认证
    def patent_clue_13(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'ISO9001质量管理体系认证').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 软件产品登记测试报告
    def patent_clue_14(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'软件产品登记测试报告').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 科技成果评价
    def patent_clue_15(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'科技成果评价').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 贯标申请服务
    def patent_clue_16(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'贯标申请服务').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 知识产权保护
    def patent_clue_17(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'知识产权保护').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 专利风险预警
    def patent_clue_18(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利风险预警').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 专利侵权对抗
    def patent_clue_19(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利侵权对抗').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 专利风险预警
    def patent_clue_20(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利风险预警').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 无效/异议提起
    def patent_clue_21(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'无效/异议提起').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 合同审核
    def patent_clue_22(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'合同审核').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 知识产权维权
    def patent_clue_23(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'知识产权维权').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 咨询分析报告
    def patent_clue_24(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'咨询分析报告').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 知识产权运营
    def patent_clue_25(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'知识产权运营').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 知识产权顾问
    def patent_clue_26(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'知识产权顾问').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']/h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 海外国家专利申请-其他国家
    def patent_clue_27(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'海外国家专利申请').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 选择国家，范围 1-6
        self.driver.find_element_by_xpath("(.//li[@origin='92'])").click()
        time.sleep(0.5)
        # 选择类型范围  1：71-72；2:81-82；3:91-93;4:101-103;5:111-113;6:121-122
        # self.driver.find_element_by_xpath("(.//li[@pt='71'])").click()
        # time.sleep(0.5)

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']//h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 海外国家专利申请--已测试
    def patent_clue_28(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'海外国家专利申请').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 随机选择一个国家
        num = random.randint(1, 6)
        print(num)
        self.driver.find_element_by_xpath("(.//li[@t='{}'])".format(num)).click()
        nation = self.driver.find_element_by_xpath("(.//li[@t='{}'])".format(num)).text
        time.sleep(0.5)
        # 选择类型 1：71-72；2:81-82；3:91-93;4:101-103;5:111-113;6:121-122
        nation_type = {}
        nation_type.update({
            "1": [71, 72], "2": [81, 82], "3": [91, 92, 93], "4": [101, 102, 103], "5": [111, 112, 113],
            "6": [121, 122]})
        # 随机选择一个业务类型
        type_num = nation_type["{}".format(num)]
        self.driver.find_element_by_xpath("(.//li[@pt='{}'])".format(random.choice(type_num))).click()
        time.sleep(0.5)

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']//h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name + "-" + nation)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 新产品风险预警（FTO）
    def patent_clue_29(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'新产品风险预警(FTO)').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 随机选择一个类型
        num = random.randint(1, 2)
        print(num)
        self.driver.find_element_by_xpath("(.//li[@t='{}'])".format(num)).click()
        case_type = self.driver.find_element_by_xpath("(.//li[@t='{}'])".format(num)).text
        time.sleep(0.5)

        # 随机选择一个业务类型(改版前)
        # self.driver.find_element_by_xpath("(.//ul[@id='ulType']/li[{}]/a)".format(random.choice([1, 2, 3]))).click()
        # time.sleep(0.5)

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']//h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name + "-" + case_type)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 侵权风险分析
    def patent_clue_30(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'侵权风险分析').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 随机选择一个类型
        num = random.randint(1, 2)
        print(num)
        self.driver.find_element_by_xpath("(.//ul[@id='zlUlType']/li[{}]/a)".format(num)).click()
        case_type = self.driver.find_element_by_xpath("(.//ul[@id='zlUlType']/li[{}]/a)".format(num)).text
        time.sleep(0.5)

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']//h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name + "-" + case_type)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 无效证据检索
    def patent_clue_31(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'无效证据检索').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 随机选择一个类型
        num = random.randint(1, 3)
        print(num)
        self.driver.find_element_by_xpath("(.//ul[@id='zlUlType']/li[{}]/a)".format(num)).click()
        time.sleep(0.5)
        case_type = self.driver.find_element_by_xpath("(.//ul[@id='zlUlType']/li[{}]/a)".format(num)).text
        time.sleep(0.5)

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']//h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name + "-" + case_type)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 专利无效宣告
    def patent_clue_36(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利无效宣告').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 随机选择一个类型
        num = random.randint(1, 3)
        print(num)
        self.driver.find_element_by_xpath("(.//ul[@p='14']/li[{}]/a)".format(num)).click()
        time.sleep(0.5)
        case_type = self.driver.find_element_by_xpath("(.//ul[@p='14']/li[{}]/a)".format(num)).text
        time.sleep(0.5)

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']//h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name + "-" + case_type)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 专利无效答辩
    def patent_clue_37(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'专利无效答辩').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 随机选择一个类型
        num = random.randint(1, 3)
        print(num)
        self.driver.find_element_by_xpath("(.//ul[@p='15']/li[{}]/a)".format(num)).click()
        time.sleep(0.5)
        case_type = self.driver.find_element_by_xpath("(.//ul[@p='15']/li[{}]/a)".format(num)).text
        time.sleep(0.5)

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']//h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name + "-" + case_type)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 行业专利导航
    def patent_clue_35(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'行业专利导航').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 随机选择一个类型
        num = random.randint(1, 2)
        print(num)
        self.driver.find_element_by_xpath("(.//ul[@p='23']/li[{}]/a)".format(num)).click()
        time.sleep(0.5)
        case_type = self.driver.find_element_by_xpath("(.//ul[@p='23']/li[{}]/a)".format(num)).text
        time.sleep(0.5)

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']//h3)").text
        self.driver.find_element_by_id("consult_phone").send_keys(self.phone)
        self.driver.find_element_by_id("consult_contact").send_keys(case_name + "-" + case_type)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res)

    # 软件开发
    def patent_clue_34(self):
        locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[2]")
        WebDriverWait(self.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
        aa = self.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[5]")
        ActionChains(self.driver).move_to_element(aa).perform()
        self.driver.find_element_by_link_text(u'软件开发').click()
        # 切换至新窗口
        windows = self.driver.window_handles
        self.driver.switch_to_window(windows[-1])

        # 随机选择一个类型
        num = random.randint(1, 5)
        text = "软件开发需求"
        self.driver.find_element_by_class_name("soft-textarea").send_keys(text)
        # demand = self.driver.find_element_by_xpath("(.//textarea)").text

        self.driver.find_element_by_xpath("(.//ul[@class='soft-optaion fl']/label[{}]/li)".format(num)).click()
        time.sleep(0.5)
        price = self.driver.find_element_by_xpath("(.//ul[@class='soft-optaion fl']/label[{}]/li)".format(num)).text
        time.sleep(0.5)

        # 输入联系方式/联系人
        case_name = self.driver.find_element_by_xpath("(.//div[@class='ui-apply-tit']//h3)").text
        self.driver.find_element_by_id("yourphone").send_keys(self.phone)
        self.driver.find_element_by_id("yourname").send_keys(case_name + text + "-" + price)

        # 提交需求
        self.driver.find_element_by_xpath("(.//div[@class='ui-zlsq-gwc']/a)[1]").click()
        time.sleep(0.5)
        # 判断是否成功推送
        res = self.check_rasult()
        self.driver.find_element_by_link_text(u'确定').click()
        self.driver.close()
        self.driver.switch_to_window(windows[0])
        return (self.phone, case_name, res, text, price)


if __name__ == "__main__":
    qq = Execute()
    qq.patent_clue_01()
    qq.patent_clue_02()
