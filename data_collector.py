import pandas as pd
import time
from pytrends.request import TrendReq
import praw
from newsapi import NewsApiClient

class DataIngestionEngine:
    """
    Handles connections and data extraction from multiple APIs.
    Incorporates robustness mechanisms for rate limiting.
    """
    def __init__(self, reddit_client_id, reddit_secret, news_api_key):
        # Initialize Google Trends with exponential backoff strategy
        self.pytrends = TrendReq(hl='en-US', tz=360, retries=3, backoff_factor=0.2)
        
        # Initialize Reddit API via PRAW
        self.reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_secret,
            user_agent='TrendPulse_AI_Agent_v1.0'
        )
        
        # Initialize NewsAPI
        self.newsapi = NewsApiClient(api_key=news_api_key)

    def fetch_google_trends(self, keyword_list, geo_code=''):
        """Fetches 90-day historical search volume data."""
        try:
            # Build payload with target region (e.g., 'IN-TN' for Tamil Nadu)
            self.pytrends.build_payload(keyword_list, timeframe='today 3-m', geo=geo_code)
            df = self.pytrends.interest_over_time()
            if not df.empty and 'isPartial' in df.columns:
                df = df.drop(columns=['isPartial'])
            return df
        except Exception as e:
            print(f"PyTrends API Error: {e}")
            return pd.DataFrame()

    def fetch_reddit_discourse(self, subreddits, limit=100):
        """Scrapes top-level posts and calculates the controversy index."""
        data = []
        for sub in subreddits:
            try:
                subreddit = self.reddit.subreddit(sub)
                for submission in subreddit.hot(limit=limit):
                    # Calculate controversy: ratio of comments to upvotes
                    controversy = submission.num_comments / (submission.score + 1)
                    data.append({
                        'title': submission.title,
                        'score': submission.score,
                        'num_comments': submission.num_comments,
                        'controversy_index': controversy
                    })
            except Exception as e:
                print(f"Reddit API Error for r/{sub}: {e}")
        return pd.DataFrame(data)

    def fetch_news_volume(self, keyword):
        """Calculates media saturation over the last 30 days."""
        try:
            response = self.newsapi.get_everything(q=keyword, language='en', sort_by='publishedAt')
            return response.get('totalResults', 0)
        except Exception as e:
            print(f"NewsAPI Error: {e}")
            return 0
