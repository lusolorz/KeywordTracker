import matplotlib.pyplot as plt
import sqlite3
import os
import re


"""
Calculations:

Keyword rankings:

Best performing urls:

rankings of urls per keyword:
(top for our specific need pages)

Regex to find the top domains over each keyword (top websites for our keywords)

Average of ranks for fomains is their relevance score 

"""

def open_db(db):
    path = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.dirname(__file__) #<-- directory name
    full_path = os.path.join(source_dir, db)
    conn = sqlite3.connect(full_path)
    cur = conn.cursor()
    return conn, cur

def keyword_rankings(conn, cur):
    cur.execute(
        "SELECT keyword, pop_score FROM keywords"
    )
    pop_scores = cur.fetchall()
    pop_scores_dict = {}
    total = 0
    for piece in pop_scores:
        total += piece[1]
    for piece in pop_scores:
        pop_scores_dict[piece[0]] = (piece[1]/total) * 100
    labels = list(pop_scores_dict.keys())
    sizes = list(pop_scores_dict.values())
    patches, texts = plt.pie(sizes, startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.axis('equal')
    plt.tight_layout()
    plt.show()
    plt.pie([x*100 for x in pop_scores_dict.values()],labels=[x for x in pop_scores_dict.keys()],autopct='%0.01f') 
    return 0

def competitor_site_urls(conn, cur):
    cur.execute(
        "SELECT SearchResults.keyword_id, SearchResults.rank, urls.url FROM SearchResults JOIN urls ON SearchResults.url_id = urls.id"
    )
    serps = cur.fetchall()
    ranks_dict = {}
    for item in serps:
        if item[0] in ranks_dict:
            ranks_dict[item[0]][item[1]] = item[2]
        else:
            ranks_dict[item[0]] = {}
            ranks_dict[item[0]][item[1]] = item[2]
    with open('ranked_urls.txt', 'a') as f:
        for item2 in ranks_dict.keys():
            cur.execute(
                "SELECT keyword FROM keywords WHERE id = ?", (item2, )
            )
            keeword = cur.fetchall()[0][0]
            f.write('\n\n\n' + keeword +  ": \n__________________________________________________________\n")
            f.write("Rank:   URL:\n")
            for item3 in ranks_dict[item2]:
                f.write(str(item3) + "       " + ranks_dict[item2][item3] + "\n")                         

    return 0

if __name__ == '__main__':
    conn, cur = open_db('Keywords.db')
    keyword_rankings(conn, cur)
    competitor_site_urls(conn, cur)