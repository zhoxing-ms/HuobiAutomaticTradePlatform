import time
import smtplib
from contextlib import suppress
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome('C:\\Users\\themi\\Desktop\\chromedriver_win32\\chromedriver.exe')
site=['https://www.huobipro.com/coin_coin/exchange/#eth_btc','https://www.huobipro.com/bch_btc/exchange/','https://www.huobipro.com/ltc_btc/exchange/']
toc=['ETH','BCH','LTC']
large=[] #!!![IMPORTANT] large[] needs to be cleared after one minutes in order to prevent failure of detection
while True:
    iterator=0
    while iterator<3:
        driver.get(site[iterator])
        time.sleep(2)
        try:
            assert "BTC" in driver.title
        except:
            pass
        #find the element containing valuable info
        time.sleep(2)
        try:
            textamt = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH,"//dl[@class='market_trades_amount']"))).text.splitlines()
            texttyp = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, "//dl[@class='market_trades_type']"))).text.splitlines()
            texttim = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, "//dl[@class='market_trades_time']"))).text.splitlines()
            textpri = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.XPATH, "//dl[@class='market_trades_price']"))).text.splitlines()
        except:
            print("卧槽，又有bug了")
        #moniter large amount of transaction
        size=len(textamt)
        i=1
        while i<size:
            placeholder=textamt[i]
            placeholder1=texttyp[i]
            placeholder2=texttim[i]
            placeholder3=textpri[i]
            if float(placeholder)>5:
                if placeholder not in large:
                    large.append(placeholder)
                    print('【大单交易检测到！】 在'+ placeholder2+' 有价值 ' + placeholder+ ' 比特币的' + toc[iterator] + placeholder1+ ' 现价为 '+ placeholder3)
                    #content='large amount of transaction detected, the amount is ' + str(placeholder)
                    #sending(content)
            i=i+1
        iterator=iterator+1
driver.close()