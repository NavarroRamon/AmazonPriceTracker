from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re


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
        self.driver = webdriver.Chrome(options=options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def get_price(self, url):
        self.driver.get(url)
        string = self.driver.page_source
        pattern = r'<span class="a-offscreen">\$([\d,\.]+)'
        try:
            price = re.search(pattern, string).group(1)
        except AttributeError:
            price = None
        return price