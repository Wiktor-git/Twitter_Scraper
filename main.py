import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from sqlalchemy.orm import sessionmaker
from models import Tweet, Task, db
from selenium_stealth import stealth

import datetime
import re
import os
import urllib.request
import time
import urllib
import requests
import yt_dlp
from typing import Generator
import database

def avoidBotDetection() -> webdriver:
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled") 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--log-level=3") 
    return webdriver.Chrome(service=service, options=options)
 
hardcodedPassword = ""
hardcodedNickname = ""
imageSavePath = r"C:\Users\kakaf\python_projects\selenium_attempt\savedImages\\"
service = Service(executable_path="chromedriver.exe")
chrome_options = Options()
chrome_options.add_argument("--log-level=3")
driver = avoidBotDetection()
driver.get("https://x.com/home?lang=en")
openedTweets = []
Session = sessionmaker(bind=db)
session = Session()
task_id = -1

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
# changing the property of the navigator value for webdriver to undefined 
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
def loggedIn() -> bool:
    loginElement = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign up with Google')]")
    return not bool(len(loginElement))
def clickSaved():
    savedButton = driver.find_element(By.XPATH, "//a[@href='/i/bookmarks']")
    savedButton.click()
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Search Bookmarks')]")))
def setCredentials():
    hardcodedPassword = input("enter password")
    hardcodedNickname = input("enter login")
def login():
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sign in')]")))
    signInButtton = driver.find_element(By.XPATH, "//*[contains(text(), 'Sign in')]")
    signInButtton.click()
    
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "r-13f91hp")))
    nicknameElement = driver.find_elements(By.TAG_NAME, "input")
    nicknameElement[0].send_keys(hardcodedNickname + Keys.ENTER)
    
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "r-ttdzmv")))
    passwordElement = driver.find_elements(By.TAG_NAME, "input")
    passwordElement[0].send_keys(hardcodedPassword + Keys.ENTER)
    
    #checkIfLoggedIn
    try:
        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "article"))) #if tweet found it means u logged in successfully
        print("Zalogowano pomyslnie")
    except():
        print("Błąd logowania")
def fetchPost():
    scrollToLastPost()
    scroll(500)
    finishPageLoading()
    postByArticle = driver.find_elements(By.TAG_NAME, "article")
    for article in postByArticle:
        if tweetAlreadyOpened(article):
            continue
        ActionChains(driver)\
            .scroll_to_element(article)\
            .perform()
        saveTweetToDB(article)
        tweetID = re.search(r"/status/([^/?#]+)", article.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]').get_attribute("href")).group(1)
        media = determineFormatOfMedia(article) 
        if(media["containsImage"]):
            processImages(article, tweetID)
        if(media["containsGif"]):
            gifElements = article.find_elements(By.CSS_SELECTOR, "video[aria-label*='GIF']")
            for i, gif in enumerate(gifElements):
                saveGif(gif.get_attribute("src"), fileName=f"{tweetID}({i}).gif")        
        if(media["containsVideo"]):
            tweetLink = article.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]').get_attribute("href")
            saveVideo(tweetLink, fileName=f"{tweetID}")     
        
        openedTweets.append(article)
def processImages(article: WebElement, tweetID: str):
        tweetImages: WebElement = article.find_elements(By.CSS_SELECTOR, "a[href*='/photo/']") #did i cast it as right webElement?????????????

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/photo/']"))) 
        
        driver.execute_script("arguments[0].click();", tweetImages[0])
        WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label=Close]")))
        tweetImages = article.find_elements(By.CSS_SELECTOR, "a[href*='/photo/']")            
        
        numberOfImagesInTweet = ammountOfImages()
        largeImageLinks = driver.find_elements(By.CSS_SELECTOR, "img[src*='?format=']")
        
        for i in range(0,numberOfImagesInTweet):
            saveImage(imageLink=largeImageLinks[i].get_attribute("src"), fileName=f"{tweetID}({i}).png")
        closeButton = driver.find_element(By.CSS_SELECTOR, "[aria-label=Close]")
        closeButton.click()
        driver.implicitly_wait(0.15)
def finishPageLoading():
    WebDriverWait(driver, 30).until_not(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.r-1ldzwu0")))
    driver.implicitly_wait(0.3)
def scroll(ammount: int):
    ActionChains(driver)\
        .scroll_by_amount(0, ammount)\
        .perform()
def scrollToLastPost():
    if len(openedTweets) != 0:
        ActionChains(driver)\
            .scroll_to_element(openedTweets[-1])\
            .perform()
def tweetAlreadyOpened(tweet: WebElement):  #optimize with lambda
    for openedTweet in openedTweets:
        if openedTweet.accessible_name == tweet.accessible_name:
            driver.implicitly_wait(0.05)
            return True
    return False
def saveImage(imageLink: str, fileName: str):
    print(imageLink)
    #imageExtension, imageName = "", ""
    #extensionMatch = re.search(r"(?<=\?format=).*?(?=&)", imageLink)
    #if extensionMatch: # screenshot saves only in png
    #    imageExtension = extensionMatch.group()
    #nameMatch = re.search(r"(?<=\/media\/).*?(?=\?format)", imageLink)
    #if nameMatch:
    #    imageName =  nameMatch.group()
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(imageLink)
    driver.implicitly_wait(0.15)
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.TAG_NAME,"img")))
    img = driver.find_element(By.TAG_NAME,"img")
    #imageExtension = ".png" 
    img.screenshot(imageSavePath + fileName)
    driver.close() #close tab
    driver.switch_to.window(driver.window_handles[0])
    driver.implicitly_wait(0.15)
def saveVideo(tweetLink: str, fileName: str): #tweet link
    ydl_opts = {
        'outtmpl': f'{fileName}---%(id)s.%(ext)s',  # Optional: name the file nicely
        'format': 'bestvideo+bestaudio/best',  # Best quality
        "path": r"\\savedImages\\"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([tweetLink])
def saveGif(gifLink: str, fileName: str): #gif ftp mp4 link
    
    filename = imageSavePath + fileName #re.search(r'/tweet_video/(.+?)\.mp4', gifLink).group(1) + ".gif"
    response = requests.get(gifLink, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete!")
    else:
        print(f"Failed to download. Status code: {response.status_code}")
def beginTask(instructions: str):
    global task_id
    time_assigned = datetime.datetime.now()
    task_id = database.add_task(instructions, time_assigned)
def saveTweetToDB(tweet: WebElement):
    tweetID = tweet.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]').get_attribute("href")
    tryGetText = tweet.find_elements(By.CSS_SELECTOR, "div.css-146c3p1.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-a023e6.r-rjixqe.r-16dba41.r-bnwqim")
    text = None
    if len(tryGetText) != 0:
        text = ""
        textBlocs = tryGetText[0].find_elements(By.TAG_NAME, "span")
        for textBloc in textBlocs:
            text += textBloc.text
    user = tweet.find_element(By.CSS_SELECTOR, "a[class*='r-1loqt21']").get_attribute("href")
    
    retweets = 0
    comments = 0
    likes = 0
    tweetStats = tweet.find_element(By.CSS_SELECTOR, 'div.css-175oi2r.r-1kbdv8c.r-18u37iz.r-1wtj0ep.r-1ye8kvj.r-1s2bzr4').get_attribute("aria-label")
    for stat in tweetStats.split(", "):

        if re.search(r'repl', stat, re.IGNORECASE):
            comments = int(stat.split(" ")[0])
        elif re.search(r'like', stat, re.IGNORECASE):
            likes = int(stat.split(" ")[0])
        elif re.search(r'repost', stat, re.IGNORECASE):
            retweets = int(stat.split(" ")[0])
    
    time_posted = datetime.datetime.strptime(tweet.find_element(By.TAG_NAME, "time").get_attribute("datetime"), r"%Y-%m-%dT%H:%M:%S.%fZ")
    time_saved = datetime.datetime.now()
    numberOfMedia = -1
    taskID = task_id
    database.add_tweet(tweetID,text,user,comments,retweets,likes,time_posted, time_saved, numberOfMedia, taskID)
def determineFormatOfMedia(tweet: WebElement) -> dict[str, bool]: #should always have all 3 "containsImage", "containsGif" and "containsVideo"  Generator[dict[str,bool], None, None]
    media = {}
    #image
    try:
        tweet.find_element(By.CSS_SELECTOR, "a[href*='/photo/']") #does it return null or except?
        media.update({"containsImage": True})
    except:
        media.update({"containsImage": False})
        
    #GIF
    try:
        tweet.find_element(By.CSS_SELECTOR, "video[aria-label*='GIF']")
        media.update({"containsGif": True})
    except:
        media.update({"containsGif": False})
    
    try:
        tweet.find_element(By.CSS_SELECTOR, "source[type='video/mp4']")
        media.update({"containsVideo": True})
    except:
        media.update({"containsVideo": False})
    return media
def _determineFormatOfMedia(tweet: WebElement): return dict(_determineFormatOfMedia(tweet))
def ammountOfImages() -> int: #needs to wait for tweet to load
    try:
        button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next slide']")
    except:
        return 1
    numberOfSlides = 1
    while True:
        button.click()
        numberOfSlides += 1
        try:
            button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next slide']")
        except:
            return numberOfSlides
def operation():
    setCredentials()
    WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Sign up with Google')]")))
    taskInstructions = f"saved:{hardcodedNickname}"
    beginTask(taskInstructions)
    while True:
        if(loggedIn()):
            print("zalogowano")
            break
        else:
            print("niezalogowano")
            login()
            continue 
    clickSaved()
    while True:
        fetchPost()
        driver.implicitly_wait(1)
    input()
        #Verify you are human by completing the action below. --- aria-label="Cloudflare" (kapszka)

operation()


print("size of opened tweets: " + sys.getsizeof(openedTweets))
time.sleep(1000)
driver.quit()
