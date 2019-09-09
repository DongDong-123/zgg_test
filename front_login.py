from selenium import webdriver
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from readConfig import ReadConfig


def front_login(username, password):
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    # driver = webdriver.Chrome()

    driver.maximize_window()

    driver.get(ReadConfig().login_page())

    locator = (By.LINK_TEXT, '密码登录')
    WebDriverWait(driver, 10, 0.5).until(EC.presence_of_element_located(locator))
    driver.find_element_by_link_text(u'密码登录').click()
    # 输入账号、密码、点击登录
    driver.find_element_by_id('tb_user').send_keys(username)
    driver.find_element_by_id('tb_password').send_keys(password)
    driver.find_element_by_id('login1').click()
    sleep(4)
    return driver
    # driver.quit()


if __name__ == '__main__':
    front_login('', '')
