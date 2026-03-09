import pandas as pd
import numpy as np
from transformers import pipeline
from prophet import Prophet
import xgboost as xgb
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

class TrendPredictionModel:
    """
    Executes NLP sentiment analysis, topic modeling, and time-series forecasting.
    """
    def __init__(self):
        # Load Hugging Face DistilBERT for sequence classification
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english",
            truncation=True
        )
        
        # Initialize XGBoost classifier with tuned hyperparameters
        self.xgb_model = xgb.XGBClassifier(
            max_depth=4, 
            learning_rate=0.05, 
            n_estimators=150,
            subsample=0.8,
            objective='binary:logistic'
        )

    def analyze_sentiment(self, text_list):
        """Extracts sentiment and normalizes to a continuous metric scale."""
        if not text_list:
            return 0.0
            
        # Truncate list to prevent memory overflow during batch processing
        results = self.sentiment_analyzer(text_list[:200]) 
        # Convert labels to numeric polarity
        scores = [1 if res['label'] == 'POSITIVE' else -1 for res in results]
        return np.mean(scores)

    def extract_topics(self, text_list, n_topics=3):
        """Applies Latent Dirichlet Allocation (LDA) to discover latent themes."""
        vectorizer = CountVectorizer(stop_words='english', max_features=1000)
        dtm = vectorizer.fit_transform(text_list)
        
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda.fit(dtm)
        
        feature_names = vectorizer.get_feature_names_out()
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_words = [feature_names[i] for i in topic.argsort()[:-5 - 1:-1]]
            topics.append(", ".join(top_words))
        return topics

    def forecast_search_volume(self, trends_df):
        """Utilizes Facebook Prophet to forecast future search behavior."""
        if trends_df.empty:
            return pd.DataFrame()
            
        # Prepare DataFrame strictly to Prophet's required format
        df_prophet = trends_df.reset_index()
        df_prophet = df_prophet.rename(columns={df_prophet.columns[0]: 'ds', df_prophet.columns[1]: 'y'})
        
        model = Prophet(daily_seasonality=True, yearly_seasonality=False)
        model.fit(df_prophet)
        
        # Project 7 days into the future
        future = model.make_future_dataframe(periods=7)
        forecast = model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(7)

    def train_xgboost_scorer(self, feature_matrix, labels):
        """Fits the XGBoost ensemble model to output a virality probability."""
        self.xgb_model.fit(feature_matrix, labels)
        joblib.dump(self.xgb_model, 'trend_scorer.pkl')

    def predict_trend_score(self, current_features):
        """Generates a calibrated probability score  for impending virality."""
        try:
            model = joblib.load('trend_scorer.pkl')
            # Predict probability of the positive class (virality)
            probability = model.predict_proba([current_features])[0][1]
            return probability
        except FileNotFoundError:
            # Fallback heuristic if model is not yet trained
            return min(0.99, (current_features[0] * 0.001) + (current_features[1] * 0.2))
