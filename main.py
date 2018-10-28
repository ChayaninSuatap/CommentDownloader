import sqlite3
from time import sleep
from util import *
from queue import Queue
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.
options.add_argument('log-level=3')
options.add_argument("--window-size=1920x1080")
chrome_prefs = {}
options.experimental_options["prefs"] = chrome_prefs
chrome_prefs["profile.default_content_settings"] = {"images": 2}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}

print('loading db')
app_ids = load_datasets_from_db()
print('db loaded',len(app_ids))

#make db
create_db()

#start crawling
def crawlcomment(app_ids, thread_index):
    driver = webdriver.Chrome(chrome_options=options, executable_path='./chromedriver')
    con = connect_db()
    con.isolation_level = None
    con.execute("PRAGMA busy_timeout = 30000")
    appnum = 0
    for app_id in app_ids:
        appnum += 1
        print('crawling :',app_id, appnum, thread_index)
        
        #get comment to memory
        records = []
        for name, date, likes_amount, comment_text, index in getcomment(driver, 'https://play.google.com/store/apps/details?id=' + app_id + '&showAllReviews=true',thread_index, sleeptime=1.5, max_comment=1400):
            records.append((app_id, comment_text, likes_amount, name, date, index))
        
        #push in db
        con.execute('BEGIN')
        for app_id, comment_text, likes_amount, name, date, index in records:
            con.execute('insert into app_comments (app_id,comment_text,likes_amount,commentor_name,date,comment_index) values( ?, ?, ?, ?, ?, ?)'
                    , (app_id, comment_text, likes_amount, name, date, index ,))
        con.execute('insert into app_comments_finish (app_id, finish) values (?, ?)', (app_id, 1,))
        con.execute('COMMIT')
    print('finished', thread_index)

datas = split(app_ids, 4)
for i,x in enumerate(datas):
    threading._start_new_thread(crawlcomment, (x,i))
while True:
    sleep(5)


    

        

    
