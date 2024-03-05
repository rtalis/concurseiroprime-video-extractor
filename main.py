import re
import os
import time
from pytube import YouTube
from glob import glob, escape
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
from urllib.parse import urlparse


#EMAIL = input("E-mail: ")
#PASSWD = input("Password: ")

EMAIL = os.getenv("email")
PASSWD = os.getenv("password")
MAIN_URL = "https://ead.concurseiroprime.com.br"
COURSE_NAME = "Brasil"
DOWNLOAD_DIR = "downloaded_videos"
COOLDOWN_TIME = 10

total_video_counter = 0
downloaded_video_counter = 0
skip_cooldown = False
def configure_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1366,768")
    chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")
    chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--headless")
    if os.name == 'nt':
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options)
    else:
        driver = webdriver.Chrome(options = chrome_options)
    print("Driver started succefully")
    return driver


def get_data(driver):

    driver.get(MAIN_URL)
    try:
        WebDriverWait(driver, COOLDOWN_TIME).until(
            lambda s: s.find_element(By.XPATH, "/html/body/div[1]/header/div/div/div[2]/div[2]/div/ul/li/button").is_displayed())
        
        log_page_button = driver.find_element(By.XPATH, "/html/body/div[1]/header/div/div/div[2]/div[2]/div/ul/li/button")
        log_page_button.click()
        WebDriverWait(driver, COOLDOWN_TIME).until(
            lambda s: s.find_element(By.NAME, "email").is_displayed())
        email_field = driver.find_element(By.NAME, "email")           
        email_field.send_keys(EMAIL, Keys.ENTER)
        WebDriverWait(driver, COOLDOWN_TIME).until(
            lambda s: s.find_element(By.NAME, "password").is_displayed())
        pw_field = driver.find_element(By.NAME, "password")
        pw_field.send_keys(PASSWD, Keys.ENTER)
        print("Logging in")

    except TimeoutException:
        print("TimeoutException: Element not found")
        return None
    try:
        WebDriverWait(driver, COOLDOWN_TIME).until(
            lambda s: s.find_element(By.PARTIAL_LINK_TEXT, COURSE_NAME).is_displayed())
        print("Found course with 'Brasil' term")
        driver.find_element(By.PARTIAL_LINK_TEXT, COURSE_NAME).click()
        

    except TimeoutException:
        driver.close()
        return None
    try:
        WebDriverWait(driver, COOLDOWN_TIME).until(
            lambda s: s.find_element(By.XPATH, "/html/body/div[2]/div/div[6]/button[1]").is_displayed())
        driver.find_element(By.XPATH, "/html/body/div[2]/div/div[6]/button[1]").click()
    except TimeoutException:
        print("No ok button")        
    return driver

def create_directory(url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.split('/')[1:]
    base_dir = DOWNLOAD_DIR
    full_path = os.path.join(base_dir, *path_segments)
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    return full_path


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
    id_list = []
    cleaned_video_url = None
    m4s_link = None
    for request in driver.requests:
            if request.response:
                url = request.url
                #check for videos stored in youtube 
                youtube_match = re.search(r'https://www\.youtube\.com/embed/[^"\']+', url)
                if youtube_match:
                    youtube_url = youtube_match.group(0)
                    return youtube_url
                
                videomatch = re.search(r'https://.*?/video/.*?\.mp4', url)   
                #TODO add support for m4s download links
                #m4smatch = re.search(r'https://.*?/video/.*?\.m4s', url) 
                #if not m4s_link and m4smatch:
                #    m4s_link = m4smatch.group(0)        
                if videomatch:
                    cleaned_video_url = videomatch.group(0)
                    id = cleaned_video_url.rsplit('/', 1)[-1]
                    if id not in id_list:
                        id_list.append(id)                        
                    if id_list.index(id) >= 1: #the second link is usually a higher quality
                        cleaned_video_url = videomatch.group(0)
                        return cleaned_video_url
                    
    #if not cleaned_video_url:
    #    cleaned_video_url = m4s_link

    return cleaned_video_url

def get_lessons(driver, url):
    cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
    response = requests.get(url, cookies=cookies)   
    soup = BeautifulSoup(response.text, 'html.parser')
    lesson_links = [link.get('href') for link in soup.find_all('a') if 'lesson' in link.get('href', '')]
    return lesson_links

def download_youtube_videos(url, directory):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_by_resolution("720p")
        print(f"Downloading {yt.title}...")
        stream.download(output_path=directory, filename=yt.title.replace('/', '_') + '.mp4')  # Specify your path
        print(f"Download completed: {yt.title}")
        return yt.title + '.mp4'  # or return the path to the downloaded video
    except Exception as e:
        print(f"Failed to download YouTube video: {e}")
        return None
def get_file_count(directory: str) -> int:
    count = 0
    for filename in glob(os.path.join(escape(directory), '*')):
        if os.path.isdir(filename):
            count += get_file_count(filename)
        else:
            count += 1
    return count


def save_lesson(driver, directory, part_number):
    global total_video_counter
    global downloaded_video_counter
    filename = f"parte {part_number}.mp4"
    filepath = os.path.join(directory, filename)
    print(f"Saving video to: {filepath}")
    video_link = get_video_link(driver)
    
    if video_link: 
        downloaded_video_counter = downloaded_video_counter + 1
        if part_number > 1:
            total_video_counter = total_video_counter + 1
        print(f"Trying to download video {downloaded_video_counter} of {total_video_counter}")
        if video_link.__contains__("youtube"):
            download_youtube_videos(video_link, directory)
            #print('youtube video....')
        else:
            audio_link = get_audio_link(driver)
            if os.path.exists(filepath):
                print(f"File already found: {filepath}, skipping...")
                return
            save_file(driver, "video.mp4", video_link)
            save_file(driver, "audio.mp4", audio_link)
            join_audio_video("audio.mp4", "video.mp4", filepath)
            os.remove("audio.mp4")
            os.remove("video.mp4")
    else:
        print(f"error download {directory}/parte-{part_number}")

def get_part_lesson(driver, url):
    i = 1
    try:
        driver.get(url)
    
        while (True):
            try:
                #driver.get(url)
                WebDriverWait(driver, COOLDOWN_TIME).until(
                        lambda s: s.find_element(By.XPATH, f"//*[@data-part-order='{i}']").is_displayed())
                actions = ActionChains(driver)
                directory = create_directory(url)
                actions.move_to_element(driver.find_element(By.XPATH, f"//*[@data-part-order='{i}']")).click().perform()
                print(f"wait {COOLDOWN_TIME}s for the page to load...")
                time.sleep(COOLDOWN_TIME)
                save_lesson(driver, directory, i)
                del driver.requests          
                i = i + 1
                
            except TimeoutException:
                print("Lesson downloaded")            
                break
    except:
        print(f"Error getting lesson {url}")
def download_in_mode(mode):
    try:
        global total_video_counter
        global downloaded_video_counter
        driver = configure_driver()
        get_data(driver)
        current_url = driver.current_url
        file_count = get_file_count(DOWNLOAD_DIR)
        lessons = get_lessons(driver, current_url)
        no_lessons = len(lessons)
        downloaded_video_counter = file_count
        total_video_counter = no_lessons 
        print(f"{no_lessons} lessons found in {COURSE_NAME} course")
        print(f"{file_count} files already found in {DOWNLOAD_DIR} folder")
        
        if mode == 'skipping':    
            for lesson in lessons:
                file_count = get_file_count(DOWNLOAD_DIR + lesson)
                if (file_count > 0):
                    print(f"Lesson {lessons.index(lesson)} already partial or completely downloaded. Skipping...")
                else:
                    print(f"lesson {lessons.index(lesson) + 1} of {no_lessons}")        
                    get_part_lesson(driver, f"{MAIN_URL}{lesson}")
        if mode == 'reverse':
            lessons.reverse()  
            for lesson in lessons:
                print(f"lesson {lessons.index(lesson) + 1} of {no_lessons}")        
                get_part_lesson(driver, f"{MAIN_URL}{lesson}")
        if mode == 'random':
            import random
            random.shuffle(lessons)
            for lesson in lessons:
                print(f"lesson {lessons.index(lesson) + 1} of {no_lessons}")        
                get_part_lesson(driver, f"{MAIN_URL}{lesson}")        
        driver.close()    
    except RuntimeError as e:
        print(f"error in {mode} download; {e}")       


if __name__ == '__main__':
    #download in multiple modes to ensure most of the lessons are downloaded before the session is closed. 
    download_in_mode('skipping')
    download_in_mode('reverse')
    download_in_mode('random')

