#Import dependencies
import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
from splinter import Browser
import pymongo

# setup mongo connection
conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)
db = client.srcape_mars_app
collection = db.mars_results

#Create Scrape function
def scrape():

    # Initialize Chromedriver 
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    #News Article grab
    #Set variable for NASA Mars News site
    News_url = 'https://mars.nasa.gov/news/'

    browser.visit(News_url)

    #Pull html text
    News_response = browser.html

    #Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(News_response, 'html.parser')

    #title & description
    news_title = soup.find('div', 'content_title', 'a').text
    news_p = soup.find('div', 'article_teaser_body').text


    #Featured Image grab
    #Set up splinter browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    Image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(Image_url)
    image_soup = BeautifulSoup(Image_url, 'html.parser')

    link = 'https://www.jpl.nasa.gov'
    featured_img = image_soup.find('div', class_='carousel_items')

    image_url = featured_img.find('article', style_='background-image:')


    featured_img_url= link +'/s'+ image_url + '.jpg'

    #weather grab
    #Set up splinter browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    #Mars Weather Twitter Account link
    Weather_url = 'https://twitter.com/marswxreport?lang=en'

    browser.visit(Weather_url)
    weather_tweet = browser.html

    #Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(weather_tweet, 'html.parser')

    #get latest tweet
    mars_weather = soup.find('p', 'TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text

    #Factuales
    #Set up splinter browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    #Set variable for Mars Facts Webpage
    Facts_url = 'https://space-facts.com/mars/'

    #Visit url
    #browser.visit(Facts_url)
    #mars_facts_html = browser.html

    tables=pd.read_html(Facts_url)
    df=tables[0]
    df.columns=['Subject','Value']

    #export pandadf to html
    mars_facts_table =df.to_html()
    mars_facts_table.replace("\n","")
    df.to_html('mars_facts_table.html')


    #Hemisperes
    #Set up splinter browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    #Set variable for Mars Facts Webpage
    Hemi_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    #Visit url
    browser.visit(Hemi_url)
    Hemi_response = browser.html

    #Create BeautifulSoup object; parse with 'html.parser'
    Hemi_soup = BeautifulSoup(Hemi_response, 'html.parser')

    #Retrieve class for each hemisphere
    returns = Hemi_soup.find('div', 'collapsible results')

    #Retrieve all anchors
    hemi = returns.find_all('div', {"class": 'description'})

    #Create empty list to hold dictionaries
    hemi_image_urls = []

    #Loop through all anchors for each hemisphere class
    for descrip in hemi:
        a = descrip.find('a')
        
        #title and link
        title = a.h3.text
        link = 'https://astrogeology.usgs.gov' + a['href']

        browser.visit(link)
        time.sleep(5)      #living on a prayer

        #link tp image
        page = browser.html
        results = BeautifulSoup(page, 'html.parser')
        image_link = results.find('div', 'downloads').find('li').a['href']

        #dictionary for title & image
        image_dict = {}
        image_dict['title'] = title
        image_dict['img_url'] = image_link

        hemi_image_urls.append(image_dict)   

    #Convert results to a dataframe for display
    #looksee = pd.DataFrame(hemi_image_urls, columns= ["title","img_url"])

    
    mars_results = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_img_url": featured_img_url,
        "mars_weather": mars_weather,
        "mars_facts_table": mars_facts_table,
        "hemi_image_urls": hemi_image_urls
    }
    collection.insert_many(mars_results)
    return mars_results