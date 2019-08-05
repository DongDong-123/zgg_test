import random
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

        attrs["__FuncCount__"] = count
        return type.__new__(cls, name, bases, attrs)


class Execute(object, metaclass=FunctionName):
    def __init__(self):
        self.common = Common()
        self.timetemp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())  # 存储Excel表格文件名编号
        self.db = "case"
        self.dboperate = DbOperate()

    # 执行下单
    def execute_function(self, callback):
        try:
            eval("self.{}()".format(callback))
        except Exception as e:
            print("错误信息:", e)
            self.common.write_error_log(callback)
            time.sleep(0.5)
            self.common.write_error_log(str(e))

    # 关闭窗口
    def closed_windows(self, num):
        self.windows = self.common.driver.window_handles
        for n in range(num + 1, len(self.windows)):
            self.common.driver.switch_to_window(self.windows[n])
            self.common.driver.close()
        self.common.driver.switch_to_window(self.windows[num])

    # 1 发明专利,实用新型，同日申请
    def patent_invention_normal(self):
        all_type = [u'发明专利', u'实用新型', u'发明新型同日申请']
        type_code = ["patent", "utility", "oneday"]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    self.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.windows[-1])
                    for num in range(1, 8):
                        if self.dboperate.is_member(type_code[index], num):
                            print("num:", num)
                            # 服务类型选择，
                            if num < 4:
                                self.common.driver.find_element_by_xpath(
                                    ".//ul[@id='ulType']/li[{}]/a".format(num)).click()
                            elif num == 4:
                                self.common.driver.find_element_by_xpath(".//ul[@id='ulType']/li[1]/a").click()
                                # 消除悬浮窗的影响
                                temp = self.common.driver.find_element_by_xpath(".//ul[@id='ulType']/li[2]/a")
                                ActionChains(self.common.driver).move_to_element(temp).perform()
                                self.common.driver.find_element_by_xpath(
                                    ".//div[@class='ui-increment-zl']//li[1]/a").click()
                            elif num == 5:
                                self.common.driver.find_element_by_xpath(".//ul[@id='ulType']/li[2]/a").click()
                                self.common.driver.find_element_by_xpath(
                                    ".//div[@class='ui-increment-zl']//li[1]/a").click()
                            elif num == 6:
                                self.common.driver.find_element_by_xpath(".//ul[@id='ulType']/li[3]/a").click()
                                self.common.driver.find_element_by_xpath(
                                    ".//div[@class='ui-increment-zl']//li[1]/a").click()
                            else:
                                self.common.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()
                            # 数量加1
                            # self.common.number_add()
                            # 数量减1
                            # # self.common.number_minus()
                            # 判断价格是否加载成功
                            while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                                time.sleep(0.5)
                            # 获取详情页 价格
                            detail_price = self.common.driver.find_element_by_xpath(
                                "(.//div[@class='sames']//label[@id='totalfee'])").text
                            print("详情页价格", detail_price)

                            self.common.apply_now()
                            # 获取下单页价格
                            case_name, case_number, case_price, totalprice = self.common.commit_order()
                            all_info = [case_name, case_number, detail_price, case_price, totalprice]
                            self.common.row = self.common.row + 1
                            time.sleep(0.5)
                            pay_totalprice = self.common.pay(self.windows)
                            all_info.append(pay_totalprice)
                            print(all_info, pay_totalprice)
                            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(
                                    pay_totalprice) and \
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
                            self.closed_windows(1)
                            self.dboperate.del_elem(type_code[index], num)
                            time.sleep(1)
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
                time.sleep(1)

    # 2 外观设计
    def patent_design(self):
        all_type = [u'外观设计']
        type_code = ["design"]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    self.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.windows[-1])
                    for num in range(1, 7):
                        if self.dboperate.is_member(type_code[index], num):
                            # 服务类型选择，
                            if num <= 3:
                                self.common.driver.find_element_by_xpath(
                                    ".//ul[@id='ulType']/li[{}]/a".format(num)).click()
                            elif num == 4:
                                self.common.driver.find_element_by_xpath(".//ul[@id='ulType']/li[1]/a").click()
                                self.common.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()
                            elif num == 5:
                                self.common.driver.find_element_by_xpath(".//ul[@id='ulType']/li[2]/a").click()
                                self.common.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()
                            elif num == 6:
                                self.common.driver.find_element_by_xpath(".//ul[@id='ulType']/li[3]/a").click()
                                self.common.driver.find_element_by_xpath(".//li[@id='liguarantee']/a").click()
                            # 数量加1
                            # self.common.number_add()
                            # 数量减1
                            # # self.common.number_minus()
                            # 判断价格是否加载成功
                            while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                                time.sleep(0.5)
                            # 获取详情页 价格
                            detail_price = self.common.driver.find_element_by_xpath(
                                "(.//div[@class='sames']//label[@id='totalfee'])").text
                            print("详情页价格", detail_price)

                            self.common.apply_now()
                            # 获取下单页价格
                            case_name, case_number, case_price, totalprice = self.common.commit_order()
                            all_info = [case_name, case_number, detail_price, case_price, totalprice]
                            self.common.row = self.common.row + 1
                            time.sleep(0.5)
                            pay_totalprice = self.common.pay(self.windows)
                            all_info.append(pay_totalprice)
                            print(all_info, pay_totalprice)
                            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(
                                    pay_totalprice) and \
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
                            self.closed_windows(1)
                            self.dboperate.del_elem(type_code[index], num)
                            time.sleep(1)
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
                time.sleep(1)

    # 3 专利申请复审,审查意见答复 -（发明专利，实用新型，外观设计）
    def patent_review_invention(self):
        all_type = [u'专利申请复审', u'审查意见答复']
        type_code = ["patent_recheck", "patent_answer"]
        ul_index = [13, 16]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    self.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.windows[-1])
                    # 业务类型选择
                    for num in range(1, 4):
                        if self.dboperate.is_member(type_code[index], num):
                            self.common.driver.find_element_by_xpath(
                                ".//ul[@p='{}']/li[{}]/a".format(ul_index[index], num)).click()
                            # 数量加1
                            # self.common.number_add()
                            # 数量减1
                            # # self.common.number_minus()
                            while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                                time.sleep(0.5)
                            # 获取详情页 价格
                            detail_price = self.common.driver.find_element_by_xpath(
                                "(.//div[@class='sames']//label[@id='totalfee'])").text
                            print("详情页价格", detail_price)

                            self.common.apply_now()
                            case_name, case_number, case_price, totalprice = self.common.commit_order()

                            all_info = [case_name, case_number, detail_price, case_price, totalprice]
                            self.common.row = self.common.row + 1
                            time.sleep(0.5)
                            pay_totalprice = self.common.pay(self.windows)
                            all_info.append(pay_totalprice)
                            print(all_info, pay_totalprice)
                            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(
                                    pay_totalprice) and \
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

                            self.closed_windows(1)
                            self.dboperate.del_elem(type_code[index], num)
                            time.sleep(1)
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
        time.sleep(1)

    # 4 查新检索-国内评估，全球评估,第三方公众意见-无需检索，需要检索
    def patent_clue_domestic_1(self):
        all_type = [u'查新检索', u'第三方公众意见']
        type_code = ["patent_clue", "patent_public"]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    self.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.windows[-1])
                    # 业务类型选择
                    for num in range(1, 3):
                        if self.dboperate.is_member(type_code[index], num):
                            self.common.driver.find_element_by_xpath(".//ul[@id='ulType']/li[{}]/a".format(num)).click()
                            # 数量加1
                            # self.common.number_add()
                            # 数量减1
                            # # self.common.number_minus()
                            while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                                time.sleep(0.5)
                            # 获取详情页 价格
                            detail_price = self.common.driver.find_element_by_xpath(
                                "(.//div[@class='sames']//label[@id='totalfee'])").text
                            print("详情页价格", detail_price)

                            self.common.apply_now()
                            case_name, case_number, case_price, totalprice = self.common.commit_order()

                            all_info = [case_name, case_number, detail_price, case_price, totalprice]
                            self.common.row = self.common.row + 1
                            time.sleep(0.5)
                            pay_totalprice = self.common.pay(self.windows)
                            all_info.append(pay_totalprice)
                            print(all_info, pay_totalprice)
                            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(
                                    pay_totalprice) and \
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

                            self.closed_windows(1)
                            self.dboperate.del_elem(type_code[index], num)
                            time.sleep(1)
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
        time.sleep(1)

    # 5 专利授权前景分析,专利稳定性分析 -（发明专利，实用新型，外观设计）
    def patent_warrant_invention_1(self):
        all_type = [u'授权前景分析', u'专利稳定性分析']
        type_code = ["patent_warrant", "patent_stable"]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    self.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.windows[-1])
                    # 业务类型选择
                    for num in range(1, 4):
                        if self.dboperate.is_member(type_code[index], num):
                            self.common.driver.find_element_by_xpath(".//ul[@id='ulType']/li[{}]/a".format(num)).click()
                            # 数量加1
                            # self.common.number_add()
                            # 数量减1
                            # # self.common.number_minus()
                            while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                                time.sleep(0.5)
                            # 获取详情页 价格
                            detail_price = self.common.driver.find_element_by_xpath(
                                "(.//div[@class='sames']//label[@id='totalfee'])").text
                            print("详情页价格", detail_price)

                            self.common.apply_now()
                            case_name, case_number, case_price, totalprice = self.common.commit_order()

                            all_info = [case_name, case_number, detail_price, case_price, totalprice]
                            self.common.row = self.common.row + 1
                            time.sleep(0.5)
                            pay_totalprice = self.common.pay(self.windows)
                            all_info.append(pay_totalprice)
                            print(all_info, pay_totalprice)
                            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(
                                    pay_totalprice) and \
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

                            self.closed_windows(1)
                            self.dboperate.del_elem(type_code[index], num)
                            time.sleep(1)
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
        time.sleep(1)

    # 6 利权评价报告-实用新型，外观设计
    def patent_evaluate_utility(self):
        all_type = [u'专利权评价报告']
        type_code = ["patent_evaluate"]
        ul_index = [19]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    self.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.windows[-1])
                    # 业务类型选择
                    for num in range(1, 3):
                        if self.dboperate.is_member(type_code[index], num):
                            self.common.driver.find_element_by_xpath(
                                ".//ul[@p='{}']/li[{}]/a".format(ul_index[index], num)).click()
                            # 数量加1
                            # self.common.number_add()
                            # 数量减1
                            # # self.common.number_minus()
                            while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                                time.sleep(0.5)
                            # 获取详情页 价格
                            detail_price = self.common.driver.find_element_by_xpath(
                                "(.//div[@class='sames']//label[@id='totalfee'])").text
                            print("详情页价格", detail_price)

                            self.common.apply_now()
                            case_name, case_number, case_price, totalprice = self.common.commit_order()

                            all_info = [case_name, case_number, detail_price, case_price, totalprice]
                            self.common.row = self.common.row + 1
                            time.sleep(0.5)
                            pay_totalprice = self.common.pay(self.windows)
                            all_info.append(pay_totalprice)
                            print(all_info, pay_totalprice)
                            if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(
                                    pay_totalprice) and \
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

                            self.closed_windows(1)
                            self.dboperate.del_elem(type_code[index], num)
                            time.sleep(1)
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
        time.sleep(1)

    # 7著录项目变更
    def patent_description(self):
        all_type = [u'著录项目变更']
        type_code = ["description"]
        for index, patent_type in enumerate(all_type):
            if self.dboperate.exists(type_code[index]):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    self.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.windows[-1])
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
                                self.common.driver.find_element_by_xpath(
                                    ".//ul[@id='ul1']/li[{}]/a".format(temp)).click()

                        # 数量加1
                        # self.common.number_add()
                        # 数量减1
                        # # self.common.number_minus()
                        # 判断价格是否加载成功
                        while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                            time.sleep(0.5)
                        # 获取详情页 价格
                        detail_price = self.common.driver.find_element_by_xpath(
                            "(.//div[@class='sames']//label[@id='totalfee'])").text
                        print("详情页价格", detail_price)

                        self.common.apply_now()
                        # 获取下单页价格
                        case_name, case_number, case_price, totalprice = self.common.commit_order()
                        all_info = [case_name, case_number, detail_price, case_price, totalprice]
                        self.common.row = self.common.row + 1
                        time.sleep(0.5)
                        pay_totalprice = self.common.pay(self.windows)
                        all_info.append(pay_totalprice)
                        print(all_info, pay_totalprice)
                        if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
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

                        self.closed_windows(1)
                        # 使用随机选择类型时，index_2改为random_index
                        self.dboperate.del_elem(type_code[index], random_index)

                        time.sleep(1)
                except Exception as e:
                    print(e)
                    self.common.driver.switch_to_window(self.windows[0])
                self.closed_windows(0)
                time.sleep(1)

    # 8 代缴专利年费
    def patent_replace(self):
        all_type = [u'代缴专利年费']
        for patent_type in all_type:
            if self.dboperate.is_member(self.db, patent_type):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    self.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.windows[-1])
                    while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                        time.sleep(0.5)
                    # 获取详情页 价格
                    detail_price = self.common.driver.find_element_by_xpath(
                        "(.//div[@class='sames']//label[@id='totalfee'])").text
                    print("详情页价格", detail_price)

                    self.common.apply_now()
                    self.common.driver.find_element_by_xpath(".//a[@class='apply-btn button']").click()

                    case_name, case_number, case_price, totalprice = self.common.commit_order()
                    all_info = [case_name, case_number, detail_price, case_price, totalprice]
                    self.common.row = self.common.row + 1
                    time.sleep(0.5)
                    pay_totalprice = self.common.pay(self.windows)
                    all_info.append(pay_totalprice)
                    print(all_info, pay_totalprice)
                    if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
                            float(all_info[4]) == float(all_info[2]):
                        status = 'True'
                    else:
                        status = "False"
                    all_info.append(status)
                    self.common.excel_number(all_info)
                    self.dboperate.del_elem(self.db, patent_type)

                    time.sleep(1)
                    screen_name = "_".join([case_name, case_number, case_price])
                    self.common.qr_shotscreen(screen_name)

                    self.closed_windows(0)

                except Exception as e:
                    print('错误信息', e)
                    self.common.driver.switch_to_window(self.windows[0])

    # 9 PCT 国际申请-- 特殊处理
    def patent_PCT(self):
        all_type = [u'PCT国际申请']
        for patent_type in all_type:
            if self.dboperate.is_member(self.db, patent_type):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    self.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.windows[-1])
                    # 判断价格是否加载成功
                    while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                        time.sleep(0.5)
                    # 获取详情页 价格
                    detail_price = self.common.driver.find_element_by_xpath(
                        "(.//div[@class='sames']//label[@id='totalfee'])").text
                    print("详情页价格", detail_price)
                    self.common.driver.find_element_by_link_text(u'立即申请').click()
                    case_name, case_number, case_price, totalprice = self.common.commit_order()
                    all_info = [case_name, case_number, detail_price, case_price, totalprice]
                    self.common.row = self.common.row + 1
                    time.sleep(0.5)
                    pay_totalprice = self.common.pay(self.windows)
                    all_info.append(pay_totalprice)
                    print(all_info, pay_totalprice)
                    if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
                            float(all_info[4]) == float(all_info[2]):
                        status = 'True'
                    else:
                        status = "False"
                    all_info.append(status)
                    self.common.excel_number(all_info)
                    self.dboperate.del_elem(self.db, patent_type)
                    time.sleep(1)
                    screen_name = "_".join([case_name, case_number, case_price])
                    self.common.qr_shotscreen(screen_name)

                    # self.common.qr_shotscreen(patent_type)
                    self.closed_windows(0)

                except Exception as e:
                    print('错误信息', e)
                    self.common.driver.switch_to_window(self.windows[0])

    # 10 共用部分
    def patent_common(self):
        all_type = [u'电商侵权处理', u'专利权恢复', u'专利实施许可备案', u'专利质押备案', u'集成电路布图设计']
        for patent_type in all_type:
            if self.dboperate.is_member(self.db, patent_type):
                try:
                    locator = (By.XPATH, "(.//div[@class='fl isnaMar'])[1]")
                    WebDriverWait(self.common.driver, 30, 0.5).until(EC.element_to_be_clickable(locator))
                    aa = self.common.driver.find_element_by_xpath("(.//div[@class='fl isnaMar'])[1]")
                    ActionChains(self.common.driver).move_to_element(aa).perform()
                    self.common.driver.find_element_by_link_text(patent_type).click()
                    # 切换至新窗口
                    self.windows = self.common.driver.window_handles
                    self.common.driver.switch_to_window(self.windows[-1])
                    # 判断价格是否加载成功
                    while not self.common.driver.find_element_by_id("totalfee").is_displayed():
                        time.sleep(0.5)
                    # 获取详情页 价格
                    detail_price = self.common.driver.find_element_by_xpath(
                        "(.//div[@class='sames']//label[@id='totalfee'])").text
                    print("详情页价格", detail_price)
                    self.common.apply_now()
                    case_name, case_number, case_price, totalprice = self.common.commit_order()
                    all_info = [case_name, case_number, detail_price, case_price, totalprice]
                    self.common.row = self.common.row + 1
                    time.sleep(0.5)
                    pay_totalprice = self.common.pay(self.windows)
                    all_info.append(pay_totalprice)
                    print(all_info, pay_totalprice)
                    if float(all_info[2]) == float(all_info[3]) and float(all_info[2]) == float(pay_totalprice) and \
                            float(all_info[4]) == float(all_info[2]):
                        status = 'True'
                    else:
                        status = "False"
                    all_info.append(status)
                    self.common.excel_number(all_info)
                    self.dboperate.del_elem(self.db, patent_type)
                    time.sleep(1)
                    screen_name = "_".join([case_name, case_number, case_price])
                    self.common.qr_shotscreen(screen_name)

                    # self.common.qr_shotscreen(patent_type)
                    self.closed_windows(0)

                except Exception as e:
                    print('错误信息', e)
                    self.common.driver.switch_to_window(self.windows[0])

