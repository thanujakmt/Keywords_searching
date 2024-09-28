
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

def Driver(wait_time):

    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'eager'
    driver = uc.Chrome(use_subprocess = True,version_main = 121)
    wait = WebDriverWait(driver,wait_time)
    return driver,wait