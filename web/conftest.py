# -*- coding: utf-8 -*-

'''
Common webdriver module

'''
import pytest
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

@pytest.fixture(scope="class")
def chrome_driver_init(request):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1024,800') # May adjust the value due to sometimes can not locate the element
    # chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('lang=en_US')
    chrome_options.add_argument('--headless') #Running in background
    chrome_options.add_argument('ignore-certificate-errors') # https
    chrome_options.add_argument('--no-sandbox') # Avoid error response
    chrome_options.add_argument('--proxy-server="direct://"')
    chrome_options.add_argument('--proxy-bypass-list=*')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('user-agent="Chrome/90.0.4430.93"') #Must told to DUT which browser do you used
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": r"/home",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False,
        })

    
    driver = webdriver.Chrome(chrome_options = chrome_options)
    request.cls.driver = driver

    yield
    driver.close()
    driver.quit()

@pytest.fixture(scope="class")
def firefox_driver_init(request):
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--disable-gpu')
    #firefox_options.add_argument('lang=en_US')
    firefox_options.add_argument('--headless') #Running in background
    firefox_options.add_argument('--no-sandbox') # Avoid error response
    firefox_options.add_argument('--proxy-server="direct://"')
    firefox_options.add_argument('--proxy-bypass-list=*')
    firefox_options.add_argument('--disable-extensions')
    firefox_options.add_argument('user-agent="Firefox/81.0"') #Must told to DUT which browser do you used
        
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'en-US, en')
    driver = webdriver.Firefox(firefox_options = firefox_options,firefox_profile=profile)

    request.cls.driver = driver
    yield
    driver.close()
    driver.quit()

@pytest.fixture(scope="class")
def edge_driver_init(request):

    #pip install msedge-selenium-tools
    from msedge.selenium_tools import EdgeOptions
    from msedge.selenium_tools import Edge
        
    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    edge_options.add_argument("headless")
    edge_options.add_argument("disable-gpu")
    edge_options.add_argument("lang=en_US")
    #driver = Edge(executable_path = 'C:/Python/Python38-32/msedgedriver.exe',options=edge_options)
    driver = Edge(options=edge_options)

    request.cls.driver = driver
    yield
    driver.close()
    driver.quit()