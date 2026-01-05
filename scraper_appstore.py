import requests
import csv

app_id = "324684580"  # Spotify
base_url = f"https://itunes.apple.com/us/rss/customerreviews/id={app_id}/json"

all_reviews = []
page = 1

while len(all_reviews) < 50:
    url = f"{base_url}?page={page}"
    r = requests.get(url)
    data = r.json()
    entries = data.get("feed", {}).get("entry", [])[1:]  # primo entry è l'app
    if not entries:
        break  # niente più recensioni
    all_reviews.extend(entries)
    page += 1

# tieni solo le prime 50
all_reviews = all_reviews[:50]

with open("spotify_reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["author", "title", "review", "rating", "version", "date"])
    for entry in all_reviews:
        writer.writerow([
            entry["author"]["name"]["label"],
            entry["title"]["label"],
            entry["content"]["label"],
            entry["im:rating"]["label"],
            entry["im:version"]["label"],
            entry["updated"]["label"]
        ])

print(f"Salvate {len(all_reviews)} recensioni in spotify_reviews.csv")
