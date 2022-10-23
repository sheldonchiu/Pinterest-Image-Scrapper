# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 13:01:02 2020

@author: OHyic
"""
#import selenium drivers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException   
from bs4 import BeautifulSoup

#import helper libraries
import time
import urllib.request
import os
import requests
import io
from PIL import Image
import traceback

#custom patch libraries
import patch 

baseURL = 'https://www.pinterest.com'

class PinterestImageScrapper():
    def __init__(self,webdriver_path,image_path, search_key="cat",number_of_images=1,headless=False,min_resolution=(0,0),max_resolution=(1920,1080)):
        #check parameter types
        image_path = os.path.join(image_path, search_key)
        if (type(number_of_images)!=int):
            print("[Error] Number of images must be integer value.")
            return
        if not os.path.exists(image_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(image_path)
        #check if chromedriver is updated
        while(True):
            try:
                #try going to www.google.com
                options = Options()
                if(headless):
                    options.add_argument('--headless')
                print(webdriver_path)
                driver = webdriver.Chrome(webdriver_path, chrome_options=options)
                driver.set_window_size(1920,1080)
                driver.get("https://www.pinterest.com")
                break
            except:
                #patch chromedriver if not available or outdated
                try:
                    driver
                except NameError:
                    is_patched = patch.download_lastest_chromedriver()
                else:
                    is_patched = patch.download_lastest_chromedriver(driver.capabilities['version'])
                if (not is_patched): 
                    exit("[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads")
                    
        self.driver = driver
        self.search_key = search_key
        self.number_of_images = number_of_images
        self.webdriver_path = webdriver_path
        self.image_path = image_path
        self.url = f"https://www.pinterest.com/search/pins/?q={search_key}"
        self.headless=headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        
    def find_image_urls(self):
        """
            This function search and return a list of image urls based on the search key.
            Example:
                google_image_scraper = GoogleImageScraper("webdriver_path","image_path","search_key",number_of_photos)
                image_urls = google_image_scraper.find_image_urls()
                
        """
        print("[INFO] Scraping for image link... Please wait.")
        page_urls=[]
        images = []
        self.driver.get(self.url)
        time.sleep(3)
        try:
            while self.number_of_images > len(page_urls):
                # Get links to detail page
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                results = soup.findAll("div", role="listitem")
                for result in results:
                    try:
                        link = result.find('a')['href']
                        if link not in page_urls:
                            page_urls.append(result.find('a')['href'])
                    except:
                        pass
                # scroll to bottom to load more images
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("[INFO] Reached bottom of page")
                    break
                last_height = new_height
        except:
            print(traceback.format_exc())
            
        # Get image link from detail page
        for link in page_urls:
            try:
                if len(images) >= self.number_of_images:
                    break
                self.driver.get(f"{baseURL}{link}")
                time.sleep(5)
                # Get image url
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                imgs = soup.find("div", attrs={"data-test-id": "pin-closeup-image"}).findAll("img")
                imgs = [i['src'] for i in imgs if 'originals' in i['src']]
                # Get image tag
                detail = soup.findAll(attrs={'data-test-id':'CloseupDetails'})[0]
                tags = [tag.text for tag in detail.findAll(attrs={'data-test-id': 'vase-tag'})]
                images.append({'url': imgs[0], 'tag': tags})
            except:
                print(traceback.format_exc())

        self.driver.quit()
        print("[INFO] search ended")
        return images

    def save_images(self,images):
        #save images into file directory
        print("[INFO] Saving Image... Please wait...")
        for indx,image in enumerate(images):
            try:
                image_url = image['url']
                print("[INFO] Image url:%s"%(image_url))
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                image = requests.get(image_url,timeout=5)
                if image.status_code == 200:
                    with Image.open(io.BytesIO(image.content)) as image_from_web:
                        try:
                            filename = "%s%s.%s"%(search_string,str(indx),image_from_web.format.lower())
                            image_path = os.path.join(self.image_path, filename)
                            print("[INFO] %d .Image saved at: %s"%(indx,image_path))
                            image_from_web.save(image_path)
                            images[indx]['filename'] = image_path
                        except OSError:
                            rgb_im = image_from_web.convert('RGB')
                            rgb_im.save(image_path)
                        image_resolution = image_from_web.size
                        if image_resolution != None:
                            if image_resolution[0]<self.min_resolution[0] or image_resolution[1]<self.min_resolution[1] or image_resolution[0]>self.max_resolution[0] or image_resolution[1]>self.max_resolution[1]:
                                image_from_web.close()
                                #print("GoogleImageScraper Notification: %s did not meet resolution requirements."%(image_url))
                                os.remove(image_path)

                        image_from_web.close()
            except Exception as e:
                print("[ERROR] Failed to be downloaded",e)
                pass
        print("[INFO] Download Completed. Please note that some photos are not downloaded as it is not in the right format (e.g. jpg, jpeg, png)")
        return images