import requests
import openai
from googleapiclient.discovery import build
import time
import openai
from openai.error import RateLimitError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

### 📌 **Fetch Latest & Hottest News Articles**
def fetch_news(keyword):
    """Fetch top 5 latest and most relevant news articles based on a keyword."""
    date_from = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
    url = f'https://newsapi.org/v2/everything?q={keyword}&from={date_from}&sortBy=relevancy&language=en&pageSize=10&apiKey={NEWS_API_KEY}'
    
    response = requests.get(url).json()
    
    if response.get("status") != "ok":
        print("❌ Error fetching news:", response.get("message"))
        return []
    
    articles = response.get('articles', [])
    
    # **Sort by published date (newest first)**
    sorted_articles = sorted(
        articles, 
        key=lambda x: x.get("publishedAt", ""), 
        reverse=True
    )

    return [{'title': article['title'], 'url': article['url'], 'publishedAt': article['publishedAt']} 
            for article in sorted_articles[:5]]


### 📌 **Fetch Latest & Hottest YouTube Videos**
def fetch_youtube_videos(keyword):
    """Fetch top 5 latest and most relevant YouTube videos based on a keyword."""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    def get_videos(order):
        request = youtube.search().list(
            q=keyword,
            part="snippet",
            type="video",
            maxResults=10,  # Fetch more to sort properly
            order=order
        )
        response = request.execute()
        return [
            {
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                "publishedAt": item["snippet"]["publishedAt"]
            }
            for item in response.get("items", [])
        ]

    latest_videos = get_videos("date")  # Fetch latest videos
    popular_videos = get_videos("viewCount")  # Fetch most popular videos

    # **Merge & Deduplicate**
    combined_videos = {video["url"]: video for video in (latest_videos + popular_videos)}.values()

    # **Sort by Date (Newest First)**
    sorted_videos = sorted(combined_videos, key=lambda x: x["publishedAt"], reverse=True)

    return list(sorted_videos)[:5]

def summarize_articles(articles):
    """Summarize news articles using OpenAI API with retry logic."""
    summaries = []
    for article in articles:
        prompt = f"Summarize this news article: {article['title']} ({article['url']})"
        
        # Retry logic for rate limiting
        while True:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" if preferred
                    messages=[
                        {"role": "system", "content": "Provide a short summary of the news article."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150
                )
                summary = response['choices'][0]['message']['content'].strip()
                summaries.append({'title': article['title'], 'summary': summary, 'url': article['url']})
                break  # Exit the retry loop if the request is successful
            except RateLimitError:
                print("Rate limit reached. Retrying in 20 seconds...")
                time.sleep(20)  # Wait for 20 seconds before retrying
            except Exception as e:
                print(f"Error: {e}")
                break  # Exit on other errors

    return summaries

if __name__ == "__main__":
    keyword = input("Enter a keyword to search for news and videos: ")

    print("\nFetching top news articles...")
    top_news = fetch_news(keyword)
    for idx, article in enumerate(top_news, 1):
        print(f"{idx}. {article['title']} ({article['url']})")

    print("\nFetching top YouTube videos...")
    top_videos = fetch_youtube_videos(keyword)
    for idx, video in enumerate(top_videos, 1):
        print(f"{idx}. {video['title']} ({video['url']})")

    print("\nSummarizing related news articles...")
    summaries = summarize_articles(top_news)
    for idx, summary in enumerate(summaries, 1):
        print(f"\n{idx}. {summary['title']} ({summary['url']})")
        print(f"Summary: {summary['summary']}")