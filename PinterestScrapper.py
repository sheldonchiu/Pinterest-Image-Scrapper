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
# from webdriver_manager.chrome import ChromeDriverManager   
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

#import helper libraries
import time
import urllib.request
import os
import requests
import io
from PIL import Image
import traceback
import json
from tqdm.auto import tqdm

#custom patch libraries
import patch 

baseURL = 'https://www.pinterest.com'

class PinterestImageScrapper():
    def __init__(self,image_path, search_key="cat",number_of_images=1,headless=False,min_resolution=(0,0),max_resolution=(1920,1080)):
        #check parameter types
        image_path = os.path.join(image_path, search_key)
        if (type(number_of_images)!=int):
            print("[Error] Number of images must be integer value.")
            return
        if not os.path.exists(image_path):
            print("[INFO] Image path not found. Creating a new folder.")
            os.makedirs(image_path)

        options = Options()
        if(headless):
            options.add_argument('--headless')
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)
        driver.set_window_size(1920,1080)
        driver.get(baseURL)

                    
        self.driver = driver
        self.search_key = search_key
        self.number_of_images = number_of_images
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
        
        def toURL(url):
            self.driver.get(url)
            time.sleep(3)
        
        def getPageLinks(limit):
            page_urls_tmp = []
            try:
                while len(page_urls_tmp) < limit:
                    # Get links to detail page
                    soup = BeautifulSoup(self.driver.page_source, "html.parser")
                    results = soup.findAll("div", role="listitem")
                    for result in results:
                        try:
                            link = result.find('a')['href']
                            imgs = result.find("div", attrs={"data-test-id": "pincard-image-with-link"}).findAll("img")
                            imgLink = imgs[0].attrs['src']
                            
                            if link not in page_urls_tmp and link not in page_urls:
                                page_urls_tmp.append(link)
                                images.append(imgLink)
                                pbar.update(1)
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
            return page_urls_tmp
                
        def getImageLink(link):
            # Get image link from detail page
            try:
                self.driver.get(f"{baseURL}{link}")
                time.sleep(3)
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
                
        def writeStateToJson():
            with open(os.path.join(self.image_path, f"{self.search_key}.json"), 'w') as f:
                json.dump({"expanded_index": expanded_index, 'page_urls': page_urls, 'image_urls': images},f)
                
        def readStateFromJson():
            filename = os.path.join(self.image_path, f"{self.search_key}.json")
            if os.path.isfile(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                expanded_index = data['expanded_index']
                page_urls = data['page_urls']
                images = data['image_urls']
                print(f"Continue scanning from page {expanded_index+1}")
                return True, expanded_index, page_urls, images
            return False, -1, [], []
                
        resume, expanded_index, page_urls, images= readStateFromJson()
        if len(page_urls) >= self.number_of_images:
            self.driver.quit()
            return images
        print("collecting links")
        with tqdm(total=self.number_of_images) as pbar:
            if not resume:
                toURL(self.url)
                page_urls += getPageLinks(self.number_of_images - len(page_urls))
                print(f"Page URLs contain {len(page_urls)} items")
                writeStateToJson()
            
            init = True
            for idx, link in enumerate(page_urls):
                if init:
                    if idx <= expanded_index:
                        continue
                    else:
                        init = False
                toURL(f"{baseURL}{link}")
                # getImageLink(link)
                if len(page_urls) < self.number_of_images:
                    page_urls += getPageLinks(self.number_of_images - len(page_urls))
                    print(f"Page URLs contain {len(page_urls)} items")
                    expanded_index = idx
                    writeStateToJson()
                else:
                    break
        
        self.driver.quit()
        print("[INFO] search ended")
        return images

    def save_images(self,images):
        #save images into file directory
        print("[INFO] Saving Image... Please wait...")
        for indx,image_url in enumerate(images):
            try:
                parts = image_url.lstrip("https://").split("/")
                parts[1] = 'originals'
                image_url = "https://" + '/'.join(parts)
                print("[INFO] Image url:%s"%(image_url))
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                for f in ['.jpg', '.png', '.jpeg']:
                    ext = os.path.splitext(os.path.basename(image_url))[1]
                    image_url = image_url.replace(ext, f)
                    image = requests.get(image_url,timeout=5)
                    if image.status_code == 200:
                        with Image.open(io.BytesIO(image.content)) as image_from_web:
                            try:
                                filename = "%s%s.%s"%(search_string,str(indx),image_from_web.format.lower())
                                image_path = os.path.join(self.image_path, filename)
                                print("[INFO] %d .Image saved at: %s"%(indx,image_path))
                                image_from_web.save(image_path)
                                # images[indx]['filename'] = filename
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
                            break
            except Exception as e:
                print("[ERROR] Failed to be downloaded",e)
                pass
        print("[INFO] Download Completed. Please note that some photos are not downloaded as it is not in the right format (e.g. jpg, jpeg, png)")
        return images