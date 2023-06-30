
from bs4 import BeautifulSoup
import requests
import sqlite3
import re
import os

"""
GOOGLE SEARCH RESULTS SCRAPER

|Database structure|

--------------------------------------------------

Tables

keywords
id | keyword | pop_score

SearchResults
id | keyword_id | url_id | rank 

urls
id | url | title

"""

def open_db(db):
    path = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.dirname(__file__) #<-- directory name
    full_path = os.path.join(source_dir, db)
    conn = sqlite3.connect(full_path)
    cur = conn.cursor()
    return conn, cur

def creat_table_keywords(conn, cur):
    val1 = cur.execute("DROP TABLE IF EXISTS keywords")
    val = cur.execute(
        "CREATE TABLE IF NOT EXISTS keywords (id INTEGER PRIMARY KEY, keyword TEXT, pop_score INTEGER)"
    )
    conn.commit()
    
    keywords = ["Miami biobank", "Biobank analyzation process", "Importance of biobanks", "Types of Biobanks", "Genetic Research", "Biobank security", "Hispanic representation in Genetic Research", "Risks of DNA sampling", "Genebanks", "DNA sample storage"]
    count  = 1
    for i in keywords:
        val2 = cur.execute(
            "INSERT OR IGNORE INTO keywords (id, keyword, pop_score) VALUES (?, ?, ?)",(count, i, 0)
        )
        count += 1 
    conn.commit()
    
def creat_table_urls(conn, cur):
    val1 = cur.execute("DROP TABLE IF EXISTS urls")
    val = cur.execute(
        "CREATE TABLE IF NOT EXISTS urls (id INTEGER, url TEXT PRIMARY KEY)"
    )
    conn.commit()

def creat_table_SearchResults(conn, cur):
    val1 = cur.execute("DROP TABLE IF EXISTS SearchResults")
    val = cur.execute(
        "CREATE TABLE IF NOT EXISTS SearchResults (id INTEGER PRIMARY KEY, rank INTEGER, keyword_id INTEGER, url_id INTEGER)"
    )
    conn.commit()

def get_rankings(conn, cur):
    cur.execute(
        "SELECT id, keyword FROM keywords"
    )
    words = cur.fetchall()
    for item in words: 
        cur.execute(
            "SELECT COUNT(*) From urls"
        )
        url_id = cur.fetchall()[0][0]
        cur.execute(
                "SELECT COUNT(*) From SearchResults"
        )
        SERP_id = cur.fetchall()[0][0]
        count = 0
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        URL = 'https://www.google.com/search?q=' + item[1]+ '&near=miami'
        response = requests.get('https://www.google.com/search?q=' + item[1]+ '&near=miami', headers=header)
        soup = BeautifulSoup(response.text, "lxml")
        #, {'class': 'yuRUbf'}
        links = soup.find_all(name = 'div', class_ = "yuRUbf")
        word_rank_temp = soup.find('div', {'id': "result-stats"}).text
        word_rank = re.search('(?<=About\s).+(?=\sresults)', word_rank_temp)[0]
        word_rank = int(word_rank.replace(',', ''))
        cur.execute(
            "UPDATE keywords SET pop_score = ? WHERE keyword = ?", (word_rank, item[1], )
        )
        conn.commit()
        for link in links:
            #title_tag = link.find(name="h3", class_="LC20lb MBeuO DKV0Md")
            #article_title = title_tag.getText()
            link_tag = link.select_one("div a") #the function we focus on
            lynk = link_tag.get('href')
            
            cur.execute(
                "INSERT OR IGNORE INTO urls (id, url) VALUES (?, ?)", (url_id + count, lynk)
            )
            conn.commit()
            cur.execute(
                "SELECT id FROM urls WHERE url = ?", (lynk, )
            )
            url_table_id = cur.fetchall()[0][0]
            cur.execute(
                "INSERT OR IGNORE INTO SearchResults (id, rank, keyword_id, url_id) VALUES (?, ?, ?, ?)", (SERP_id + count, count + 1, item[0], url_table_id)
            )
            conn.commit()
            count += 1 
        
    return 0


if __name__ == '__main__':
    print('running :) ...')
    conn, cur = open_db('Keywords.db')
    creat_table_keywords(conn, cur)
    creat_table_urls(conn, cur)
    creat_table_SearchResults(conn, cur)
    get_rankings(conn, cur)
