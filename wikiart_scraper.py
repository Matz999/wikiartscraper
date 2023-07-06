from bs4 import BeautifulSoup
import requests
import urllib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


driver = webdriver.Chrome()


def get_links(url):
    driver.get(url)
    # THIS FUNCTION WILL RETURN A LIST
    link_list = []
    # THE PAGE IS DIVIDED IN DIV BLOCKS

    while True:
        try:
            loadbool = driver.find_element(
                By.XPATH, "//div[@class='masonry-load-more-button-wrapper']").is_displayed()
            time.sleep(2)
            loadclick = driver.find_element(
                By.XPATH, "//div[@class='masonry-load-more-button-wrapper']").click()
            time.sleep(5)
            # IF AN ALERT HAPPENS THE WE SHOULD CLICK ON THE BUTTON

            alertbool = driver.find_element(
                By.XPATH, "//div[@class='needsclick  kl-private-reset-css-Xuajs1']").is_displayed()
            if alertbool is True:
                alert = driver.find_element(
                    By.XPATH, "//button[@class='needsclick klaviyo-close-form kl-private-reset-css-Xuajs1']").click()
            time.sleep(2)
            # RIGHT NOW THIS ALERT CODE INTERRUPTS THE TRY-EXCEPT CODE. IT SEEMS TO WORK ONLY FOR TWO CYCLES
        except Exception as e:
            print(e)
            break
    print("Complete")

    blocks = driver.find_elements(By.CLASS_NAME, "title-block")
    i = 0

    for block in blocks:
        # WE ARE SEARCHING FOR THE LINKS INSIDE THE "A" TAGS
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            if link.get_attribute("class") == "artwork-name ng-binding":
                link = link.get_attribute("href")
                i += 1
                link_list.append(link)
                print(f"{i} of {len(blocks)} links fetched")
            if i == len(blocks):  # IF THE COUNTER IS EQUAL TO THE LENGHT OF BLOCKS THE PROCESS IS OVER
                return link_list


link_list = get_links(
    "https://www.wikiart.org/en/paintings-by-style/proto-renaissance?select=featured#!#filterName:featured,viewType:masonry")
i = 0
for link in link_list:
    try:
        # the page offers two types of descriptions, so we have to have two types of search in mind this doesnt work.
        # body = soup.find("p", {"itemprop": "description"}).text

        url = link
        html_text = requests.get(url).text
        soup = BeautifulSoup(html_text, 'lxml')
        html = requests.get(url)
        title = soup.find('h3').text.replace('"', '')
        name = soup.find("span", {"itemprop": "name"}).text.replace(' ', '')
        name = name.strip()

    # SOMETIMES THERE IS A DESCRIPTION AND SOMETIMES THERE IS NOT, IN THE LATTER CASE BODY SHALL BE AN EMPTY STRING
        if soup.find("div", {"id": "info-tab-wikipediadescription"}) is None:
            body = ""
        else:
            body = soup.find(
                "div", {"id": "info-tab-wikipediadescription"}).text

    # SOMETIMES THERE IS A DATE AND SOMETIMES THERE IS NOT, IN THE LATTER CASE DATE SHALL BE AN EMPTY STRING
        if soup.find("span", {"itemprop": "dateCreated"}) is None:
            date = ""
        else:
            date = soup.find(
                "span", {"itemprop": "dateCreated"}).text.replace(' ', '')

        maxres = soup.find(
            "span", {"class": "max-resolution"}).text.replace('px', '')
        print(maxres)
        img_filename = title + name + date + ".jpg"

    # we have to use selenium

        driver = webdriver.Chrome()
        driver.get(url)
        is_all_sizes_visible = driver.find_element(
            By.CLASS_NAME, "all-sizes").is_displayed()
        if is_all_sizes_visible is True:  # SOMETIMES THE VIEW ALL SIZES BUTTON IS NOT AVAILABLE IN THAT CASE WE WOULD USE XPATH TO GO TO THE ONLY AVAILABLE IMG
            driver.find_element(By.CLASS_NAME, "all-sizes").click()
            wait = WebDriverWait(driver, 1)
            original = driver.find_element(
                By.XPATH, f"//*[contains(text(), '{maxres}')]")
            src = original.get_attribute('href')

        else:
            src = driver.find_element(
                By.XPATH, "/html/body/div[2]/div[1]/section[1]/main/div[2]/aside/div[1]/img")

    # image download by urllib

        # HERE YOU SELECT THE DESIRED FOLDER
        path = 'C:\\'
        urllib.request.urlretrieve(src, path+img_filename)
        i += 1
        print(f"Downloaded: {src}")
        print(f"{i} of {len(link_list)}")
        driver.close()
    except:
        print("error")
