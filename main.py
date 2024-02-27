import re
import os
import csv
import requests
#from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


#EMAIL = input("Trei.no E-mail: ")
#PASSWD = input("Trei.no Password: ")

EMAIL = os.getenv("email")
PASSWD = os.getenv("password")

def configure_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1366,768")
    #chrome_options.add_argument("--headless")
    if os.name == 'nt':
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options)
    else:
        driver = webdriver.Chrome(options = chrome_options)
    return driver


def get_data(driver):

    driver.get("https://ead.concurseiroprime.com.br")
    try:
        WebDriverWait(driver, 10).until(
            lambda s: s.find_element(By.XPATH, "/html/body/div[1]/header/div/div/div[2]/div[2]/div/ul/li/button").is_displayed())
        
        log_page_button = driver.find_element(By.XPATH, "/html/body/div[1]/header/div/div/div[2]/div[2]/div/ul/li/button")
        log_page_button.click()
        WebDriverWait(driver, 10).until(
            lambda s: s.find_element(By.NAME, "email").is_displayed())
        email_field = driver.find_element(By.NAME, "email")           
        email_field.send_keys(EMAIL, Keys.ENTER)
        WebDriverWait(driver, 10).until(
            lambda s: s.find_element(By.NAME, "password").is_displayed())
        pw_field = driver.find_element(By.NAME, "password")
        pw_field.send_keys(PASSWD, Keys.ENTER)
    except TimeoutException:
        print("TimeoutException: Element not found")
        return None
    try:
        WebDriverWait(driver, 10).until(
            lambda s: s.find_element(By.PARTIAL_LINK_TEXT, "Brasil").is_displayed())
        driver.find_element(By.PARTIAL_LINK_TEXT, "Brasil").click()
        

    except TimeoutException:
        driver.close()
        return None
    try:
        WebDriverWait(driver, 10).until(
            lambda s: s.find_element(By.TAG_NAME, "button").is_displayed())
        driver.find_element(By.TAG_NAME, "button").click()
    except TimeoutException:
        print("No ok button")        
    return driver

def save_video(driver, filename):

    #video_element = driver.find_element(By.CLASS_NAME, "video-responsive")  # get the video element
    video_url = driver.find_element(By.XPATH ,'//*[@id="lesson"]/iframe').get_attribute('src')
    cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
    r = requests.get(video_url, cookies=cookies, stream=True)
    with open(f"{filename}.mp4", 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
if __name__ == '__main__':
    driver = configure_driver()
    get_data(driver)
    input("Play a video")
    save_video(driver, "teste")
