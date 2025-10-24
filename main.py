import json
import os
from datetime import datetime
from time import sleep
import pandas as pd
from amz import AmazonTracker
from discord_webhook import DiscordWebhook
from file_value import read_value, write_value, delete_value

from modules.discord import send_discord
from modules.telegram import send_telegram

from dotenv import load_dotenv
import os
load_dotenv()

# webhook to send the message to discord
discordWebhook = os.getenv('DISCORD_WEBHOOK')
loop = os.getenv('LOOP', False)
webhook = DiscordWebhook(url=discordWebhook, username='AmazonPriceTracker', content='')

# JASON with the information of the product that you need to track
# should be created as the next examplo
# {"name_here" : "https://www.amazon.com.mx/dHTT3DTDMG884&colid=32p" }
ProductsJSON = "products.json"


def amazon_tracker_fun(link):
    """
    :param data_products: list of pairs [{"name": "product_name", "link": "product_url"}, {...}]
    :param df: if you want to concatenate the results in a previous dataframe send it as param, if not just ignore it
    :return: df with the product name product price and datetime of current track
    """
    with AmazonTracker() as amazon_tracker:
        try:
            price = amazon_tracker.get_price(link)
            if not price:
                return False
        except Exception as e:
            return False
    return price


def main():
    # Load the input data
    with open(ProductsJSON, "r") as file:
        data = json.load(file)
    df = pd.DataFrame(list(data.items()), columns=["product", "link"])

    while True:
        # Track the products
        for elm in df.itertuples(index=False):
            value_path = os.path.join('data', f"{elm.product}.txt")
            price = amazon_tracker_fun(elm.link)
            if not price:
                send_telegram(f"Error en tracker {elm.product}")
            current_value = read_value(value_path)
            if current_value is None or price < int(current_value):
                write_value(value_path, price)
                send_telegram(f"{elm.product}\nCosto minimo {price}\n{elm.link}")
                send_discord(f"{elm.product}\nCosto minimo {price}\n{elm.link}")
        if not loop:
            print('Exiting code')
            break
        else:
            sleep(60*4)


if __name__ == "__main__":
    main()
