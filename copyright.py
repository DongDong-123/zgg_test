import time

from selenium.webdriver.common.action_chains import ActionChains

from front_login import *
from db import DbOperate
from Common import Common


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
        self.common = Common()
        self.timetemp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())  # 存储Excel表格文件名编号
        # 每个案件的数量
        self.number = 1
        self.dboperate = DbOperate()
        self.db = "copyright"

    # 执行下单
    def execute_function(self, callback):
        try:
            eval("self.{}()".format(callback))
        except Exception as e:
            print("错误信息:", e)
            self.common.write_error_log(callback)
            time.sleep(0.5)
            self.common.write_error_log(str(e))

    # 计算机软件著作权登记
    def copyright_computer_software_01(self):
        all_type = [u'计算机作品著作权登记']
        type_code = ["computer"]
        for index, copyright_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(u'计算机软件著作权登记').click()
                    # 切换至新窗口
                    self.common.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.common.windows[-1])
                    # 服务类型：
                    # 1-6，36个工作日-3个工作日
                    # 随机选择一个类型
                    # for num in [random.randint(range(1, 7))]:
                    for num in range(1, 3):
                        self.common.driver.find_element_by_xpath("//ul[@p='232']/li[{}]/a".format(num)).click()
                        # 数量加减
                        # self.common.number_add()
                        # self.common.number_minus()
                        time.sleep(0.5)
                        while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.common.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.common.apply_now()
                        case_name, case_number, case_price, totalprice = self.common.commit_order()
                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.common.row = self.common.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.common.pay(self.common.windows)
                        all_info.append(pay_totalprice)
                        print(all_info, pay_totalprice)
                        if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) \
                                and float(all_info[4]) == float(all_info[2]):
                            status = 'True'
                        else:
                            status = "False"
                        all_info.append(status)
                        self.common.excel_number(all_info)
                        time.sleep(1)
                        self.common.driver.back()
                        self.common.driver.back()
                        self.common.driver.back()
                        screen_name = "_".join([case_name, case_number, case_price])
                        self.common.qr_shotscreen(screen_name)
                        self.common.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.common.windows[0])
                self.common.closed_windows(1)
        time.sleep(1)

    # 美术作品著作权登记-30日
    def copyright_art_works_01(self):
        # 选择美术作品著作权登记
        all_type = [u'美术作品著作权登记']
        type_code = ["art"]
        for index, copyright_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(copyright_type).click()
                    # 切换至新窗口
                    self.common.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.common.windows[-1])
                    # 30个工作日
                    for num in range(1, 3):
                        self.common.driver.find_element_by_xpath("//ul[@p='107538']/li[{}]/a".format(num)).click()
                        # 数量加减
                        # self.common.number_add()
                        # # self.common.number_minus()
                        time.sleep(0.5)
                        while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.common.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.common.apply_now()
                        case_name, case_number, case_price, totalprice = self.common.commit_order()

                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.common.row = self.common.row + 1
                        time.sleep(0.5)

                        pay_totalprice = self.common.pay(self.common.windows)
                        all_info.append(pay_totalprice)
                        print(all_info, pay_totalprice)
                        if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice)\
                                and float(all_info[4]) == float(all_info[2]):
                            status = 'True'
                        else:
                            status = "False"
                        all_info.append(status)
                        self.common.excel_number(all_info)
                        time.sleep(1)
                        self.common.driver.back()
                        self.common.driver.back()
                        self.common.driver.back()
                        screen_name = "_".join([case_name,case_number,case_price])
                        self.common.qr_shotscreen(screen_name)
                        self.common.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.common.windows[0])
                self.common.closed_windows(1)
        time.sleep(1)

    # 文字作品著作权登记-30日
    def copyright_writings_01(self):
        # 选择文字作品著作权登记
        all_type = [u'汇编作品著作权登记', u'文字作品著作权登记', u'摄影作品著作权登记', u'电影作品著作权登记', u'音乐作品著作权登记', u'曲艺作品著作权登记']
        type_code = ["compile", "word", "photography", "film", "music", "drama"]
        for index, copyright_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "//div[@class='isnav-first']/div[1]/h2")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[3]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(copyright_type).click()
                    # 切换至新窗口
                    self.common.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.common.windows[-1])
                    # 案件类型：
                    for num in range(1, 2):
                        self.common.driver.find_element_by_xpath("//ul[@id='ulType']/li[{}]/a".format(num)).click()
                        # 数量加减
                        # self.common.number_add()
                        # # self.common.number_minus()
                        time.sleep(0.5)
                        while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.common.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.common.apply_now()
                        case_name, case_number, case_price, totalprice = self.common.commit_order()

                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.common.row = self.common.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.common.pay(self.common.windows)
                        all_info.append(pay_totalprice)
                        print(all_info, pay_totalprice)
                        if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) \
                                and float(all_info[4]) == float(all_info[2]):
                            status = 'True'
                        else:
                            status = "False"
                        all_info.append(status)
                        self.common.excel_number(all_info)

                        time.sleep(1)
                        self.common.driver.back()
                        self.common.driver.back()
                        self.common.driver.back()
                        screen_name = "_".join([case_name, case_number, case_price])
                        self.common.qr_shotscreen(screen_name)
                        self.common.closed_windows(1)
                        self.dboperate.del_elem(type_code[index], num)
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.common.windows[0])
                self.common.closed_windows(1)
        time.sleep(1)
