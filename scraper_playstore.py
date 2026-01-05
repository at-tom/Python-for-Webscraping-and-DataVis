from google_play_scraper import reviews, Sort
import csv

app_id = "com.spotify.music"  # Spotify su Play Store

# Ottieni fino a 500 recensioni
result, _ = reviews(
    app_id,
    lang='en',       # lingua
    country='us',    # paese
    sort=Sort.NEWEST,
    count=500
)

with open("spotify_playstore_reviews.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["userName", "score", "at", "content", "replyContent", "thumbsUpCount", "version"])
    for r in result:
        writer.writerow([
            r["userName"],
            r["score"],
            r["content"].replace("\n", " "),
            r.get("at"),
            r.get("appVersion", ""),
            (r.get("replyContent") or "").replace("\n", " "),
        ])


print(f"✅ Salvate {len(result)} recensioni in spotify_playstore_reviews.csv")
