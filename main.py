from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from model_pipeline import TrendPredictionModel

# Initialize FastAPI application
app = FastAPI(
    title="TrendPulse AI API", 
    description="Predictive API for forecasting digital trend virality.",
    version="1.0.0"
)

# Instantiate the prediction pipeline
predictor = TrendPredictionModel()

class TrendResponse(BaseModel):
    topic: str
    trend_probability: float
    expected_growth: str
    status: str

@app.get("/predict_trend", response_model=TrendResponse)
async def get_trend_prediction(
    topic: str = Query(..., description="The keyword or topic to analyze"),
    geo: str = Query("World", description="ISO geographic code filter (e.g., US, IN-TN)")
):
    try:
        # In a production environment, this calls the DataIngestionEngine
        # For demonstration, we simulate the extracted feature array:
        # Features: [search_volume_sma, sentiment_score, controversy_index, news_volume]
        simulated_features = [150.5, 0.85, 1.2, 3400] 
        
        # Execute XGBoost inference
        probability = predictor.predict_trend_score(simulated_features)
        
        # Categorize growth tier based on probability thresholds
        growth_tier = "High 🔥" if probability > 0.75 else "Medium 📈" if probability > 0.4 else "Low 📉"
        
        return TrendResponse(
            topic=topic,
            trend_probability=float(round(probability, 3)),
            expected_growth=growth_tier,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
