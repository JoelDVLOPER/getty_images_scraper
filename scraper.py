import requests
from bs4 import BeautifulSoup
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
import tkinter
import os
import validators
import time

def sopa(driver_property, parser, stuff):
    soup = BeautifulSoup(driver_property, parser)
    global find
    find = soup.find_all(stuff)

def folder_inexistent(dirs):
        print('Path does not exist. Created one.')
        os.makedirs(dirs)

while True:
        url_input =  input('Enter your URL.')
        if validators.url(url_input):
            break
        else:
            print('URL is invalid. Check if you may have inputted it incorrectly.')

while True:
    try:
        img_amount = int(input('Enter the amount of images.'))
        if type(img_amount) == int:
            break
    except ValueError:
        print('Not an integer. Please insert an integer.')

relative_url = url_input.split('/', 3)[-1]# gets the section connected to main url
base_url = url_input.split('/', 3)[2] # gets the main url
url_prefix = url_input.split('/')[0] # gets the starting url points or whatever it's called, like https:
root = tkinter.Tk()
root.withdraw() 

while True:
    global directory
    directory = filedialog.askdirectory()
    if type(directory) == tuple:
        print('No folder was selected.')
    elif not os.path.exists(directory):
        folder_inexistent(directory)
        break
    else:
        break

driver = webdriver.Firefox()
driver.get(f'{url_prefix}//{base_url}/{relative_url}')
img_url = []
file_names = []
file_counter = 0 
img_counter = 0
SCROLL_PAUSE_TIME = 2

while True:
    captionsoup  = BeautifulSoup(driver.page_source, 'html.parser')
    caption = captionsoup.find_all('figcaption')
    sopa(driver.page_source, 'html.parser', 'img')
    # Scroll down to bottom)
    next_page = driver.find_element(By.CSS_SELECTOR, '.Npj3TMjwvq4A76qbyQTN')
    driver.execute_script("arguments[0].scrollIntoView();", next_page)
    # iterate through website body, find img urls and put them into a list
    for c in caption:
        file_names.append(c.text)
    for f in find:
        if 'src':
            src = f.get('src')
            if src is not None and src not in img_url and '.svg' not in src:
                    img_url.append(src)
                    img_counter += 1
    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)
    # Calculate new scroll height and compare with last scroll height
    # usually means that the page has no more content to show
    if img_counter >= img_amount:
        break
    elif next_page is None:
        print('No more pages.')
        break
    else:
        driver.execute_script("arguments[0].click();", next_page)
        time.sleep(4)
driver.quit()

file_name_tracker = {}
for im, fig in zip(img_url, file_names):
    if im.startswith('/'):
        im = url_prefix + '//' + base_url + im
    re = requests.get(im)
    # used for tracking duplicate file names and assigning them a number if it is a duplicate
    if fig not in file_name_tracker:
        file_name_tracker[fig] = 1
        file_path = os.path.join(directory, f'{fig}')
    else:
        file_name_tracker[fig] += 1
        file_path = os.path.join(directory, f'{fig}_{file_name_tracker[fig]}')
    if not os.path.exists(directory):
        folder_inexistent(directory)
    with open(file_path, 'wb') as file:
        for images in re:
            file.write(images)
    file_counter += 1
    print(f'Downloaded file: {fig}')
    if file_counter >= img_amount:
        break

if file_counter > 0:
    print(f'Finished Downloading!\nTotal downloaded: {file_counter} files saved at {directory}.')
else:
    print('No images were found.')
