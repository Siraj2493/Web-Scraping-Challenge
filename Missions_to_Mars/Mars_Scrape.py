from bs4 import BeautifulSoup
from splinter import Browser
import time
import pandas as pd
import re
import pymongo

# NASA Mars News
# 
def scrape_mars_news(browser):
    """
    Scraps NASA Mars news and returns the first news title and the associated teaser
    """
    nasa_news_url = "https://mars.nasa.gov/news/"
    browser.visit(nasa_news_url)

    time.sleep(5)
    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    news = soup.find("div", class_='list_text')
    news_title = news.find("div", class_="content_title").text
    news_p = news.find("div", class_ ="article_teaser_body").text
    return([news_title, news_p])


# JPL Mars Space Images - Featured Image
# 
def scrape_jpl_image(browser):
    """
    Scrapes jpl images for the featured mars image and returns  the 
    link to the high res jpeg
    """

    jpl_image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_image_url)
    time.sleep(5)


    browser.click_link_by_id("full_image")
    time.sleep(5)

    browser.click_link_by_partial_text('more info')
    time.sleep(5)

    jpl_image_html = browser.html
    jpl_image_soup = BeautifulSoup(jpl_image_html, 'html.parser')

    featured_image_urls = jpl_image_soup.find_all("div", class_="download_tiff")
    jpl_jpg_image = featured_image_urls[1].a.get('href')
    return("https:" + jpl_jpg_image)


# Mars Weather
# 
def scrape_mars_weather(browser):
    """
    Scrapes twitter for the most recent mars weathe rreport and returns
    the string
    """
    mars_weather_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(mars_weather_url)
    time.sleep(5)

    mars_weather_html = browser.html
    mars_weather_soup = BeautifulSoup(mars_weather_html, 'html.parser')

    mars_weather_posts = mars_weather_soup.find_all("span", class_="css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0")
    for post in mars_weather_posts:
        if "InSight sol" in post.text:
            mars_weather = post.text
            break
    return(mars_weather)


# Mars Facts
# 
def scrape_mars_facts(filename, browser):
    """
    scraps mars facts from space-facts.com and outputs and them table of the results
    """
    mars_facts_url = "https://space-facts.com/mars/"
    mars_facts_df = pd.read_html(mars_facts_url, match="Equatorial Diameter")
    mars_facts_df[0].to_html(filename, header=False, index=False)
    mars_facts_new = mars_facts_df[0].set_index(0)
    return(mars_facts_new.to_dict()[1])


# Mars Hemispheres
# 
def scrape_hemi_images(browser):
    """
    scrapes astrogeology.usgs.gov and returns links of high res images of each
    of the hemispheres
    """
    hemi_main_link = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_main_link)
    time.sleep(5)

    hemi_main_html = browser.html
    hemi_main_soup = BeautifulSoup(hemi_main_html, 'html.parser')

    hemi_urls = hemi_main_soup.find_all("div", class_="description")

    hemisphere_image_urls = []

    for hemi in hemi_urls:
        browser.visit("https://astrogeology.usgs.gov" + hemi.a.get('href'))
        time.sleep(5)
        
        hemi_html = browser.html
        hemi_soup = BeautifulSoup(hemi_html, 'html.parser')
        
        for link in hemi_soup.find_all('a'):
            if link.text == "Sample":
                hemisphere_image_urls.append({"title" : re.search("(.*) Enhanced",hemi_soup.find("h2", class_="title").text)[1], "img_url" : link.get('href')})
                break

    return(hemisphere_image_urls)

def load_db(data_to_load):

    #setup the database connection
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.mars_db
    
    # coment out this line to keep old documents
    db.mars.drop()

    # load the data
    db.mars.insert_one(data_to_load)
    
    # close the database connection
    client.close()

def scrape():
    mars = {}

    # setup the browser
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)

    mars['news_title'], mars['news_teaser'] = scrape_mars_news(browser)
    mars['jpl_image'] = scrape_jpl_image(browser)
    mars['weather_str'] = scrape_mars_weather(browser)
    mars['facts'] = scrape_mars_facts('mars_facts.html', browser)
    mars['hemi_image1'], mars['hemi_image2'], mars['hemi_image3'], mars['hemi_image4'] = scrape_hemi_images(browser)

    load_db(mars)

if __name__ == "__main__":
    scrape()