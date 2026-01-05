#!/usr/bin/env python3
# reddit_audiophile_scraper.py

import requests
import csv
import time
import re
from datetime import datetime

# ---------- CONFIG ----------
#SUBREDDIT = "audiophile"
POST_LIMIT = 100     # Numero massimo di post
TOP_COMMENTS = 300   # Numero massimo di commenti per post
DELAY = 1.2          # Pausa tra le richieste
USER_AGENT = "Mozilla/5.0 (script: reddit_scraper) Python/requests"
# ----------------------------

headers = {"User-Agent": USER_AGENT}
url_feed = "https://www.reddit.com/search.json?q=spotify+audio+quality&limit=100"

def safe_get_json(url):
    """Scarica un JSON da Reddit con gestione errori"""
    try:
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            print(f"HTTP {r.status_code} su {url}")
            return None
        return r.json()
    except Exception as e:
        print(f"Errore request {e} su {url}")
        return None

def extract_urls(text):
    """Estrae tutti gli URL dal testo"""
    if not text:
        return []
    return re.findall(r'https?://[^\s)>\]]+', text)

def scrape_posts():
    """Scarica i post principali dal subreddit"""
    data = safe_get_json(url_feed)
    if not data:
        return []
    posts = []
    for item in data.get("data", {}).get("children", []):
        p = item.get("data", {})
        post = {
            "id": p.get("id"),
            "title": p.get("title", ""),
            "author": p.get("author", ""),
            "flair": p.get("link_flair_text", ""),
            "score": p.get("score", 0),
            "num_comments": p.get("num_comments", 0),
            "created": datetime.utcfromtimestamp(p.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M"),
            "url": "https://www.reddit.com" + p.get("permalink", ""),
            "domain": p.get("domain", ""),
            "selftext": p.get("selftext", ""),
            "links_in_post": ";".join(extract_urls(p.get("selftext", "")))
        }
        posts.append(post)
    return posts

def scrape_comments(permalink):
    """Scarica i commenti per un singolo post"""
    url = f"https://www.reddit.com{permalink}.json?limit=500"
    data = safe_get_json(url)
    time.sleep(DELAY)
    if not data or len(data) < 2:
        return []
    comments_data = data[1].get("data", {}).get("children", [])
    comments = []
    for c in comments_data:
        if c.get("kind") != "t1":
            continue
        d = c.get("data", {})
        comments.append({
            "comment_id": d.get("id"),
            "comment_author": d.get("author", "[deleted]"),
            "comment_score": d.get("score", 0),
            "comment_created": datetime.utcfromtimestamp(d.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M"),
            "comment_body": d.get("body", ""),
            "comment_links": ";".join(extract_urls(d.get("body", "")))
        })
    return comments[:TOP_COMMENTS]

def main():
    print("🔍 Scarico i top post da r/audiophile ...")
    posts = scrape_posts()
    print(f"✅ Trovati {len(posts)} post.")

    all_rows = []

    for p in posts:
        print(f"\n🎵 Post: {p['title'][:60]}...")
        permalink = p["url"].replace("https://www.reddit.com", "")
        comments = scrape_comments(permalink)
        print(f"   ↳ {len(comments)} commenti trovati")

        if comments:
            for c in comments:
                row = {**p, **c}
                all_rows.append(row)
        else:
            # se non ci sono commenti, salvi comunque il post
            all_rows.append({**p, **{
                "comment_id": "",
                "comment_author": "",
                "comment_score": "",
                "comment_created": "",
                "comment_body": "",
                "comment_links": ""
            }})

    # ---------- SALVA IN CSV ----------
    filename = "reddit_audiophile.csv"
    keys = list(all_rows[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\n💾 Salvati {len(all_rows)} record in {filename}")

if __name__ == "__main__":
    main()
