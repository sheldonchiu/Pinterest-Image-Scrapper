# %%
import os
import sys 
import json
sys.path.append(os.path.dirname(__file__))

from PinterestScrapper import PinterestImageScrapper
from patch import webdriver_executable

if __name__ == "__main__":
    #Define file path
    image_path = "/home/sheldon/mecha"

    #Add new search key into array ["cat","t-shirt","apple","orange","pear","fish"]
    search_keys= ['gundam']

    #Parameters
    number_of_images = 10000
    headless = False
    min_resolution=(500,500)
    max_resolution=(9999,9999)
    os.environ['WDM_LOCAL'] = '1'

    #Main program
    for search_key in search_keys:
        image_scrapper = PinterestImageScrapper(image_path,search_key,number_of_images,headless,min_resolution,max_resolution)
        images = image_scrapper.find_image_urls()
        images = image_scrapper.save_images(images)

    #Release resources    
    del image_scrapper
    # with open(f"{image_path}/{search_key}/tags.json", 'w', encoding='utf-8') as f:
    #     json.dump(images, f, ensure_ascii=False, indent=4)
# %%
