# %%
import os
import sys 
import json
sys.path.append(os.path.dirname(__file__))

from PinterestScrapper import PinterestImageScrapper
from patch import webdriver_executable

if __name__ == "__main__":
    #Define file path
    webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))
    image_path = "/output"

    #Add new search key into array ["cat","t-shirt","apple","orange","pear","fish"]
    search_keys= ['gundam']

    #Parameters
    number_of_images = 1000
    headless = True
    min_resolution=(500,500)
    max_resolution=(9999,9999)

    #Main program
    for search_key in search_keys:
        image_scrapper = PinterestImageScrapper(webdriver_path,image_path,search_key,number_of_images,headless,min_resolution,max_resolution)
        images = image_scrapper.find_image_urls()
        images = image_scrapper.save_images(images)

    #Release resources    
    del image_scrapper
    with open(f"{image_path}/{search_key}/tags.json", 'w', encoding='utf-8') as f:
        json.dump(images, f, ensure_ascii=False, indent=4)
# %%
