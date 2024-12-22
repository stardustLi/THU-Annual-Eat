from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import os
import subprocess
import platform
import time
import random

def random_delay(time_start, time_end):
    delay = random.uniform(time_start, time_end)
    time.sleep(delay)

def get_cookie(username, password):
    # passs in empty string if your browser will auto-fill the login form

    if platform.system() == 'Windows':
        os.system("taskkill /f /im msedge.exe")     # must close to enable debugging
        os.chdir("C:\Program Files (x86)\Microsoft\Edge\Application")
        sub_popen = subprocess.Popen('.\msedge.exe --remote-debugging-port=3971"')
        random_delay(2, 3)
    else:
        print("Not Supported platform: " + platform.system())
        exit(1)

    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:3971")
    browser = webdriver.Edge(options=options)

    # # 设置浏览器全屏
    browser.maximize_window()
    browser.get('https://card.tsinghua.edu.cn/userselftrade')
    random_delay(2, 3)

    if browser.current_url.startswith('https://id.tsinghua.edu.cn'):
        if username or password:
            element = browser.find_element(By.ID, "i_user")
            element.send_keys(username)
            element = browser.find_element(By.ID, "i_pass")
            element.send_keys(password)
            random_delay(2, 3)

        button = browser.find_element(By.XPATH, '//*[@id="theform"]/div[4]/a')
        button.click()
        random_delay(2, 3)

    cookie = browser.get_cookie('servicehall')['value']
    browser.quit()

    if platform.system() == 'Windows':
        os.system("taskkill /f /im msedge.exe")
    return cookie
