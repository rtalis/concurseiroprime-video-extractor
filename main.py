import re
import os
import csv
import requests
from bs4 import BeautifulSoup
from seleniumwire import webdriver
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
            lambda s: s.find_element(By.XPATH, "/html/body/div[2]/div/div[6]/button[1]").is_displayed())
        driver.find_element(By.XPATH, "/html/body/div[2]/div/div[6]/button[1]").click()
    except TimeoutException:
        print("No ok button")        
    return driver
def join_audio_video(audio_file, video_file, output_file):
    cmd = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac -strict experimental "{output_file}"'
    os.system(cmd)
    
def save_file(driver, filename, url):
    cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
    r = requests.get(url, cookies=cookies, stream=True)     
    total_size = int(r.headers.get('content-length', 0))
    bytes_written = 0
    chunk_size = 1024 * 1024
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                bytes_written += len(chunk)
                progress = min(100, int(bytes_written / total_size * 100))
                print(f"\rDownloading {filename}: [{'#' * int(progress / 2):50s}] {progress}% ", end="", flush=True)
    print("\nDownload completed.")

def get_audio_link(driver):
    cleaned_audio_url = None
    for request in driver.requests:
            if request.response:
                url = request.url
                audiomatch = re.search(r'https://.*?/audio/.*?\.mp4', url)
                if audiomatch and not cleaned_audio_url:
                    cleaned_audio_url = audiomatch.group(0)
                    return cleaned_audio_url
def get_video_link(driver):
    cleaned_video_url = None
    for request in driver.requests:
            if request.response:
                url = request.url
                videomatch = re.search(r'https://.*?/video/.*?\.mp4', url)               
                if videomatch:
                    cleaned_video_url = videomatch.group(0)
                    id = cleaned_video_url.rsplit('/', 1)[-1]
                    print("url: ", cleaned_video_url)
                    if id not in id_list:
                        id_list.append(id)                        
                    if id_list.index(id) >= 1: #the second link is usually a higher quality
                        print(id_list)
                        cleaned_video_url = videomatch.group(0)
                        return cleaned_video_url

def get_requests(driver, url):
    cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
    response = requests.get(url, cookies=cookies)
   
    soup = BeautifulSoup(response.text, 'html.parser')

# Find all links containing the term 'lesson'
    lesson_links = [link.get('href') for link in soup.find_all('a') if 'lesson' in link.get('href', '')]

    # Print all found links
    for link in lesson_links:
        print(link)
        #TODO: navegar para cada um dos links e clicar no conteudo que contem 'parte' no texto
    return response

if __name__ == '__main__':
    id_list = []
    driver = configure_driver()
    get_data(driver)
    input("Play a video")    
    current_url = driver.current_url
    requests = get_requests(driver, current_url)
    
    video_link = get_video_link(driver)
    audio_link = get_audio_link(driver)
    save_file(driver, "video.mp4", video_link)
    save_file(driver, "audio.mp4", audio_link)
    join_audio_video("audio.mp4", "video.mp4", "output.mp4")
            
            # Delete the separated audio and video files
    os.remove("audio.mp4")
    os.remove("video.mp4")

