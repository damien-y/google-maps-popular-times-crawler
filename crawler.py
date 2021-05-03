#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 06:54:37 2021

@author: damien
"""

#--- import modules
import pandas as pd
import datetime
import time
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

#--- read files
clean_shop = pd.read_csv("借電站報表_清理.csv")["商家名稱"].values.tolist()

#--- set up parameters
weekday = ["星期日","星期一","星期二","星期三","星期四","星期五", "星期六"]
week = {0 : weekday[0],
        1 : weekday[1],
        2 : weekday[2],
        3 : weekday[3],
        4 : weekday[4],
        5 : weekday[5],
        6 : weekday[6],}
hour = [h for h in range(0,24)]
weekday_hour = []
for w in weekday:
    for h in hour:
        weekday_hour.append(w + " " + str(h))
count = 0
ans_frame = pd.DataFrame(index = weekday_hour)

#--- set up crhome
driver = webdriver.Chrome("/Users/damien/Downloads/ChargeSPOT_資料集/chromedriver")
shop_pop_time = []
shop_list_fin = []
for key in clean_shop:
    url = 'https://www.google.com/maps/'
    driver.get(url)
    
    #--- key in
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
    id = driver.find_element_by_id("searchboxinput")
    time.sleep(5)
    id.send_keys(key)
    time.sleep(1)
    
    #--- click
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//*[@id='searchbox-searchbutton']")))
    search_button = driver.find_element_by_xpath("//*[@id='searchbox-searchbutton']")
    time.sleep(5)
    search_button.click()
    time.sleep(1)
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "place-result-container-place-link")))
        section_button = driver.find_elements_by_class_name("place-result-container-place-link")
        if len(section_button) > 0:
            time.sleep(5)
            section_button[0].click()
            time.sleep(1)
    except TimeoutException:
        print(key + "該店家為單一搜尋結果")
    time.sleep(5)
    
    #--- HTML
    page_source = driver.page_source
    soup = bs(page_source, 'html.parser')
    
    #--- elements
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "section-hero-header-title-subtitle")))
        """title = soup.find(class_= "section-hero-header-title-subtitle").text"""
        weekly = []
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "section-popular-times-bar")))
            pop = soup.find_all(class_="section-popular-times-bar")
            if len(pop) == 0:
                print("#---" + key + "該店家無熱門時段資訊---#")
            else:
                today = -1
                ans_frame[key] = pd.Series()
                for p in pop:
                    close = 0
                    try:
                        if p["jsinstance"] == "0":
                            today += 1
                        p["jsinstance"]
                        now_time = p["aria-label"][:p["aria-label"].index("時")]
                        ans_frame.loc[weekday[today] + " " + str(now_time), key] = int(p["aria-label"][p["aria-label"].index("%") - 2 : p["aria-label"].index("%")].strip().replace("%", "")) / 100
                    except ValueError:
                        now_time = datetime.datetime.now().hour
                        ans_frame.loc[weekday[today] + " " + str(now_time), key] = int(p["aria-label"][p["aria-label"].index("%") - 2 : p["aria-label"].index("%")].strip().replace("%", "")) / 100                        
                    except KeyError:
                        close = 1
                        today += 1
                        """ans_frame[key][today * 24 : today * 24 + 24] = pd.Series()"""
                    finally:
                        if close == 0:
                            print("追加" + key + weekday[today] + " " + str(now_time) + "：" + str(int(p["aria-label"][p["aria-label"].index("%") - 2 : p["aria-label"].index("%")].strip().replace("%", "")) / 100))
                        elif close == 1:
                            print("追加" + key + weekday[today] + "為公休日")
            """         
            if len(pop) > 0:
                #--- time schedule
                index_number = []
                for day in pop:
                    try:
                        index_number.append(day["jsinstance"])
                    except KeyError:
                        pass
                openhour = len(set(e["jsinstance"] for e in pop if "jsinstance" in str(e)))
                total_open = len(pop)
                close_day = 0
                for close in pop:
                    if close["aria-label"] == "の混雑度は % です。":
                        total_open -= 1
                        close_day += openhour
                for i in range(0, 7):
                    daily = []
                    for j in range(0, openhour):
                        try:
                            times = pop[j + (i * openhour) - close_day]["aria-label"]
                            if times == "の混雑度は % です。":
                                times = "本日公休"
                                break
                        except IndexError:
                            times = "N/A"                        
                        daily.append(times)
                    if times == "本日公休":
                        daily = ("本日公休喔" * (openhour - 1) + "本日公休").split("喔")
                    weekly.append(daily)
                    print(key + "該店家具備齊全熱門時段資料")
            else:
                daily = []
                weekly.append(daily, daily, daily, daily, daily, daily, daily)
                print(key + "該店家熱門時段並不齊全")
            shop_pop_time.append(weekly)
            print(key + "#---成功完成輸入熱門時段---#")
            """
        except TimeoutException:
            """
            weekly.append([])
            shop_pop_time.append(weekly)
            """
            ans_frame[key] = pd.Series()
            print("#---" + key + "該店家無熱門時段---#")
        """    
        print("目前進度" + str((len(shop_list_fin) / len(clean_shop)) * 100))
        shop_list_fin.append(key)
        """
    except TimeoutException:
        ans_frame[key] = pd.Series()
        print("#---" + key + "該店家找不到搜尋結果---#")
    finally:
        count += 1
        ans_frame.to_csv('ans_raw.csv', # 檔案名稱
                        encoding = 'utf-8-sig', # 編碼
                        index=True # 是否保留index
                        )
        print(":::目前進度" + str(count / len(clean_shop) * 100) + ":::")

#--- output
"""ans_frame = pd.DataFrame(index = weekday, columns = shop_list_fin)"""
"""
for i in range(0, len(shop_list_fin)):
    if len(shop_pop_time[i]) > 0:
        name = shop_list_fin[i]
        sunday = shop_pop_time[i][0]
        monday = shop_pop_time[i][1]
        tuesday = shop_pop_time[i][2]
        wednessday = shop_pop_time[i][3]
        thursday = shop_pop_time[i][4]
        friday = shop_pop_time[i][5]
        saturday = shop_pop_time[i][6]
        ans_frame[name] = [sunday, monday, tuesday, wednessday, thursday, friday, saturday]
    else:
        ans_frame[name] = ["", "", "", "", "", "", ""]    
"""
ans_frame.fillna(0, inplace = True)
ans_frame.to_csv('ans_zero.csv', # 檔案名稱
                encoding = 'utf-8-sig', # 編碼
                index=True # 是否保留index
                )