from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from fake_useragent import UserAgent

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

        # Launch with options
        self.driver = webdriver.Chrome(options=options)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def get_price(self, url):
        """
        :param url: The url of the product
        :return: The product price
        """
        self.driver.get(url)
        string = self.driver.page_source
        pattern = r'<span class="a-offscreen">\$([\d,\.]+)'
        try:
            price = re.search(pattern, string).group(1)
        except AttributeError:
            price = None
        return price
    
