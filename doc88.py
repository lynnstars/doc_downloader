from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

import base64
import time
import sys
import os
import shutil
from tqdm import trange
from img2pdf import conpdf

def download(url):
    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    option.add_argument('log-level=3')
    option.add_argument("--window-size=1920,1080")
    service = Service(executable_path='.//chromedriver')
    driver = webdriver.Chrome(service=service, options=option)
    title = "output"
    try:
        driver.set_page_load_timeout(15)
        driver.get(url)
        title = driver.title
    except:
        print("Timeout - start download anyway.")

    print(f'道客巴巴: 《{title}》')
    time.sleep(5)

    try:
        # 展开全部
        elem_cont_button = driver.find_element(By.ID, "continueButton")
        driver.execute_script("arguments[0].scrollIntoView(true);", elem_cont_button)
        actions = ActionChains(driver)
        actions.move_to_element(elem_cont_button).perform()
        time.sleep(0.5)
        elem_cont_button.click()
    except NoSuchElementException:
        pass

    # 获取页数
    num_of_pages = driver.find_element(By.ID, 'toolbar').find_element(By.ID, 'item-page-panel').\
        find_element(By.CLASS_NAME, 'text').text
    num_of_pages = int(num_of_pages.split(' ')[-1])
    # print("页数：",num_of_pages)

    for i in range(5):
        # 缩放
        driver.find_element(By.ID, 'zoomInButton').click()
        time.sleep(0.5)

    if os.path.exists(f'./temp/{title}'):
        shutil.rmtree(f'./temp/{title}')
    os.makedirs(f'./temp/{title}')


    for pages in trange(num_of_pages):
        time.sleep(0.5)
        canvas_id = "outer_page_" + str(pages + 1)
        pagepb_id = "page_" + str(pages + 1)

        try:
            element = driver.find_element(By.ID, canvas_id)
        except:
            time.sleep(1)
            element = driver.find_element(By.ID, canvas_id)

        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()
        time.sleep(0.5)
        # 执行js代码
        js_cmd = "var canvas = document.getElementById('{}');".format(pagepb_id) + \
            "return canvas.toDataURL();"
        img_data = driver.execute_script(js_cmd)
        img_data = (img_data[22:]).encode()

        with open(f"./temp/{title}/{pages}.png", "wb") as fh:
            fh.write(base64.decodebytes(img_data))
    driver.quit()
    print('下载完毕，正在转码')
    conpdf(f'output/{title}.pdf', f'temp/{title}', '.png')
