import json
import os
from datetime import datetime
from time import sleep
import pandas as pd
from amz import AmazonTracker
from discord_webhook import DiscordWebhook

# webhook to send the message to discord
webhook = DiscordWebhook(url='insert_your_url', username='AmazonPriceTracker', content='')
ProductsJSON = "products.json"
ProductsCSV = "products.csv"


def amazon_tracker_fun(data_products, df=pd.DataFrame()) -> pd.DataFrame:
    """
    :param data_products: list of pairs [{"name": "product_name", "link": "product_url"}, {...}]
    :param df: if you want to concatenate the results in a previous dataframe send it as param, if not just ignore it
    :return: df with the product name product price and datetime of current track
    """
    with AmazonTracker() as amazon_tracker:
        for element in data_products:
            name = element.get("name")
            url = element.get("link")
            if not name or not url:
                continue
            try:
                date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                price = amazon_tracker.get_price(url)
                if not price:
                    raise ValueError("Price not found")
                product = {'Product': name, 'Price': price, 'Date': date}
                df = pd.concat([df, pd.DataFrame([product])])
            except (ValueError, AttributeError) as e:
                print(f"Failed to get price for product {name}: {e} \n {url}")
            except Exception as e:
                print(f"An error occurred while processing product {name}: {e} \n {url}")
    return df


def lower_price(df_new: pd.DataFrame, df_old: pd.DataFrame) -> pd.DataFrame:
    """
    :param df_new: the dataframe with the new prices
    :param df_old: the historical dataframe with old prices
    :return: df_lowers_price, with the products with the lowest price than in df_old (if exists)
    """
    # Prepare the minimum value in historical and order by products
    if df_old.empty:
        df_old = df_new
    else:
        df_old.sort_values(by='Product', inplace=True)
    df_old_min = df_old.groupby('Product', as_index=False).min()
    # join dataframes df and df_hist_min on the 'Product' column
    df_merged = pd.merge(df_old_min, df_new, on='Product', suffixes=('_hist', '_now'))
    price_diff = df_merged['Price_now'] < df_merged['Price_hist']
    # filter the merged dataframe to show only the rows where the price is lower
    df_lowers_price = df_merged[price_diff]
    return df_lowers_price.drop(columns=['link_hist'])


def main():
    # Check if historical file exists, if not just load an empty df
    if os.path.exists(ProductsCSV):
        df_hist = pd.read_csv(ProductsCSV)
    else:
        df_hist = pd.DataFrame()

    while True:
        # Load the input data
        with open(ProductsJSON, "r") as file:
            data = json.load(file)
        products_link = pd.DataFrame(data)

        # Track the products
        df = amazon_tracker_fun(data)
        df = pd.merge(df, products_link, how='left', left_on="Product", right_on="name")
        df.drop(columns=['name'], inplace=True)

        # Check for lower price
        df_lower_price = lower_price(df, df_hist)
        # You can also add a logic where the price has a minimum value, for example send email.
        if not df_lower_price.empty:
            webhook.content = f"{df_lower_price}"
            webhook.execute()

        # Save the historical results in a csv file
        df_hist = pd.concat([df, df_hist])
        df_hist.to_csv(ProductsCSV, index=False)

        # Waiting time between execution, and also can add a breakpoint here to see the results
        for i in range(400):
            sleep(1)
            if i == 500:
                break


if __name__ == "__main__":
    main()
