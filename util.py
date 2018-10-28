from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import sqlite3

def getcomment(driver, url,thread_index, max_comment=200, sleeptime = 1.5):
    #download comment
    driver.get(url)
    try:
        clickSortByRating(driver, sleeptime)
    except:
        print('comment amount : 0', thread_index)
        return

    #get comment
    commentnum = 0
    while True:
        comment_elems = driver.find_elements_by_xpath("//div[@class='zc7KVe']")

        if commentnum == len(comment_elems):
            break
        else:
            commentnum = len(comment_elems)
        
        if len(comment_elems) >= max_comment :break
        else:
            scroll_simple(driver,thread_index, sleeptime)
            #view more button
            viewmore = driver.find_elements_by_css_selector('span.RveJvd.snByac')
            if len(viewmore) > 0:
                ActionChains(driver).move_to_element(viewmore[0]).click(viewmore[0]).perform()
                print('clicked view more')
                sleep(sleeptime)
                
    
    #click all full reviews
    for x in driver.find_elements_by_css_selector('.LkLjZd.ScJHi.OzU4dc'):
        x.send_keys(Keys.RETURN)
    print('comment amount :',len(comment_elems), thread_index)
    for i,x in enumerate(comment_elems):
        try:
            t= extract_comment_data(x, i)
            yield t
        except:
            continue

def clickSortByRating(driver, sleeptime):
    sortbybuttons = driver.find_elements_by_css_selector('content.vRMGwf.oJeWuf')

    #find sortbyrating button
    ActionChains(driver).move_to_element(sortbybuttons[-1]).click(sortbybuttons[-1]).perform()
    sleep(.3)
    sortbybuttons = driver.find_elements_by_css_selector('content.vRMGwf.oJeWuf')
    sortbyratingbut = [x for x in sortbybuttons if x.text == 'Rating'][0]
    #click sort by rating
    ActionChains(driver).move_to_element(sortbyratingbut).click(sortbyratingbut).perform()
    sleep(sleeptime)

def extract_comment_data(x, i):
    x = x.text.split('\n')
    name = x[0]
    date = x[1]
    likes_amount = x[3]
    if len(x) == 6:
        comment_text = x[5]
    #noone hit like
    else:
        likes_amount = 0
        comment_text = x[4]
    return name, date, likes_amount, comment_text, i

def scroll_page(driver, sleeptime=1.5, scrolltimes = 9999):
    oldheight = 0
    scrolltimes_i = 0
    while True and scrolltimes_i <= scrolltimes:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        scrolltimes_i += 1
        sleep(sleeptime)
        height = driver.execute_script("return document.body.scrollHeight")
        if oldheight == height:
            break
        else:
            oldheight = height
            print('scrolled')

def scroll_simple(driver, thread_index , sleeptime=1.5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    sleep(sleeptime)
    print('scrolled', thread_index)

def load_datasets_from_db():
    data_dir = r'E:/datasets/'
    db_path =  data_dir + 'app_datas.db'
    con = None
    try:
        con = sqlite3.connect(db_path)
    except:
        con = sqlite3.connect('app_datas.db')
    datas = con.execute('''
    select app_id from app_datas where app_id not in (select distinct(app_id) from app_comments_finish)
    ''')
    #TODO: filter 0 comment app
    output = [x[0] for x in datas]
    con.close()
    return output

def create_db():
    db_path =  'app_datas.db'
    con = sqlite3.connect(db_path)
    try:
        con.execute('''
        create table app_comments
        (app_id text,
        comment_text text,
        likes_amount int,
        commentor_name text,
        date text,
        comment_index int,
        foreign key (app_id) references app_datas(app_id)
        )
        ''')
    except:
        print('cant create db')
    try:
        con.execute('''
        create table app_comments_finish
        (app_id text,
        finish boolean,
        foreign key (app_id) references app_datas(app_id))
        ''')
    except:
        print('cant create db')
    con.commit()
    return con

def connect_db():
    data_dir = r'E:/datasets/'
    db_path = 'app_datas.db'
    con = sqlite3.connect(db_path) 
    return con

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))
