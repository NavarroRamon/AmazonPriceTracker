from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
from fake_useragent import UserAgent
from dotenv import load_dotenv

from selenium.webdriver.common.by import By

import os
load_dotenv()

class AmazonTracker:
    """
    A class for tracking prices of products on Amazon.
    """
    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # User agent option
        user_agent = UserAgent()
        user_agent_string = user_agent.random
        options.add_argument(f'user-agent={user_agent_string}')

        # La forma moderna de pasar el path al driver
        service = Service(executable_path=os.getenv('CHROMEDRIVER'))

        # Launch with options
        self.driver =  webdriver.Chrome(service=service, options=options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def get_price(self, url):
        """
        :param url: The url of the product
        :return: The product price
        """
        try:
            self.driver.get(url)
            child_element = self.driver.find_element(By.ID, "renewedSingleOfferHeader")
            parent_div = child_element.find_element(By.XPATH,
                                                    "ancestor::div[contains(@class,'a-section') and contains(@class,'a-spacing-none') and contains(@class,'a-padding-none')]")
            price = parent_div.find_element(By.ID, "apex_offerDisplay_desktop")
            price = price.text.split('\n')[0].replace('$', '').replace(',', '')
            price = int(price)
        except:
            price = None
        return price
    
