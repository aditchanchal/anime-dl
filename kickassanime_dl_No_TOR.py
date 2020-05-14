#!/usr/bin/python3
import requests
import re
from bs4 import BeautifulSoup
import m3u8
from time import time as timer
from multiprocessing.pool import ThreadPool
import sys
from tqdm import tqdm
import time
from selenium import webdriver
#from torrequest import TorRequest
import json
import math
import pyfiglet

# ANSI escape code to delete printed line
ERASE_LINE = '\033[2K'


# Setting up asci text banner
ascii_banner = pyfiglet.figlet_format("Anime - dL", justify='right')
print(ascii_banner)


# Function to print Text with blinking dots
def print_start(text):
    print(f"{text}\033[6m....", end="\r", flush=True)

# Function to erase current line and print ✔ Text


def print_end(text, color_code):
    print(ERASE_LINE, end="\r", flush=True)
    print("\033[25m\033", end="\r", flush=True)
    print(f"\n\033[{color_code}m✔\033[0m {text}\n")


print_start("CONFIGURING Anime-dl")

# Setting up TOR
# tr = TorRequest(password='xxxxxx')
# tr.reset_identity()

# Setting up SELENIUM
options = webdriver.FirefoxOptions()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)


# Used when page/iframe loads slowly
def selenium_get(url):
    driver.get(url)
    # time.sleep(5)
    page0 = driver.page_source
    soup = BeautifulSoup(page0, 'html.parser')
    return soup


# Using requests to fetch html
def tor_get(url):
    req = requests.get(url)
    req.raise_for_status()
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup

# Extracts title & resolution-wise m3u8 dict from iframes


def get_master_m3u8(anime_page):
    title = anime_page.find('h1', {'class': 'title'}).text
    embed_iframe = anime_page.find('iframe', {'class': 'embed-responsive-item'}).get('src')
    iframe = selenium_get(embed_iframe)
    #-to-choose-server-
    # iframe.find('div',{'class':'control-wrapper'}).find('select',{'id':'server-list'}).find_all('option')
    def_server_iframe = iframe.find('iframe', {'src': re.compile(r'http')}).get('src')

    iframe = tor_get(def_server_iframe)
    m3u8_iframe = iframe.find('iframe', {'id': 'pref'}).get('src')

    base_url = def_server_iframe.split('?', 1)[0]  # removing query parameter i.e., after ?
    base_url = base_url.rsplit('/', 1)[0]  # removing last path i.e., player.php
    m3u8_iframe_url = base_url + '/' + m3u8_iframe

    iframe = selenium_get(m3u8_iframe_url)
    # Keep in check the following "id-player" tag w.r.t. kickassanime
    embed_vid = iframe.find('iframe', {'src': re.compile(r'http')}).get('src')

    # Extracting url for m3u8 file
    m3u8_url = tor_get(embed_vid)
    scripts = m3u8_url.find_all('script')
    # URL is stored in "var config" as key-value pair
    config = re.compile(r'var config = (.*?);')

    master_m3u8_url = ''
    for script in scripts:
        if(script.string and config.search(script.string) != None):
            m = config.search(script.string)
            master_m3u8_url = json.loads(m.group(1))['metadata']['qualities']['auto'][0]['url']
            break

    master_m3u8 = requests.get(master_m3u8_url)
    master_m3u8 = m3u8.loads(master_m3u8.text)
    master_m3u8 = master_m3u8.data['playlists']

    # Extracting resolution and corresponding m3u8 url
    res_m3u8 = {}
    for item in master_m3u8:
        res = json.loads(item['stream_info']['name'])
        if res not in res_m3u8:
            res_m3u8[res] = item['uri']

    return title, res_m3u8

# Get all ts file links of an episode


def get_ts_urls(resolution, res_m3u8):
    res_m3u8_sorted = sorted(res_m3u8.items(), key=lambda x: int(x[0]))
    if resolution in res_m3u8:
        episode_url = res_m3u8[resolution]
    else:
        # default resolution
        episode_url = res_m3u8_sorted[math.ceil(len(res_m3u8_sorted) / 2) - 1][1]
        resolution = res_m3u8_sorted[math.ceil(len(res_m3u8_sorted) / 2) - 1][0]

    ts_m3u8 = requests.get(episode_url)
    ts_m3u8 = m3u8.loads(ts_m3u8.text)

    ts_urls = [ts['uri'] for ts in ts_m3u8.data['segments']]
    base_url = re.search(r'(http[\S]+.com)', episode_url).group(1)
    ts_urls = [base_url + ts_url for ts_url in ts_urls]

    return resolution, ts_urls

# Function to fetch one ts file


def fetch_url(ts_url):
    ts_i = requests.get(ts_url)
    return ts_i.content

# Download and write all the ts files into current directory


def ts_downloader(title, resolution, ts_urls):
    episode = re.search(r'((E|e)pisode \d+)', title).group(1)
    start = timer()

    file_name = title + '.ts'
    size = 0

    # Multi-threading and progress bar
    download_bar = tqdm(ThreadPool(8).imap(fetch_url, ts_urls), total=len(ts_urls), desc=episode + ' ' + resolution + 'p ' + str(size / (1024 * 1024)) + 'MB')

    with open(file_name, 'wb') as f:
        for result in download_bar:
            size += sys.getsizeof(result)
            download_bar.set_description(episode + ' ' + resolution + 'p ' + str(round(size / (1024 * 1024), 2)) + 'MB')
            f.write(result)

    # --TESTING--
    # for i in tqdm(range(100), desc=episode + ' ' + resolution + 'p'):
    #     time.sleep(0.01)

    t1 = timer() - start
    print("Time Elapsed:", t1 / 60, 'Mins')

# Extract URL of next episode


def get_next_ep_url(anime_episode_url, anime_page):
    anchors = anime_page.find('div', {'id': 'sidebar-anime-info'}).find_all('a')
    for a in anchors:
        if(a.text and re.search(r'Next Episode \d+', a.text) != None):
            next_episode_href = a.get('href')
            break

    base_url = anime_episode_url.rsplit('/', 3)[0]
    next_episode_url = base_url + next_episode_href
    return next_episode_url

# Function calls to download one episode


def download_episode(anime_page, resolution):
    title, res_m3u8 = get_master_m3u8(anime_page)
    new_resolution, ts_urls = get_ts_urls(resolution, res_m3u8)
    ts_downloader(title, new_resolution, ts_urls)

# Function calls to download range of episodes


def download_anime():
    print_end("CONFIGURATION COMPLETE.", 93)

    # Ask User for episode link and no. of episodes to download
    anime_episode_url = input("Enter the URL of the episode: ")
    no_episodes = input("Number of additional episodes to download in continuation to this: ")

    print_start("FETCHING RESOLUTIONS")

    anime_page = selenium_get(anime_episode_url)
    # Returns title & resolution-wise m3u8 dict
    title, res_m3u8 = get_master_m3u8(anime_page)

    print_end("FETCHING COMPLETE.", 96)

    print('Available video resolutions are: ', list(res_m3u8.keys())
          )

    # Ask User for video resolution
    resolution = input("Select video resolution: ")
    print('\n')

    new_resolution, ts_urls = get_ts_urls(resolution, res_m3u8)

    # Download episode of given url
    ts_downloader(title, new_resolution, ts_urls)

    # Loop over additional episodes
    for i in range(int(no_episodes)):
        print('\n')
        anime_episode_url = get_next_ep_url(anime_episode_url, anime_page)
        anime_page = selenium_get(anime_episode_url)
        download_episode(anime_page, resolution)


if __name__ == "__main__":
    download_anime()
    print_start("CLOSING Anime-dl")
    driver.quit()
    print_end("TASK DONE.", 92)
