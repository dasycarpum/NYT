#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-19

@author: Roland

@abstract: The objective is to extract from Amazon's website as much 
information as possible about each bestseller reviewed in the New-York Times. 
In addition to the 2 ISBNs that serve as identification keys, we will be able
to collect the rating, the average number of stars given, the price, the number
of pages of the book, its language, the publication date and the readers' 
reviews. The latter are composed of 4 main parts: the number of stars, the
title of the review, its text and the writing date.

"""

import random
import time
from datetime import datetime
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib3.exceptions import MaxRetryError





def find_customer_reviews_page(url, driver):
    """
    Navigate to the 'All Customer Reviews' page of a product on Amazon.

    This function loads the page of a product, waits for the 'Customer reviews' 
    section to load, scrolls to the section, clicks on it to navigate to the reviews 
    page, and then returns the URL of the 'All Customer Reviews' page.

    Args:
        url (str): The URL of the product on Amazon.

    Returns:
        str: The URL of the 'All Customer Reviews' page.

    Raises:
        Exception: If an error occurs while finding the 'See all reviews' button.

    Example:
        find_customer_reviews_page("https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20")
    
    """
    driver.get(url)

    time.sleep(3)  # let the page load

    # Wait for the 'customer reviews' section to be loaded
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "acrCustomerReviewText"))
    )

    # Use JavaScript to scroll to the 'customer reviews' element
    driver.execute_script("arguments[0].scrollIntoView();", element)

    # Use ActionChains to click the element
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()

    time.sleep(2)  # let the reviews page load

    # Check if we successfully navigated to the reviews page
    driver.get( driver.current_url)

    try:
        see_all_reviews_button = driver.find_element(By.LINK_TEXT, 'See more reviews')
        see_all_reviews_link = see_all_reviews_button.get_attribute('href')
        return see_all_reviews_link
    except Exception as e:
        print(f"An error occurred: {str(e)}")

        
def transform_url_for_specific_page(url, page):
    """
    Transform the URL for a specific page of reviews on Amazon.

    This function takes the base URL for the reviews of a book on Amazon, and 
    modifies it to access a specific page of reviews.

    Args:
        url (str): The base URL for the book reviews on Amazon.
        page (int): The page number to access.

    Returns:
        str: The modified URL that points to the specified page of reviews.

    Example:
        transform_url_for_specific_page("https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20", 2)
        
    """
    url_review_p = url.replace("cm_cr_dp_d_show_all_btm",
                               f"cm_cr_arp_d_paging_btm_next_{page}")
    url_review_p = url_review_p + f"&pageNumber={page}"
    
    return url_review_p


def scrape_reviews(url, driver):
    """
    Scrape reviews of a book from Amazon.

    This function reviews every review on the first 10 Amazon pages, extracts the review data (including the rating, title, text, and date), and returns the data.

    Args:
        url (str): The URL of the Amazon page for the book.
        driver (webdriver) : Selenium webdriver

    Return:
        list of dict : all scraped information

    Raises:
        Exception: If an error occurs in accessing the URL, parsing the 
        review, or writing to the file.

    Example:
        scrape_review("https://www.amazon.com/dp/006267112X?tag=NYTBSREV-20")
    """
    url_review = find_customer_reviews_page(url, driver)
    
    result = []
    page_reviews = []
    for p in range(1,11):
        try:
            url_review_p = transform_url_for_specific_page(url_review, p)
            driver.get(url_review_p)
        except Exception as e:
            print(f"Error in accessing URL: {e}")
            continue
    
        # Let the page load
        time.sleep(2)
    
        # Parse HTML with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    
        # Find and store reviews
        reviews = soup.find_all('div', {'data-hook': 'review'})
    
        for review in reviews:
            try:
                full_title = review.find('a', {'data-hook': 'review-title'}).text.strip()
                title_lines = full_title.split('\n')  # Split the title into lines
                title = title_lines[1] if len(title_lines) > 1 else full_title  
                rating_str = review.find('i', {'data-hook': 'review-star-rating'}).text.strip()
                rating = rating_str[:3] 
                date_str = review.find('span', {'data-hook': 'review-date'}).text.strip()
                body = review.find('span', {'data-hook': 'review-body'}).text.strip()
            except Exception as e:
                print(f"Error in parsing review: {e}")
                continue
    
            page_reviews.append({
                "stars": rating,
                "title": title,
                "text": body,
                "date": date_str
            })
    
    # Concatenated data
    return page_reviews
    
    
def scrape_amazon_book(amazon_url, driver, retry_count=0):
    """
    Scrapes details and reviews for a book product from Amazon.

    This function uses a webdriver to load an Amazon book product page and 
    parses the HTML with BeautifulSoup to extract relevant product details.
    The function also loads the review page of the book and scrapes review details. 
    
    Args:
        amazon_url (str): The URL of the Amazon book product page.
        driver (webdriver) : Selenium webdriver
        retry_count (int) : number of page access attempts

    Return:
        list of dict : all scraped information

    Raises:
        ValueError: If no element is found on the page matching the criteria 
        specified in the function.

    """
    # Get information from the main Amazon web page
    # =============================================
    # load the webpage
    driver.get(amazon_url)
    time.sleep(5)   # wait for the page to load

    # parse the HTML with Beautifulsoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    found_element = False
    products = []
    product = {"url": amazon_url}

    rating_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
    if rating_elem:
        found_element = True
        product["rating"] = rating_elem.get_text().strip().split()[0]
    else: # to solve the CAPTCHA problem
        if retry_count < 5:  # only retry up to 5 times
            return scrape_amazon_book(amazon_url, driver, retry_count + 1)
        else:
            raise ValueError("Failed to load page after multiple attempts")

    num_stars_elem = soup.find('span', {'class': 'a-icon-alt'})
    if num_stars_elem:
        found_element = True
        product["number_of_stars"] = num_stars_elem.get_text().strip().split()[0]

    price_elem = soup.find('span', {'class': 'a-size-base a-color-price a-color-price'})
    if price_elem:
        found_element = True
        product["price"] = price_elem.get_text().strip()

    num_pages_elem = soup.find('div', {'id':'rpi-attribute-book_details-fiona_pages'})
    if num_pages_elem:
        found_element = True
        product["number_of_pages"] = num_pages_elem.get_text().strip().split()[-2]

    language_elem = soup.find('div', {'id': 'rpi-attribute-language'})
    if language_elem:
        found_element = True
        product["language"] = language_elem.get_text().strip().split()[1]

    pub_date_elem = soup.find('div', {'id':'rpi-attribute-book_details-publication_date'})
    if pub_date_elem:
        found_element = True
        pub_date = pub_date_elem.get_text().strip().split()[-3:]
        date_str = " ".join(pub_date)
        date_obj = datetime.strptime(date_str, "%B %d, %Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        product["publication_date"] = formatted_date

    isbn_10_elem = soup.find('div', {'id': 'rpi-attribute-book_details-isbn10'})
    if isbn_10_elem:
        found_element = True
        product["ISBN-10"] = isbn_10_elem.get_text().strip().split()[-1]

    isbn_13_elem = soup.find('div', {'id': 'rpi-attribute-book_details-isbn13'})
    if isbn_13_elem:
        found_element = True
        product["ISBN-13"] = isbn_13_elem.get_text().strip().split()[-1]

    asin = amazon_url.split('/')[-1].split('=')[0].split('?')[0]

    # Reviews Amazon web pages
    # ========================
    # load the webpage
    driver.get('https://www.amazon.com/product-reviews/' + asin)
    time.sleep(2) # wait for the page to load

    # parse the HTML with Beautifulsoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Get total number of reviews
    ratings_reviews_text = soup.find('div',
                                     {'data-hook':
                                      'cr-filter-info-review-rating-count'})\
                                                            .get_text().strip()

    pattern = r'\d{1,3}(?:,\d{3})*' # matches numbers with or without commas
    matches = re.findall(pattern, ratings_reviews_text)
    reviews_count = int(matches[1].replace(',', ''))

    product["reviews_count"] = reviews_count

    # Get reviews on the first 10 pages
    product['reviews'] = scrape_reviews(amazon_url, driver)
    
    # Return data
    # ===========
    if found_element:
        products.append(product)
        return products
    else:
        raise ValueError("No element found")


def scrape_amazon_books(url):
    """
    Search for book details and reviews on the Amazon site

    Args:
        url (str): book URL to be scraped

    Return:
        data : book data scraped from Amazon

    Raises:
        NoSuchElementException: If Selenium can't locate a required element on a page.
        WebDriverException: If there is an issue with the webdriver or with loading a page.
        AttributeError: If BeautifulSoup can't locate a tag.
        Exception: If an unexpected error occurred.

    """
    # Adding a retry loop to handle connectivity issues to the Selenium server.
    max_attempts = 10  # maximum number of connection attempts
    
    for attempt in range(max_attempts):
        try:
            """
            driver = webdriver.Remote(
                command_executor='http://firefox:4444/wd/hub',
                desired_capabilities=DesiredCapabilities.FIREFOX)
            """
            driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
            delay = random.uniform(2.1, 5.1)  # generate random delay
            time.sleep(delay)
            break
        except MaxRetryError:
            if attempt < max_attempts - 1:  # no need to delay after the last attempt
                time.sleep(5)
                continue
            else:
                raise
        except Exception as e:
            print(f"An unexpected error occurred while trying to connect to the Selenium server: {e}")
            raise


    data = None  # Initialize data before the try block

    # Scraping unique product
    try:
        data = scrape_amazon_book(url, driver)
    except NoSuchElementException as e:
        print("\nSelenium couldn't find an element :", url)
        print("Error : ", e)
        raise
    except WebDriverException as e:
        print("\nThere was an issue with the webdriver or the page load :", url)
        print("Error : ", e)
        raise
    except AttributeError as e:
        print("\nBeautifulSoup couldn't find a tag :", url)
        print("Error : ", e)
        raise
    except Exception as e:
        print("\nAn unexpected error occurred :", url)
        print("Error : ", e)
        raise
    finally:    
        # Close the webdriver
        driver.quit()

    return data
