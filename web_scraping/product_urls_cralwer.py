
import csv
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

URLS_FILENAME = "adidas_url.csv"

# urlのcsvファイルを開く
# csv_urls_open = open(URLS_FILENAME, 'r', encoding='utf-8')
# csv_reader = csv.reader(csv_urls_open)

input_df = pd.read_csv(URLS_FILENAME)

# input_df = input_df[:150]
input_df = input_df[5500:5550]


# len(jordan_stockx_url_list)     22,803
# len(nike_stockx_url_list)       13,809
# len(adidas_stockx_url_list)     5,476
# COUNT = 30


def replace_all_chars(text, chars_to_replace="$()%,", replace_chars_with=""):
    """ replace characters for cleaner results """
    for char in chars_to_replace:
        text = text.replace(char, replace_chars_with)
    return text


url = 'https://stockx.com/adidas-ultra-boost-4-non-dye-cloud-white-sample'
url = 'https://stockx.com/adidas-ultra-boost-atr-mid-reigning-champ-black'

# データ収集実行
sneaker_list_data = []
id_counter = 0
brand = "adidas"
# driver = webdriver.Firefox()
driver = webdriver.Chrome('chromedriver.exe')


for i, row in input_df.iterrows():
    # if i < COUNT:
    #     continue

    product_id = row[1]
    model_type = row[2] #2
    size_type = row[3] #3
    list_image_url = row[4] #4
    product_url = row[5] #5

    print(model_type, size_type, list_image_url, product_url)

    # url入手してpose
    driver.get(product_url)
    time.sleep(5)

    # BeautifulSoupをインスタンス化
    content = driver.page_source
    soup = BeautifulSoup(content, 'lxml')

    # 商品名
    prod_name = soup.find('h1').string.lower()

    # condition
    # <div class="header-stat"><span class="extra-space">Condition:</span><span data-testid="product-condition" class="sneak-score">New</span></div></div>
    condition = soup.find('div', class_='header-stat').text.split(':')[1]

    # last sale
    last_sale = replace_all_chars(soup.find('div', class_='sale-value').text)

    # last sale size
    if soup.find('span', class_='bid-ask-sizes') == None:
        last_sale_size = '--'
    else:
        last_sale_size = soup.find('span', class_='bid-ask-sizes').text.split(' ')[1]

    # lowest ask
    lowest_ask = replace_all_chars(
        soup.find('div', class_='bid bid-button-b').find('div', class_='stats').text.strip('Lowest Ask'))

    # highest bid
    highest_bid = replace_all_chars(
        soup.find('div', class_='ask ask-button-b').find('div', class_='stats').text.strip('Highest Bid'))

    # since last sale dollar amount
    since_last_sale_dollar = replace_all_chars(soup.select_one('div.dollar').text)

    # since last sale percent amount (%)
    since_last_sale_percent = replace_all_chars(soup.select_one('div.percentage').text)

    # 商品情報: colorway, retail price, release date
    prod_info = soup.find_all('div', class_='detail')

    # データが無い場合の空欄埋め
    colorway = '--'
    retail_price = '--'
    release_date = '--'

    for info in prod_info:
        # pass style
        if info.get_text().split(' ')[0] == 'Style':
            pass
        elif info.get_text().split(' ')[0] == 'Colorway':
            colorway = info.get_text().replace('Colorway ', '').strip()
        elif info.get_text().split(' ')[0] == 'Retail':
            retail_price = replace_all_chars(info.get_text().split(' ')[2].strip(''))
        elif info.get_text().split(' ')[0] == 'Release':
            release_date = info.get_text().split(' ')[2].strip()

    # 52 week high
    high_52_week = replace_all_chars(soup.find('div', class_='value-container').text.split(' ')[1])

    # 52 week low
    low_52_week = replace_all_chars(soup.find('div', class_='value-container').text.split(' ')[4])

    # 12 month trade range low
    low_12_month_trade = replace_all_chars(soup.find('div', class_='ds-range value-container').text.split(' ')[0])

    # 12 month trade range high
    high_12_month_trade = replace_all_chars(soup.find('div', class_='ds-range value-container').text.split(' ')[2])

    # volatility
    volatility = replace_all_chars(soup.find('li', class_='volatility-col market-down').text.strip('Volatility'))

    # market information (12 month - num sales, price premium, avg sale price)
    market_info = soup.find_all('div', class_='gauge-container')

    for m in market_info:
        if m.text.split(' ')[0] == '#':
            num_sales_12_month = m.text.strip('# of Sales')
        elif m.text.split(' ')[0] == 'Price':
            price_premium_12_month = m.text.strip('Price Premium(Over Original Retail Price)%')
        elif m.text.split(' ')[0] == 'Average':
            avg_sale_price_12_month = m.text.strip('Average Sale Price$,')

    id_counter = id_counter + 1

    sneaker_list_data.append({
        "id": product_id,
        "brand": brand,
        "product_name": prod_name,
        "condition": condition,
        "last_sale": last_sale,
        "last_sale_size": last_sale_size,
        "lowest_ask": lowest_ask,
        "highest_bid": highest_bid,
        "since_last_sale_dollar": since_last_sale_dollar,
        "since_last_sale_percent": since_last_sale_percent,
        "colorway": colorway,
        "retail_price": retail_price,
        "release_date": release_date,
        "high_52_week": high_52_week,
        "low_52_week": low_52_week,
        "low_12_month_trade": low_12_month_trade,
        "high_12_month_trade": high_12_month_trade,
        "volatility": volatility,
        "num_sales_12_month": num_sales_12_month,
        "price_premium_12_month": price_premium_12_month,
        "avg_sale_price_12_month": avg_sale_price_12_month
    })

    print(f'Progress: {id_counter} of {len(input_df)} Completed')


first_data = pd.DataFrame(sneaker_list_data)

first_data.to_csv('./adidas_detail_data_5500_5550.csv', index=False)





