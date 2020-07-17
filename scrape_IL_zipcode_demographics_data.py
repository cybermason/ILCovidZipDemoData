from selenium import webdriver as wd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
import os.path
import datetime
import time
import pandas as pd
import shutil

today = datetime.datetime.today()
yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
month = today.strftime("%m").lstrip("0")
day = today.strftime("%d").lstrip("0")
year = today.strftime("%Y")
today = f"{month}_{day}_{year}"

driver = wd.Chrome(executable_path=r'chromedriver.exe')
driver.get('https://chicago.suntimes.com/coronavirus-data/2020/4/13/21219237/illinois-coronavirus-cases-zip-code-map-search')
delay = 30
try:
    myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "//div[@class='covid-data-download-link']//p//a")))
    print("Page is ready!")
    time.sleep(10)
except TimeoutException:
    print("Loading took too much time!")

button = driver.find_element_by_xpath("//div[@class='covid-data-download-link']//p//a")
ActionChains(driver).click(button).perform()
#button = driver.find_element_by_xpath("//div[@class='covid-data-download-link']//p//a").click()

while not os.path.exists(f"<path>/il-covid-counts-by-zipcode-{today}.csv"):
    time.sleep(1)
driver.quit()

current_zipcode_df = pd.read_csv(f"<path>/il-covid-counts-by-zipcode-{today}.csv")

master_df = pd.read_csv("<path>/MasterILZipcodeDemographicsData.csv")

zipcode_demo_data = current_zipcode_df.copy()
zipcode_demo_data = zipcode_demo_data.iloc[:,[1,16,17,20,21]]
matrix_len = len(zipcode_demo_data.columns)
temp_df = zipcode_demo_data["zip"]
for col_index in range(1, matrix_len):
    series = zipcode_demo_data.iloc[:,col_index]
    col_name = zipcode_demo_data.columns[col_index]
    col_name = col_name[6:]
    series = series.rename(f"{today}_{col_name}")
    temp_df = pd.concat([temp_df, series], axis=1, sort=False)
zipcode_demo_data = temp_df

master_df = pd.merge(master_df, zipcode_demo_data, on='zip', how='outer')
master_df.fillna(0, inplace=True)
master_df.to_csv("<path>/MasterILZipcodeDemographicsData.csv", index=False)

shutil.move(f"<path>/il-covid-counts-by-zipcode-{today}.csv", f"<path>/il-covid-counts-by-zipcode-{today}.csv")
