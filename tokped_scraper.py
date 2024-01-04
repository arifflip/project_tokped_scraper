####-------------------------------------------------------
## Library
####-------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pandas as pd
import os
import time
import matplotlib.pyplot as plt
import numpy as np
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

####-------------------------------------------------------
## Scraper Class
####-------------------------------------------------------

#setup chromedriver

service = Service(executable_path=r'chromedriver')
options = webdriver.ChromeOptions()
#options.add_argument('--headless')
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=service, options=options)

#tokped scrapper class
class tokopedia_scraper() :
    def __init__(self,key_search,number_of_page) :
        self.key_search=key_search
        self.number_of_page=number_of_page
        
    #method to go to tokped page
    def get_to_tokopedia_page(self) :
        driver.get('https://www.tokopedia.com/')
    
    #method to send value in search bar and enter it
    def search_product_button(self,product) :
        elem=driver.find_element(By.CSS_SELECTOR,'.css-3017qm')
        elem.send_keys(product)
        elem.send_keys(Keys.ENTER)

        #wait statement to let browser fully load the page
        element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".css-x8pgyn")) )

    #method to extract product name from a webdriver object
    def extract_product_name(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-3um8ox').text
        except :
            val=None
        return val

    #method to extract product price from a webdriver object
    def extract_price(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-h66vau').text
        except :
            val=None
        return val

    #method to extract product name from an webdriver object
    def extract_place(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-1kdc32b').text
        except :
            val=None
        return val

    #method to extract merchant name from an webdriver object
    def extract_merchant_name(self,elem) :
        try :
            val=elem.find_element(By.CLASS_NAME,'css-1rn0irl').find_elements(By.TAG_NAME,'span')[1].text
        except :
            val=None
        return val
    
    #method to extract rating product from an webdriver object
    def extract_rating(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-t70v7i').text
        except :
            val=0
        return val

    #method to extract total product sale name from an webdriver object
    def extract_sales(self,elem) :
        try :
            val=elem.find_element(By.CSS_SELECTOR,'.css-26zmlj span:last-child').text.split(' ')[0]
        except :
            val=0
        return val
    
    #method to extract all data from webdriver object then store it in dict
    def extract_data(self,elem) :
        data={'product_name' : self.extract_product_name(elem),
            'product_price' : self.extract_price(elem),
            'place': self.extract_place(elem),
            'store_name': self.extract_merchant_name(elem),
            'rating':self.extract_rating(elem),
            'total_sales' :self.extract_sales(elem)
             }
        return data
    
    #method to handling errors such as (product not found and next button doesnt apper)
    def error_handling(self) :
        val=None
        #check if result result none
        if len(driver.find_elements(By.CSS_SELECTOR,'.css-1852zva')) > 0 :
            val=f"-- {driver.find_element(By.CSS_SELECTOR,'.css-1852zva').text} --"
        #check if next button deosn apper
        if len(driver.find_elements(By.CSS_SELECTOR,'.css-16uzo3v-unf-pagination-item')) > 0:
            if driver.find_elements(By.CSS_SELECTOR,'.css-16uzo3v-unf-pagination-item')[1].is_enabled()==False :
                val='--Next button doesnt appear or its the end on of page--'
        return val

    #method to scroll down the page
    def scroll_down(self) :
        catcher=None
        body = driver.find_element(By.CSS_SELECTOR,'body')
        while driver.find_elements(By.CSS_SELECTOR,'css-bugrro-unf-pagination-item') == [] :
            
            #create catcher variable to handle error
            catcher=self.error_handling()
            if catcher != None :
                print(catcher)
                break
            time.sleep(1)
            body.send_keys(Keys.PAGE_DOWN)
        return catcher

    #method to clik next page
    def next_page(self,page) :
        #btn=driver.find_elements(By.CSS_SELECTOR,'.css-16uzo3v-unf-pagination-item')
        #btn[1].click()
        
        #next button
        driver.find_elements(By.CLASS_NAME,'css-bugrro-unf-pagination-item')[1].click()                             
    
    #method run scraper looper which include (visiting tokped's page, scrolling, extracting, and paginating)
    def run_scraper(self) :
        
        #visit tokped page and seach product
        self.get_to_tokopedia_page()
        self.search_product_button(self.key_search)
        time.sleep(2)
        data=[]        
        page=0
        print(f"SCRAPER RUN WITH QUERY '{self.key_search}' AND PICK {self.number_of_page} PAGES ")
        
        while True :
            
            print(f'------     Running on page {page+1}     -----')
            
            #scroll down to next page            
            counter_page_down=0
            while driver.find_elements(By.CLASS_NAME,'css-bugrro-unf-pagination-item') == [] :
                body = driver.find_element(By.CSS_SELECTOR,'body')
                body.send_keys(Keys.PAGE_DOWN)
                
                counter_page_down+=1 # handling if searh result return only 1 page
                if counter_page_down>10 : # break the loop
                    break
                    
            body.send_keys(Keys.PAGE_UP)

            #loop to extract data
            for i in driver.find_elements(By.CSS_SELECTOR,'.css-llwpbs') :
                data.append(self.extract_data(i))

            #next page
            try :
                driver.find_elements(By.CLASS_NAME,'css-bugrro-unf-pagination-item')[1].click()
                page_report='next_page_exist'
            except :
                page_report='no_next_page' #variable to stop loop
                print('There is no next page')
                body.send_keys(Keys.HOME)
                
            #break loop if there is no next page
            page+=1
            if page==self.number_of_page or page_report =='no_next_page' :
                break

        df=pd.DataFrame.from_dict(data)
        try :
            df=df[~df.product_name.isnull()]
        except :
            df
            
        print('------     Scraping Result :     -----')
        return df
    
def export_data(df) :
    name_file='tokped_scraper_result.csv'
    df.to_csv(name_file,index=None)
    print(f'Data exported to dir {os.getcwd()} with name : {name_file}')

    #terminate driver
    driver.quit()
    print('------     Driver Closed     -----')

####-------------------------------------------------------
## Run Scraper
####-------------------------------------------------------

# tokopedia scraper requeuire 2 input (product_to_search,and number of page that wanna be scraped)
scrapper=tokopedia_scraper('Pikachu Doll',2)
df=scrapper.run_scraper()

print(df.head(10))
export_data(df)