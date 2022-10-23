# %%
#import selenium drivers
from attr import attributes
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

# %%
driver = webdriver.Chrome("webdriver/chromedriver")
# %%
driver.get("https://www.pinterest.com/search/pins/?q=space battleship")
# %%
soup = BeautifulSoup(driver.page_source, "html.parser")
results = soup.findAll(attrs={'data-test-id':'CloseupDetails'})
# %%
