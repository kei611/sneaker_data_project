import csv
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

TARGET_URL_LIST = "https://stockx.com/sneakers"
CSV_FILENAME = "other_brands_yeezy.csv"
IMPLICIT_WAIT = 10

#.csvファイルを開く
csv_open   = open(CSV_FILENAME, "w+", encoding="utf-8")
csv_writer = csv.writer(csv_open)

# ターゲットurl接続
# driver = webdriver.Firefox()
driver = webdriver.Chrome()
driver.get(TARGET_URL_LIST)
#要素がロードされるまで待ち時間を5秒に設定
driver.implicitly_wait(IMPLICIT_WAIT)

# 最初に出てくるモーダルウィンドウキャンセル
element_choose_your_location_cancel = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/section/div/img')
element_choose_your_location_cancel.click()
driver.implicitly_wait(IMPLICIT_WAIT)

#adidas
# //*[@id="browse-wrapper"]/div[3]/div/div/div[1]/div/div[3]/div[1]/div
#other brands
# //*[@id="browse-wrapper"]/div[3]/div/div/div[1]/div/div[3]/div[4]/div[1]
element_category_adidas = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[2]/div[2]/div[3]/div/div/div[1]/div/div[3]/div[4]/div[1]")
element_category_adidas.click()

#SIZE TYPESにMenを指定
checkbox_size_type_xpath = f"/html/body/div[1]/div[1]/div[2]/div[2]/div[3]/div/div/div[1]/div/div[4]/div[2]/div[{1}]/div/div/label"
element_checkbox_size_type = driver.find_element_by_xpath(checkbox_size_type_xpath)
size_type = element_checkbox_size_type.text
element_checkbox_size_type.click()
driver.implicitly_wait(IMPLICIT_WAIT)

#adidasのタイプ選択
# //*[@id="browse-wrapper"]/div[3]/div/div/div[1]/div/div[3]/div[1]/div[2]/div[i]/div/label
#other brandsのタイプ選択
# //*[@id="browse-wrapper"]/div[3]/div/div/div[1]/div/div[3]/div[4]/div[2]/div[i]/div/label
for i in range(10, 11):
    checkbox_jordan_xpath   = f"/html/body/div[1]/div[1]/div[2]/div[2]/div[3]/div/div/div[1]/div/div[3]/div[4]/div[2]/div[{i}]/div/label"
    element_checkbox_jordan = driver.find_element_by_xpath(checkbox_jordan_xpath)
    jordan_number = element_checkbox_jordan.text
    element_checkbox_jordan.click()
    driver.implicitly_wait(IMPLICIT_WAIT)

    # ページネーション突起
    k = 1
    base_url = driver.current_url
    while True:
        target_url = base_url + f"&page={k}"
        driver.get(target_url)
        driver.implicitly_wait(IMPLICIT_WAIT)

        time.sleep(5)

        # 商品がない案内フレーズがあるページならbreak
        try:
            element_suggest_product = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div[2]/div[2]/div[3]/div/div/div[2]/div[2]/div[2]/div/div/a")
            break
        except NoSuchElementException:
            pass

        # 靴商品url保存
        list_element_product_links = driver.find_elements_by_xpath('//div[contains(@class, "tile") and contains(@class, "css-1bonzt1") and contains(@class, "e1yt6rrx0")]/a')
        for element_product_link in list_element_product_links:
            element_product_link.send_keys(Keys.TAB)
            driver.implicitly_wait(5)
            element_product_image = element_product_link.find_element_by_xpath('.//div/img')
            image_src = element_product_image.get_attribute("src")
            href = element_product_link.get_attribute("href")
            row = (jordan_number, size_type, image_src, href,)
            csv_writer.writerow(row)
        k+=1
        
# リソースの解放
csv_open.close()
driver.quit()