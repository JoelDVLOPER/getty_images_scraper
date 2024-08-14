import requests
from bs4 import BeautifulSoup
from tkinter import filedialog
from selenium import webdriver
import tkinter
import os
import time
import validators
# PARA HACER: tuple

def sopa(driver_property, parser):
    soup = BeautifulSoup(driver_property, parser)
    global img
    img = soup.find_all('img')

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
    directory = filedialog.askdirectory()
    if type(directory) == tuple or not os.path.exists(directory):
        print('No folder was selected, or folder does not exist.')
    else:
        break

driver = webdriver.Firefox()
driver.get(f'{url_prefix}//{base_url}/{relative_url}')
sopa(driver.page_source, 'html.parser')
img_url = []
file_counter = 0
img_counter = 0
SCROLL_PAUSE_TIME = 2
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    sopa(driver.page_source, 'html.parser')
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") 
    # iterate through website body, find img urls and put them into a list
    for i in img:
            if 'src':
                src = i.get('src')
                if src not in img_url:
                    img_url.append(src)
                    img_counter += 1
    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    # usually means that the page has no more content to show
    if new_height == last_height or img_counter >= img_amount:
        break
    last_height = new_height
driver.quit()

for im in img_url:
    if im.startswith('/'):
        im = url_prefix + '//' + base_url + im
    elif im.startswith('data:image/'):
        header, base64_data = im.split(',', 1)
        file_format = header.split('/')[1].split(';')[0]
        data = base64.b64decode(base64_data)
        file_name = f'{file_counter + 1}.{file_format}'
        file_path = os.path.join(directory, file_name)
        if not os.path.exists(directory):
            break
        with open(file_path, 'wb') as file:
            file.write(data)
        file_counter += 1
        print(f'Downloaded file: {file_name}')
    file_name = im.split('/')[-1] # gets the name of the file so it can be downloaded later
    re = requests.get(im)
    file_path = os.path.join(directory, file_name)
    if not os.path.exists(directory):
        break
    file_counter += 1
    with open(file_path, 'wb') as file:
        for q in re:
            file.write(q)
    print(f'Downloaded file: {file_name}')
    if file_counter >= img_amount:
        break

if file_counter > 0:
    print(f'Finished Downloading! \n Total downloaded: {file_counter} files saved at {directory}.')
elif 0 < file_counter < img_amount:
    print(f'Finished Downloading!\nFailed to fulfill amount of images asked. \n Total downloaded: {file_counter} files saved at {directory}.')
elif not os.path.exists(directory):
    print('Session was interrupted and could not run as intended')
else:
    print('No images were found.')
