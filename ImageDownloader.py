import os
import json
import time
from requestium import Session
import requests

from multiprocessing import Pool
from selenium import webdriver

def get_image_links( main_keyword, supplemented_keywords, link_file_path, num_requested=1000):
    s = Session('chromedriver',
                browser='chrome',
                default_timeout=15,
                webdriver_options={'arguments': ['headless', 'disable-gpu']}
                )
    number_of_scrolls = int(num_requested / 400) + 1
    img_urls = set()
    for i in range(len(supplemented_keywords)):
        search_query = main_keyword + ' ' + supplemented_keywords[i]
        url = "https://www.google.com/search?q=" + search_query + "&source=lnms&tbm=isch"
        s.driver.get(url)

        for _ in range(number_of_scrolls):
            for __ in range(10):
                s.driver.execute_script("window.scrollBy(0, 1000000)")
                time.sleep(2)
            time.sleep(5)
            try:
                s.driver.find_element_by_xpath("//input[@value='Show more results']").click()
            except Exception as e:
                print("Process-{0} reach the end of page or get the maximum number of requested images, args:{2}".format(
                    main_keyword, e.args))
                break

        images = s.driver.find_elements_by_xpath('//div[contains(@class,"rg_meta")]')
        for img in images:
            img_url = json.loads(img.get_attribute('innerHTML'))["ou"]
            img_urls.add(img_url)
        print('Process-{0} add keyword {1} , got {2} image urls so far'.format(main_keyword, supplemented_keywords[i],
                                                                               len(img_urls)))
    print('Process-{0} totally get {1} images'.format(main_keyword, len(img_urls)))
    s.driver.quit()

    with open(link_file_path, 'w') as wf:
        for url in img_urls:
            wf.write(url + '\n')
    print('Store all the links in file {0}'.format(link_file_path))

def download_with_time_limit(link_file_path, download_dir):
    main_keyword = link_file_path.split('/')[-1]
    img_dir = download_dir + main_keyword + '/'
    count = 0
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    with open(link_file_path, 'r') as rf:
        for link in rf:
            s = requests.session()
            s.keep_alive = False
            proxies = {
                'http': 'socks5://127.0.0.1:1080',
                'https': 'socks5://127.0.0.1:1080'
            }
            s.proxies = proxies
            try:
                img = s.get(link.strip(), stream=False, timeout=(10, 20))
                file_path = img_dir + '{0}.jpg'.format(count)
                with open(file_path,'wb') as wf:
                    wf.write(img.content)
                print('Process-{0} download image {1}/{2}.jpg'.format(main_keyword, main_keyword, count))
                count += 1
                time.sleep(2)
            except Exception as e:
                print('Error while downloading image {0}error type:{1}, args:{2}'.format(link, type(e), e.args))
                continue


if __name__ == "__main__":
    main_keywords = ['pie chart', 'bar chart', 'rectangle treemap', 'line chart', 'scatter plot', 'box plot',
                     'rectangle heatmap', 'heatmap map'
                     ]

    supplemented_keywords = ['jpg']

    download_dir = './data/'
    link_files_dir = './data/link_files/'

    for keyword in main_keywords:
        link_file_path = link_files_dir + keyword
        get_image_links(keyword, supplemented_keywords, link_file_path)

    for keyword in main_keywords:
        link_file_path = link_files_dir + keyword
        download_with_time_limit(link_file_path, download_dir)

