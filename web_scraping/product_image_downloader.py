import os
import pprint
import time
import urllib.error
import urllib.request
import pandas as pd

def download_file(url, dst_path):
    try:
        with urllib.request.urlopen(url) as web_file:
            data = web_file.read()
            with open(dst_path, mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        print(e)

def download_file_to_dir(url, dst_dir):
    download_file(url, os.path.join(dst_dir, os.path.basename(url)))

# dst_dir = 'data/temp'
# download_file_to_dir(url, dst_dir)


URLS_FILENAME = "adidas_url.csv"
input_df = pd.read_csv(URLS_FILENAME)

for i, row in input_df.iterrows():
    # if i < COUNT:
    #     continue

    model_type = row[2] #2
    size_type = row[3] #3
    list_image_url = row[4] #4
    product_url = row[5] #5

    product_name = product_url.split('/')[-1]

    dst_path = './img/{}.jpg'.format(product_name)
    download_file(list_image_url, dst_path)
