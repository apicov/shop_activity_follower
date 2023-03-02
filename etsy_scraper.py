import requests
import bs4
from bs4 import BeautifulSoup
import time
import random
import pickle
from pathlib import Path
import os
from collections import OrderedDict
import shutil
import re
import json
import numpy as np

import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# basic functions#################################
def open_file(path):
    with open(path, 'r') as f:
        content = f.read()
    return content

def open_html(path):
    f = open_file(path)
    soup = BeautifulSoup(f, "lxml")
    return soup

def save_html(html, path):
    '''Save html string or beautiful soup object as html'''
    with open(path,'wb') as file:
        if type(html) is bs4.BeautifulSoup:
            file.write(html.prettify('utf-8'))
        else:
            file.write(html)
            
            
headers_list = [
    # Firefox 77 Mac
     {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Firefox 77 Windows
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    },
    # Chrome 83 Mac
    {
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
    },
    # Chrome 83 Windows 
    {
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://www.google.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9"
    }
]

# Create ordered dict from Headers above
ordered_headers_list = []
for headers in headers_list:
    h = OrderedDict()
    for header,value in headers.items():
        h[header]=value
    ordered_headers_list.append(h)


def download_html(url):
    headers = random.choice(ordered_headers_list)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
            return None
    soup = BeautifulSoup(response.text, "lxml")
    return soup

def download_url(url):
    headers = random.choice(ordered_headers_list)
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
            print(f'error: {response.status_code}')
            return None
    return response.text

def download_img(url, dest_path):
    with open(dest_path, 'wb') as handle:
        response = requests.get(url, stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

        
'''def custom_wait():
    custom_wait.cnt += 1
    if custom_wait.cnt % 5 == 0:
        time.sleep(random.randint(120,124))
    else:
        time.sleep(random.randint(25,35))
        
custom_wait.cnt = 0'''

def custom_wait():
    custom_wait.cnt += 1
    if custom_wait.cnt % 5 == 0:
        time.sleep(random.randint(120,124))
    else:
        time.sleep(random.randint(5,10))
        
custom_wait.cnt = 0
###################################################################################

###########Downloading reviewers data ############################################

def download_favorite_shops(base_url, dest_path,file_name_prefix=""):
    #first dowload page 1 and extract from it the total number of paging sites
    shop_url = base_url+'?tab=shops&page={}&soas=1'
    error, soup = download_favorite(shop_url.format(1))
    if error == -1: 
        #response error (may be bot blocked by server  (-1))
        return error
    elif error == -2:
        #item list is empty (may be private account)(-2), , keep it to extract other data and exit
        save_html(soup,dest_path/(file_name_prefix+str(1).zfill(5)+'.html'))
        return 0
    else:
        #save site 1
        save_html(soup,dest_path/(file_name_prefix+str(1).zfill(5)+'.html'))
        #extract total number of pagination sites
        try:
            total_pages = int(soup.find('div', class_='wt-show-md').find_all('li', class_='wt-action-group__item-container')[-2].text)
        except:
            #there is no pagination menu, so there is only one site
            total_pages = 1
            print(f'\rpage number:{1} {shop_url.format(1)}',end='')
            custom_wait() 
            return 0
        
        print(f'shop_tot_pages : {total_pages}')
        #download other sites
        #for pn in range(1,total_pages+1): 
        #download maximum 20 sites
        for pn in range(2,min(total_pages+1,20)):
            error, soup = download_favorite(shop_url.format(pn))
            if error == -1:
                #response error (may be bot blocked by server  (-1)) 
                return error
            elif error == -2:
                # item list is empty (-2)
                if pn != total_pages: #if item list is empty but it is the last page, it is ok
                    return error 

            #extract current page number from downloaded html to check if numbers match
            try:
                current_page = soup.find('button', class_='wt-btn wt-btn--filled wt-action-group__item wt-is-selected wt-pr-xs-2 wt-pl-xs-2').text
            except:
                #there was some problem with the downloaded page
                return -3
            #if page numbers dont match, there is something wrong with html
            if int(current_page) != pn:
                return -4
                
            save_html(soup,dest_path/(file_name_prefix+str(pn).zfill(5)+'.html'))
            print(f'\rpage number:{current_page} {shop_url.format(pn)}                               ',end='')
            custom_wait() 

        return 0
    
    
def download_favorite_items(base_url, dest_path,file_name_prefix=""):
    #first dowload page 1 and extract from it the total number of paging sites
    it_url = base_url+'?tab=items&ref=cl_favorite-images&page={}'
    error, soup = download_favorite(it_url.format(1))
    if error == -1: 
        #response error (may be bot blocked by server  (-1))
        return error
    elif error == -2:
        #item list is empty (may be private account)(-2),, keep it to extract other data and exit
        save_html(soup,dest_path/(file_name_prefix+str(1).zfill(5)+'.html'))
        return 0
    else:
        #save site 1
        save_html(soup,dest_path/(file_name_prefix+str(1).zfill(5)+'.html'))
        #extract total number of pagination sites
        try:
            total_pages = int(soup.find('div', class_='wt-show-md').find_all('li', class_='wt-action-group__item-container')[-2].find('a').get('href').split("=")[-1]) 
        except:
            #there is no pagination menu, so there is only one site
            total_pages = 1
            print(f'\rpage number:{1} {it_url.format(1)}',end='')
            custom_wait() 
            return 0
        
        print(f'items_tot_pages : {total_pages}')
        #download other sites
        #for pn in range(1,total_pages+1): 
        #download maximum 20 sites
        for pn in range(2,min(total_pages+1,20)):
            error, soup = download_favorite(it_url.format(pn))
            if error == -1: 
                #response error (may be bot blocked by the server  (-1)) 
                return error
            elif error == -2:
                # item list is empty (-2)
                if pn != total_pages: #if item list is empty but it is the last page, it is ok
                    return error 
            #extract current page number from downloaded html to check if numbers match
            try:
                current_page = soup.find('a',class_='wt-action-group__item wt-btn wt-pr-xs-2 wt-pl-xs-2 wt-is-selected').find('span', class_="").text
            except:
                #there was some problem with the downloaded page
                return -3
            #if page numbers dont match, there is something wrong with html
            if int(current_page) != pn:
                return -4
            
            save_html(soup,dest_path/(file_name_prefix+str(pn).zfill(5)+'.html'))
            print(f'\rpage number:{current_page} {it_url.format(pn)}                               ',end='')
            custom_wait() 

        return 0 
        
def download_favorite(url):
    soup = download_html(url)
    #check if it return a valid code (200)
    if soup == None:
        print('te pillaron')
        return -1, None
    #check if site contains items
    section = soup.find('p', class_='wt-text-heading-01 wt-text-black wt-pt-xs-5 wt-pb-xs-1 wt-text-center-xs')
    if section != None:
        #no item menu found , probably private page
        return -2, soup 
    return 0, soup

def download_reviewers_htmls(df_rev,dest_path,file_name_prefix="",start_idx=0,end_idx=None):
    #dest_path.mkdir(parents=True, exist_ok=True)
    end_idx = df_rev.shape[0] if end_idx is None else end_idx
    for r in range(start_idx,end_idx):
        #print(type(r))
        idx = df_rev.loc[r]['CustomerURL'].find('?')
        base_url = df_rev.loc[r]['CustomerURL'][:idx]
        customerId = base_url.split('/')[-1]
        print(base_url,customerId,df_rev.loc[r]['CustomerName'], r)
        
        cust_path = dest_path/(df_rev.loc[r]['CustomerName']+'___'+customerId)
        cust_path.mkdir(parents=True, exist_ok=True)
        fav_items_path = cust_path/('favorite_items')
        fav_items_path.mkdir(parents=True, exist_ok=True)
        fav_shops_path = cust_path/('favorite_shops')
        fav_shops_path.mkdir(parents=True, exist_ok=True)
        
        error_code = download_favorite_items(base_url,fav_items_path,file_name_prefix)
        if error_code < 0:
            print(f'error:{error_code}')
            return
        print("")
        error_code = download_favorite_shops(base_url,fav_shops_path,file_name_prefix)
        if error_code < 0:
            print(f'error:{error_code}')
            return
            
def download_reviewers_htmls_to_mega(df_rev,dest_path,file_name_prefix="",start_idx=0,end_idx=None):
    #dest_path.mkdir(parents=True, exist_ok=True)
    end_idx = df_rev.shape[0] if end_idx is None else end_idx
    for r in range(start_idx,end_idx):
        #print(type(r))
        idx = df_rev.loc[r]['CustomerURL'].find('?')
        base_url = df_rev.loc[r]['CustomerURL'][:idx]
        customerId = base_url.split('/')[-1]
        print(base_url,customerId,df_rev.loc[r]['CustomerName'], r)
        
        cust_path = dest_path/(df_rev.loc[r]['CustomerName']+'___'+customerId)
        cust_path.mkdir(parents=True, exist_ok=True)
        fav_items_path = cust_path/('favorite_items')
        fav_items_path.mkdir(parents=True, exist_ok=True)
        fav_shops_path = cust_path/('favorite_shops')
        fav_shops_path.mkdir(parents=True, exist_ok=True)
        
        error_code = download_favorite_items(base_url,fav_items_path,file_name_prefix)
        if error_code < 0:
            print(f'error:{error_code}')
            return
        print("")
        error_code = download_favorite_shops(base_url,fav_shops_path,file_name_prefix)
        if error_code < 0:
            print(f'error:{error_code}')
            return
                
        #send downloaded customer data to mega drive
        os.system(f"mega-put -c {cust_path} reviewers/{cust_path.name}")
        shutil.rmtree(cust_path)
        
##########################################################################################################


#################################################Download reviews data##########################
#this was used for downloading reviews from thestitchpatterns, which used ajson file
#def collect_json_reviews(base_url, pages, dest,file_name_prefix=''):
#    '''Downloads jsons of reviews requests'''
#    dest.mkdir(parents=True, exist_ok=True)
#    
#    for p in range(1,pages+1):
#        json_file = download_url(base_url.format(p))
#        with open(dest/(file_name_prefix+str(p).zfill(5)+'.json'),'w') as file:
#            file.write(json_file)
#        print(f'\r {p}      ',end='')
#        custom_wait()



#this one works with html files
def download_reviews(base_url, pages, dest,file_name_prefix=''):
    '''Downloads htmls of reviews requests'''
    dest.mkdir(parents=True, exist_ok=True)

    for p in range(1,pages+1):
        html = download_url(base_url.format(p))
        with open(dest/(file_name_prefix+str(p).zfill(5)+'.html'),'w') as file:
            file.write(html)
        print(f'\r {p}      ',end='')
        custom_wait()
###############################################################################################


###############################Extract reviews data##########################################################
months = dict(jan='01', feb='02', mar='03', apr='04', may='05', jun='06', jul='07', aug='08', sep='09', oct='10', nov='11', dec='12')

def format_review_date(scraped_date):
    "processes string containing review date to a pandas compatible date format"
    month = re.search('[a-z]{3}',scraped_date.lower()).group()
    day = re.search('[^0-9][0-9]{1,2}[^0-9]',scraped_date).group()[1:-1].zfill(2)
    year = re.search('[0-9]{4}',scraped_date).group()
    assert month in months and int(day)<=31 and int(year)>1980, 'bad input'
    new_format = f"{year}-{months[month]}-{day}"
    return new_format



def extract_reviews_data_from_html(soup):
    reviews = soup.find_all('li', class_='wt-bt-xs wt-pt-xs-2 wt-mb-xs-5')
    r_items = []
    for r in reviews:
        #import pdb; pdb.set_trace()
        rev = {}
        dcustomer = r.find('p', class_="shop2-review-attribution").a
        if dcustomer is None: continue
        rev['CustomerName'] = dcustomer.text
        rev['CustomerURL'] = dcustomer['href']
        rev['ReviewDate'] = format_review_date( dcustomer.next_sibling )
        rev['Stars'] = float(r.find('input', attrs={'name':'rating'})['value'])
        item = r.find('div', class_= 'wt-display-table-cell wt-width-full wt-vertical-align-middle wt-hide-xs wt-show-md')
        if item is None: continue
        rev['ItemName'] = item.p.text
        item_href = r.find('a', class_='wt-display-block wt-text-link-no-underline').get('href')
        #get listing id from href
        rev['ItemId'] = re.search('listing/[0-9]+', item_href).group().split('/')[1]
        review = r.find('p', class_= 'prose wt-break-word wt-m-xs-0')
        rev['Review'] = review.text if review is not None else ""
        r_items.append(rev)
    return r_items


def html_from_reviews_json(json_path):
    "extracts html part from json response in reviews request"
    content = open_file(json_path)
    #decode json and put it in dictionary
    response_dic = json.loads(content)
    #use received html part 
    soup = BeautifulSoup(response_dic['output']['shop-reviews'], "lxml")
    return soup

#also used to extract erviews from jsons in thestitchpatterns
'''def extract_reviews_from_files(jsons_path):
    # get  downloaded jsons
    jsons = sorted(list(jsons_path.rglob('*.json')))
    cleaned_reviews = []
    for j in jsons:
        #import pdb; pdb.set_trace()
        soup = html_from_reviews_json(j)
        cleaned_reviews += extract_reviews_data_from_html(soup)
        print(f'\r {j}      ',end='')
    df = pd.DataFrame.from_dict(cleaned_reviews)
    return df'''


def extract_reviews_from_files(path):
    # get  downloaded htmls
    htmls = sorted(list(path.rglob('*.html')))
    cleaned_reviews = []
    for j in htmls:
        #import pdb; pdb.set_trace()
        soup = open_html(j)
        cleaned_reviews += extract_reviews_data_from_html(soup)
        print(f'\r {j}      ',end='')
    df = pd.DataFrame.from_dict(cleaned_reviews)
    return df
##############################################################################################################




##########################check downloaded reviewers files and download again if there is somethig wrong##################################
def check_down_favorite_items(items_path):
    htmls = sorted (list(items_path.glob('*.html')))
    if htmls ==[]: #no items in list, try to download again
        return -1
    #open first file and extract current page number and total number of supposed pages
    soup = open_html(htmls[0])
    #check if site contains items
    section = soup.find('p', class_='wt-text-heading-01 wt-text-black wt-pt-xs-5 wt-pb-xs-1 wt-text-center-xs')
    if section != None:
        #no items menu found, so not needed to download more(this is use to collect other reviewers data)
        return 0
    #extract total number of pagination sites
    try:
        total_pages = int(soup.find('div', class_='wt-show-md').find_all('li', class_='wt-action-group__item-container')[-2].find('a').get('href').split("=")[-1]) 
    except:
        #there is no pagination menu, so there is only one site
        total_pages = 1
        
    if len(htmls) != min(19,total_pages):
        #error if number of sites doesnt match 
        return -1
    
    #check if current page extracted from html matches with file name 
    for i in range(1, len(htmls)):
        soup = open_html(htmls[i])
        #extract 5 digit number from file name
        intended_pn = int(re.search('[0-9]{5}', htmls[i].name).group())
        #extract current page number from downloaded html to check if numbers match
        try:
            extracted_pn = int(soup.find('a',class_='wt-action-group__item wt-btn wt-pr-xs-2 wt-pl-xs-2 wt-is-selected').find('span', class_="").text)
        except:
            #there was some problem with the downloaded page
            extracted_pn = 100000000
            
        if extracted_pn != intended_pn:
            #download again this site if numbers dont match
            #print('hay malos',i,extracted_pn,intended_pn)
            return -1
            
    #if no errors return 0
    return 0



def check_down_favorite_shops(shops_path):
    htmls = sorted (list(shops_path.glob('*.html')))
    if htmls ==[]: #no items in list, try to download again
        return -1
    #open first file and extract current page number and total number of supposed pages
    soup = open_html(htmls[0])
    #check if site contains items
    section = soup.find('p', class_='wt-text-heading-01 wt-text-black wt-pt-xs-5 wt-pb-xs-1 wt-text-center-xs')
    if section != None:
        #no items menu found, so not needed to download more(this is use to collect other reviewers data)
        return 0
    #extract total number of pagination sites
    try:
        total_pages = int(soup.find('div', class_='wt-show-md').find_all('li', class_='wt-action-group__item-container')[-2].text) 
    except:
        #there is no pagination menu, so there is only one site
        total_pages = 1
    
    if len(htmls) != min(19,total_pages):
        #error if number of sites doesnt match 
        return -1
    
    #check if current page extracted from html matches with file name
    for i in range(1, len(htmls)):
        soup = open_html(htmls[i])
        #extract 5 digit number from file name
        intended_pn = int(re.search('[0-9]{5}', htmls[i].name).group())
        #extract current page number from downloaded html to check if numbers match
        try:
            extracted_pn = int(soup.find('button', class_='wt-btn wt-btn--filled wt-action-group__item wt-is-selected wt-pr-xs-2 wt-pl-xs-2').text)
        except:
            #there was some problem with the downloaded page
            extracted_pn = 100000000
            
        if extracted_pn != intended_pn:
            #download again this site if numbers dont match
            #print('hay malos',extracted_pn,intended_pn)
            return -1
            
    #if no errors return 0
    return 0




def empty_folder(path):
    files = path.glob('*')
    for f in files:
        os.remove(f)


#check all folders in path
def check_and_correct_reviewers_folders(reviewers_path,file_name_prefix=""):
    paths = sorted(reviewers_path.glob('*'))
    for n,d in enumerate(paths):
        print(f'{n+1} of {len(paths)}')
        cust_id = d.name.split("_")[-1]

        #check favorite items
        items_path = d/'favorite_items'
        error = check_down_favorite_items(items_path)

        if error < 0:
            #if error empty folder and download again
            print(f'error in {d.name} items')
            empty_folder(items_path)
            base_url = 'https://www.etsy.com/people/'+cust_id
            print(base_url)
            error_code = download_favorite_items(base_url,items_path,file_name_prefix)
            if error_code < 0:
                print(f'error:{error_code}')

        #check favorite shops       
        shops_path = d/'favorite_shops'
        error = check_down_favorite_shops(shops_path)

        if error < 0:
            #if error empty folder and download again
            print(f'error in {d.name} shops' )
            empty_folder(shops_path)
            base_url = 'https://www.etsy.com/people/'+cust_id
            print(base_url)
            error_code = download_favorite_shops(base_url,shops_path,file_name_prefix)
            if error_code < 0:
                print(f'error:{error_code}')
###############################################################################################3
   


#################### Extract reviewers data #########################################################################
def extract_reviewer_data_from_html(soup):
    data = {}
    #name that appears on site
    data['CustomerName'] = soup.find('h1', class_='wt-text-heading-01 wt-mr-xs-4 wt-mb-xs-1').text.lstrip(" \n").rstrip(" \n")
    try:
    #location
        data['CustomerLocation'] = soup.find('div', class_='wt-nudge-r-3 wt-text-caption wt-mr-xs-2 wt-mb-xs-1').find('span', class_='').text.lstrip(" \n").rstrip(" \n")
    except:
        data['CustomerLocation'] = ""
    try:
        #number following
        data['NumberFollowing'] = int( soup.find('a', class_='wt-text-link-no-underline wt-text-caption wt-mr-xs-2').span.text.lstrip(" \n").rstrip(" \n").replace(',','') )
    except:
        data['NumberFollowing'] = np.NaN
    try:
        #number followers
        data['NumberFollowers'] = int( soup.find('a', class_='wt-text-link-no-underline wt-text-caption').span.text.lstrip(" \n").rstrip(" \n").replace(',','') )
    except:
        data['NumberFollowers'] = np.NaN

    itsh = soup.find_all('div', class_='wt-display-flex-xs wt-align-items-center wt-text-center-xs') #contains number of favorite items and shops

    if 'private' in itsh[0].text.lower():
        data['IsFavoriteItemsPrivate'] = True
        data['NumberFavoriteItems'] = np.NaN
    else:
        data['IsFavoriteItemsPrivate'] = False
        data['NumberFavoriteItems'] = int( re.search('[0-9]+', itsh[0].text).group() )

    #check if shop list is private
    if 'private' in itsh[1].text.lower():
        data['IsFavoriteShopsPrivate'] = True
        data['NumberFavoriteShops'] = np.NaN
    else:
        data['IsFavoriteShopsPrivate'] = False
        data['NumberFavoriteShops'] = int( re.search('[0-9]+', itsh[1].text).group() )

    return data


def extract_favorite_items_from_html(soup):
    #check if site contains items
    section = soup.find('p', class_='wt-text-heading-01 wt-text-black wt-pt-xs-5 wt-pb-xs-1 wt-text-center-xs')
    if section != None:
        #no items menu found
        return []

    items = soup.find_all('div', class_='js-merch-stash-check-listing v2-listing-card wt-mb-xs-2 wt-position-relative wt-grid__item-xs-6 wt-flex-shrink-xs-1 wt-grid__item-xl-2 wt-grid__item-lg-2 wt-grid__item-md-4 wt-block-grid__item listing-card-experimental-style')
    items_list = []
    for i in items:
        ditem = {}

        #item id
        ditem['ItemId'] = i.find('a',class_='listing-link wt-display-inline-block').get('data-listing-id')
        #item name
        ditem['ItemName'] = i.find('a',class_='listing-link wt-display-inline-block').get('title')
        #itemUrl 
        ditem['ItemUrl'] = i.find('a',class_='listing-link wt-display-inline-block').get('href')
        #Shop
        try:
            tag_name = i.find('div',class_='wt-text-caption wt-text-truncate wt-text-gray wt-mb-xs-1')
            
            #some sites have class name with "grey" instead of "gray"
            if tag_name is None:
                tag_name = i.find('div',class_='wt-text-caption wt-text-truncate wt-text-grey wt-mb-xs-1')
            
            sh_name = re.search('From shop [a-zA-Z0-9]+', tag_name.text).group().split(" ")[-1]

            ditem['ShopName'] = sh_name
            
        except:
            ditem['ShopName'] = ''
        #is bestseller if not none
        isbest = i.find('span', class_='wt-badge wt-badge--small wt-badge--status-03 wt-mt-xs-1 wt-mr-xs-1 search-half-unit-mb')
        ditem['IsBestseller'] = False if isbest is None else True
        #thumbnailUrl
        try:
            ditem['ItemThumbnailUrl'] = i.find('img', class_='wt-width-full wt-height-full wt-display-block wt-position-absolute user_profile').get('src')
        except:
            ditem['ItemThumbnailUrl'] = ''
        #currency
        try:
            ditem['PriceCurrency'] = i.find('div',class_='v2-listing-card__info').find('span', attrs={'class':"currency-symbol"}).text.lstrip(" \n").rstrip(" \n")
        except:
            ditem['PriceCurrency'] = ''
        #sale price
        try:
            ditem['SalePrice'] = float(i.find('div',class_='v2-listing-card__info').find('span', attrs={'class':"currency-value"}).text)
        except:
            ditem['SalePrice'] = np.NAN
        items_list.append(ditem)

    return items_list


def extract_favorite_shops_from_html(soup):
    #check if site contains items
    section = soup.find('p', class_='wt-text-heading-01 wt-text-black wt-pt-xs-5 wt-pb-xs-1 wt-text-center-xs')
    if section != None:
        #no items menu found
        return []

    shops = soup.find('div', class_='wt-grid wt-mb-xs-3 wt-pl-xs-0 wt-ml-xs-0 wt-mr-xs-0 wt-block-grid-xs-1 wt-block-grid-lg-2').find_all('div', class_='wt-grid__item-xs-12 wt-grid__item-md-6 wt-grid__item-lg-6 wt-pb-xs-6 wt-pl-xs-0 wt-pr-xs-0 wt-overflow-hidden fave-shop-card')
    shops_list = []
    for i in shops:
        dshop = {}
        
        #shop name
        dshop['ShopName'] = i.find('p', class_='wt-text-caption-title wt-text-truncate').text.lstrip(" \n").rstrip(" \n")
        #shop url
        dshop['ShopUrl'] = i.find('a', class_='wt-display-flex-xs wt-justify-content-space-between wt-card__link').get('href')
        #stars
        try:
            dshop['Stars'] = float(i.find('span', class_='wt-screen-reader-only').text.lstrip(" \n").rstrip(" \n").split(" ")[0])
        except:
            dshop['Stars'] = 0.0 
        #location
        try:
            dshop['ShopLocation'] =  i.find('span', class_='wt-ml-md-1 wt-text-truncate').text.lstrip(" \n").rstrip(" \n")
        except:
            dshop['ShopLocation'] = ""
        
        try:
            #number of reviews
            num = i.find('div', class_='wt-display-flex-xs wt-flex-direction-row-xs wt-align-items-center').find('span',class_='wt-text-truncate').text.lstrip("\n (").rstrip("\n )")
            #remove commas ',' from string
            num = num.replace(',','')
            dshop['NumReviews'] = int(num)
        except:
            dshop['NumReviews'] = 0
        #avatarUrl
        dshop['AvatarUrl'] = i.find('img', class_='wt-rounded-01 shop-card-avatar').get('src') 
        shops_list.append(dshop)

    return shops_list


def extract_reviewers_data_from_folder(reviewers_path):
    paths = sorted(reviewers_path.glob('*'))
    reviewers_list = []
    favorite_items_list = []
    favorite_shops_list = []

    for n,p in enumerate(paths[:]):
        #extract Customer reviews name(name shown in reviews) and customer url id(name included in profile site) from folder name
        names = p.name.split('_')
        customer_reviews_name = names[0]
        customer_url_id = names[-1]
        print(f"{n+1} of {len(paths)}, {customer_reviews_name} {customer_url_id}")

        #get list of htmls of favorite items
        fi_htmls = sorted((p/'favorite_items').glob('*.html'))

        #extract reviewer data from one of the htmls
        soup = open_html(fi_htmls[0])
        reviewer = extract_reviewer_data_from_html(soup)
        # add customer rev name and id
        reviewer['CustomerNameInReview'] = customer_reviews_name
        reviewer['CustomerUrlId'] = customer_url_id
        reviewers_list.append(reviewer)

        #extract favorite items from htmls
        for h in fi_htmls:
            soup = open_html(h)
            items = extract_favorite_items_from_html(soup)
            
            # add customer rev name and id to every  item in list
            for i in items:
                i['CustomerNameInReview'] = customer_reviews_name
                i['CustomerUrlId'] = customer_url_id

            favorite_items_list += items



        #get list of htmls of favorite shops
        fs_htmls = sorted((p/'favorite_shops').glob('*.html'))
        #extract favorite shops from htmls
        for h in fs_htmls:
            soup = open_html(h)
            shops = extract_favorite_shops_from_html(soup)
            
            # add customer rev name and id to every  shop in list
            for i in shops:
                i['CustomerNameInReview'] = customer_reviews_name
                i['CustomerUrlId'] = customer_url_id

            favorite_shops_list += shops
        
    df_reviewers = pd.DataFrame.from_dict(reviewers_list)
    df_favorite_items = pd.DataFrame.from_dict(favorite_items_list)
    df_favorite_shops = pd.DataFrame.from_dict(favorite_shops_list)
    return df_reviewers, df_favorite_items, df_favorite_shops

    ##################################################################################################################


##################### Download htmls cointaining item urls sorted in categories#########################################
#for downloading urls  of items by categories
def extract_categories_ids(soup):
    categories = soup.find('div',class_="wt-tab-container wt-mb-xs-6").find_all('button', class_="wt-tab__item wt-ml-md-0 wt-mr-md-0 wt-justify-content-space-between")
    listings =[]
    for c in categories:
        listings.append({'ItemCategoryId':c.get('data-section-id'), 'ItemCategory':c.find('span', class_="wt-break-word wt-mr-xs-2").text.lstrip(" \n").rstrip(" \n")})
    return listings

def download_categories(url):
    soup = download_html(url)
    categories = extract_categories_ids(soup)
    df = pd.DataFrame.from_dict(categories)
    return soup, df

def download_item_urls_by_category(base_url, df_categories, dest_path):
    for cid, category in zip(df_categories['ItemCategoryId'].values, df_categories['ItemCategory'].values):
        print(category)
        dest = dest_path/category
        dest.mkdir(parents=True, exist_ok=True)
        #does pagination until page is empty
        for pn in range(1,100):
            soup = download_html(base_url.format(cid,pn))
            if soup == None:
                print('te pillaron')
                return
            #if called page number doesnt exist
            if len(soup.find_all('div',class_="empty-state")) != 0:
                print('finp')
                break
            save_html(soup, dest/(str(pn).zfill(3)+'.html'))
            print(f'\r {pn}      ',end='')
            custom_wait()
#########################################################################################################################


############################################ Extract item urls from downloaded htmls##################################
def extract_items_url(soup):
    '''extracts items urls ,name, and ids listed in an html file'''
    items = []
    raw_items = soup.find_all('div', attrs={'class': "js-merch-stash-check-listing v2-listing-card wt-position-relative wt-grid__item-xs-6 wt-flex-shrink-xs-1 wt-grid__item-xl-3 wt-grid__item-lg-4 wt-grid__item-md-4 listing-card-experimental-style"})
    for i in raw_items:
        itm = {}
        itm['ItemName'] = i.img.get('alt')
        itm['ItemUrl'] = i.a.get('href')
        itm['ItemId'] = i.a.get('data-listing-id')
        items.append(itm)
    return items
    
    
def extract_items_list_from_folder(path):
    paths = sorted(list(path.rglob('*.html')))
    all_items = []
    for p in paths:
        items = extract_items_url(open_html(p))
        #add category to each item
        for i in items:
            i['ItemCategory'] = p.parent.name
        all_items += items
    df = pd.DataFrame.from_dict(all_items)
    return df
#######################################################################################################################


#################################### Download items htmls ##############################################################
def download_items_htmls(df_item_list, dest_path):
    for cnt,itm in enumerate(df_item_list.itertuples()):
        path = dest_path/itm.ItemCategory
        
        if not os.path.exists(path):
            path.mkdir(parents=True, exist_ok=True)
        
        soup = download_html(itm.ItemUrl)
        if soup == None:
            print('te pillaron')
            return
        save_html(soup,path/(itm.ItemId+'.html'))
        print(f"\r{cnt} {itm.ItemName}                                  ",end='')
        
        custom_wait()
########################################################################################################################




########################################## Extract Data from downloaded items Htmls#################################
def extract_item_name(soup):
    return soup.find('h1', class_= "wt-text-body-03 wt-line-height-tight wt-break-word").text.lstrip(" \n").rstrip(" \n")

def extract_image_url(soup):
    return soup.find('img', attrs={'data-index':"0"}).get('src')

def extract_n_reviews(soup):
    sr = soup.find('span', class_ = "wt-badge wt-badge--status-02 wt-ml-xs-2")
    if sr is None:
        return 0
    else:
        return int(sr.text.replace(',',''))

def extract_is_bestseller(soup):
    bt = soup.find('button', class_="wt-popover__trigger wt-display-inline-flex-xs wt-align-items-center wt-popover__trigger--underline wt-text-caption")
    if bt is None:
        return False
    else:
        best  = bt.find('span',class_="wt-display-inline-block")
        if best is None:
            return False
        else:
            return True
        
def extract_item_id(soup):
    #item_id = soup.find('button', class_="btn--focus wt-position-absolute wt-btn wt-btn--light wt-btn--small wt-z-index-2 wt-btn--filled wt-btn--icon wt-btn--fixed-floating wt-position-right wt-mr-xs-2 wt-mt-xs-2").get('data-listing-id')
    url = soup.find('p', class_='wt-text-body-01 wt-mr-xs-1').a['href']
    item_id = re.search('id=[0-9]+',url).group()[3:]
    return item_id

def extract_original_price(soup):
    sp = soup.find('div', attrs={'data-buy-box-region':"price"}).find('div', class_="wt-text-strikethrough wt-mr-xs-1")
    if sp is None:
        return ''
    return re.search('[0-9]*[.]*[0-9]+', sp.text).group()

def extract_sale_price(soup):
    sp = soup.find('div', attrs={'data-buy-box-region':"price"}).p.text
    return re.search('[0-9]*[.]*[0-9]+', sp).group()

def extract_price_currency(soup):
    curr = soup.find('div', attrs={'data-buy-box-region':"price"}).p.text
    return re.search('[^ \n\t\r][0-9]*[.]*[0-9]+', curr).group()[0]



def extract_item_data_from_html(soup):
    data ={}
    data['ItemId'] = extract_item_id(soup)
    data['ItemName'] = extract_item_name(soup)
    data['PriceCurrency'] = extract_price_currency(soup)

    oprice = extract_original_price(soup)
    if oprice == '':
        #if original price is empty, it means that the item has no sale price
        #original price will appear when using extract sale price function
        data['OriginalPrice'] = extract_sale_price(soup)
        data['SalePrice'] = np.NaN
    else:
        data['OriginalPrice'] = oprice
        data['SalePrice'] = extract_sale_price(soup)
    data['NumReviews'] = extract_n_reviews(soup)    
    data['IsBestseller'] = extract_is_bestseller(soup)  
    data['ImageUrl'] = extract_image_url(soup)
    return data

def extract_items_data_from_folder(items_path):
    items_data = []
    for c,i in enumerate(items_path.rglob('*.html')):
        print(f'\r {c}  {i}    ',end='')
        soup = open_html(i)
        it = extract_item_data_from_html(soup)
        #add category from file path
        it['ItemCategory'] = i.parent.name
        items_data.append(it)
        #print(f'\r {c}  {i}    ',end='')
    df = pd.DataFrame.from_dict(items_data)
    return df
#######################################################################################################################



##################################Extract some items data from reviews dataframe########################
def extract_items_data_from_reviews(df_reviews):
    #convert reviewdate string to date datatype
    df_reviews['ReviewDate'] =  pd.to_datetime(df_reviews['ReviewDate'], format='%Y-%m-%d')
    item_groups = df_reviews.groupby('ItemId')
    df_items_from_reviews = item_groups.aggregate(NumCalcReviews=('CustomerName','size'),
                                              NumCalcStars=('Stars','mean'),
                                              OldestReviewDate=('ReviewDate','min'),
                                              NewestReviewDate=('ReviewDate','max'))
    df_items_from_reviews = df_items_from_reviews.reset_index()
    return df_items_from_reviews
#########################################################################################################


######################################Download Item images##############################################
def download_item_images(df_items, dest_path, start_idx=0, end_idx=None):
    #dest_path.mkdir(parents=True, exist_ok=True)
    end_idx = df_items.shape[0] if end_idx is None else end_idx
    for r in range(start_idx,end_idx):
        url = df_items.loc[r]['ImageUrl']
        categ = df_items.loc[r]['ItemCategory']
        iid = df_items.loc[r]['ItemId']
        (dest_path/categ).mkdir(parents=True, exist_ok=True)
        path = dest_path/categ/(str(iid)+url[-4:])
        download_img(url, path)
        print(f'\r {r+1} of {end_idx} {path}')
        custom_wait()
#########################################################################################################
