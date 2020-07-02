import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy
import time
from os import path

url = 'https://www.kijiji.ca/b-appartement-condo/ville-de-montreal'
baseurl = 'https://www.kijiji.ca'
base_quebec = '/c37l1700281'
page_nos = '/page-'
apartment = 'b-appartement-condo'
room_rent = 'room rent'
ad_url = []
listing = []
url_to_save = []
title = []
prices = []
description = []
location = []
date_posted = []
features = []
links_from_text = []
listing_type = []
ad_id = []
save_points = [1000,2000,3000,4000,5000,6000,7000]

# Getting the URLs
def get_urls(no_pages):

    if path.exists('links.txt'):
        with open('links.txt', 'r') as f:
            links_from_text = f.readlines()
        get_details(links_from_text)
    else:
        for i in range(no_pages):
            url_final = url+page_nos+str(i)+base_quebec
            response = requests.get(url_final)
            soup = BeautifulSoup(response.text, "html.parser")
            advtTitles = soup.findAll('div', attrs={'class' : 'title'})
            try:
                for link in advtTitles:
                    adlink = baseurl+link.find('a')['href']
                    ad_url.append(adlink)
            except(Exception):
                print(Exception)
            #time.sleep(1)
        print(len(ad_url))

        ## since connection gets closed by the server its better to save the links to a text file
        save_links(ad_url)
        get_details(ad_url)

def get_details(urls):
    
    urls = urls[6766:]
    print(len(urls))

    i =0;
    try:
        for url in urls:
            print(url)
            listDetails = ""
            listDetailsTwo = []
            url = url.rstrip('\n')
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            try:
                adTitle = soup.select_one("h1[class*=title-2323565163]").text
                title.append(adTitle)
                adPrice = soup.select_one("span[class*=currentPrice-2842943473]").text
                prices.append(adPrice)
                adDescription = soup.find_all('div', attrs={'class' : 'descriptionContainer-3544745383'})
                description.append(adDescription)
                adLocation = soup.find('span', attrs={'class' : 'address-3617944557'})
                location.append(adLocation)
                date = soup.find('time')   
                date_posted.append(date)

                # get features from the listing 
                # we have two kinds of listing apartments and room rentals.

                if apartment in url:
                    adfts = soup.find_all('li', attrs={'class' : 'realEstateAttribute-3347692688'})
                    for ft in adfts:
                        #dd = ft.find('div').text
                        dd = ft.find_all('div')
                        listDetails = listDetails + str(dd) + " || "
                    features.append(listDetails)
                    listing_type.append(apartment)
                    url_to_save.append(url)
                    ad_id = get_ad_id(url)
                    ad_id.append(ad_id)
                else:                
                    adfts = soup.find_all('dl', attrs={'class' : 'itemAttribute-983037059'})
                    for ft in adfts:
                        dd = ft.find('dd').text
                        dt = ft.find('dt').text
                        listDetails = listDetails + str(dt) + " : " + str(dd) + " || "
                    features.append(listDetails)
                    listing_type.append(room_rent)
                    url_to_save.append(url)
                    ad_id = get_ad_id(url)
                    ad_id.append(ad_id)
                print("Scraping listing : ",str(i))
                #response.close()
                i += 1
                if i in save_points:
                    save_to_disk(i)
                    #break
                time.sleep(1)
            except Exception as e:
                pass
        save_to_disk(i)
    except Exception as e: 
        print(e)
        pass
    #save_to_disk()

def get_ad_id(advt):
    advtList = advt.split("/")
    adlen = len(advtList)
    return advtList[adlen-1]


def save_to_disk(i):
    print("saving ***")
    name='kijiji'+str(i)+'.csv'
    d = {'ad_id':ad_id, 'Title':title,'Price':prices,'Description':description, 'Location':location,'Ddate Posted':date_posted, 'Location':location, 'Features' : features, 'URL':url_to_save, 'Type' : listing_type}
    df = pd.concat([pd.Series(v, name=k) for k, v in d.items()], axis=1)
    df.to_csv(name,index=False)
    reset_all()
    
def save_links(links):
    with open('links.txt', 'w') as f:
        for item in links:
            f.write("%s\n" % item)

    f.close()

def reset_all():
    print('cleaning')
    ad_id.clear()
    title.clear()
    prices.clear()
    description.clear()
    date_posted.clear()
    location.clear()
    features.clear()
    url_to_save.clear()
    listing_type.clear()
    

# call main methond to start scraping by passing number of pages wanted to scrape  
no_pages = 300
get_urls(no_pages)