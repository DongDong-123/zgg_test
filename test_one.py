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
        self.db = "case"

    # 执行下单
    def execute_function(self, callback):
        try:
            eval("self.{}()".format(callback))
        except Exception as e:
            print("错误信息:", e)
            self.common.write_error_log(callback)
            time.sleep(0.5)
            self.common.write_error_log(str(e))

    # 商标续展--（续展申请、宽展申请、补发续展证明）
    def trademark_brand_extension_01(self):
        this_type = u'商标续展'
        if self.dboperate.is_member(self.db, this_type):
            locator = (By.XPATH, ".//div[@class='isnav-first']/div[1]/h2")
            WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
            aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
            ActionChains(self.common.driver).move_to_element(aa).perform()
            self.common.driver.find_element_by_link_text(this_type).click()
            # 切换至新窗口
            self.common.windows = self.common.driver.window_handles
            self.common.driver.switch_to_window(self.common.windows[-1])
            # 业务方向:续展申请、宽展申请、补发续展证明
            for num in range(1, 4):
                try:
                    self.common.driver.find_element_by_xpath(".//ul[@p='2274']/li[{}]/a".format(num)).click()
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
                    pay_total_price = self.common.pay(self.common.windows)
                    all_info.append(pay_total_price)
                    print(all_info, pay_total_price)
                    if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_total_price) and \
                            float(all_info[4]) == float(all_info[2]):
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
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.common.windows[1])
            print("=============2=====================")
            # self.common.closed_windows(self.common.windows[1])
            print("===============1====================")
            self.dboperate.del_elem(self.db, this_type)
            print("================3=====================")
            time.sleep(1)

    # 商标许可备案 --(许可备案、变更（被）许可人名称、许可提前终止)
    # def trademark_brand_permit(self):
    #     this_type = u'商标许可备案'
    #     if self.dboperate.is_member(self.db, this_type):
    #         locator = (By.XPATH, ".//div[@class='isnav-first']/div[1]/h2")
    #         WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
    #         aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[2]")
    #         ActionChains(self.common.driver).move_to_element(aa).perform()
    #         self.common.driver.find_element_by_link_text(this_type).click()
    #         # 切换至新窗口
    #         self.common.windows = self.common.driver.window_handles
    #         self.common.driver.switch_to_window(self.common.windows[-1])
    #         # 业务方向:许可备案、变更（被）许可人名称、许可提前终止
    #         for num in range(1, 4):
    #             try:
    #                 self.common.driver.find_element_by_xpath(".//ul[@p='2278']/li[{}]/a".format(num)).click()
    #                 # 数量加减
    #                 # self.common.number_add()
    #                 # # self.common.number_minus()
    #                 time.sleep(0.5)
    #                 while not self.common.driver.find_element_by_id("totalfee").is_displayed():
    #                     time.sleep(0.5)
    #                 # 获取详情页 价格
    #                 detail_price = self.common.driver.find_element_by_xpath("(.//div[@class='sames']//label[@id='totalfee'])").text
    #                 print("详情页价格", detail_price)
    #
    #                 self.common.apply_now()
    #                 case_name, case_number, case_price, totalprice = self.common.commit_order()
    #                 all_info = [case_name, case_number, detail_price, case_price, totalprice]
    #                 self.common.row = self.common.row + 1
    #                 time.sleep(0.5)
    #                 pay_totalprice = self.common.pay(self.common.windows)
    #                 all_info.append(pay_totalprice)
    #                 print(all_info, pay_totalprice)
    #                 if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
    #                         float(all_info[4]) == float(all_info[2]):
    #                     status = 'True'
    #                 else:
    #                     status = "False"
    #                 all_info.append(status)
    #                 self.common.excel_number(all_info)
    #                 time.sleep(1)
    #                 self.common.driver.back()
    #                 self.common.driver.back()
    #                 self.common.driver.back()
    #                 screen_name = "_".join([case_name, case_number, case_price])
    #                 self.common.qr_shotscreen(screen_name)
    #
    #             except Exception as e:
    #                 print(e)
    #                 self.common.driver.switch_to_window(self.common.windows[1])
    #         self.common.closed_windows(self.common.windows[1])
    #         self.dboperate.del_elem(self.db, this_type)
    #         time.sleep(1)
