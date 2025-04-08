from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_API_KEY")
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "yh-finance.p.rapidapi.com"
}

def fetch_price_data(symbol, start_date, end_date):
    url = "https://yh-finance.p.rapidapi.com/stock/v3/get-historical-data"
    params = {"symbol": symbol}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        df = pd.DataFrame(data.get("prices", []))
        df["date"] = pd.to_datetime(df["date"], unit="s")
        df = df[["date", "close"]].dropna()
        df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
        df.set_index("date", inplace=True)
        return df.rename(columns={"close": symbol})
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame()

@app.route("/analyze", methods=["POST"])
def analyze_portfolio():
    try:
        data = request.get_json()
        tickers = data["tickers"]
        weights = data["weights"]
        start = data["start_date"]
        end = data["end_date"]

        price_data = pd.DataFrame()
        for t in tickers:
            df = fetch_price_data(t, start, end)
            if not df.empty:
                price_data = pd.concat([price_data, df], axis=1)

        if price_data.empty:
            return jsonify({"error": "No valid data found."}), 400

        daily_returns = price_data.pct_change().dropna()
        weights = np.array(weights)

        expected_return = np.dot(daily_returns.mean(), weights) * 252
        volatility = np.sqrt(np.dot(weights, np.dot(daily_returns.cov() * 252, weights)))
        sharpe_ratio = expected_return / volatility if volatility else 0

        cumulative = (1 + daily_returns).cumprod().reset_index().to_dict(orient="list")
        correlation = daily_returns.corr().values.tolist()

        return jsonify({
            "expected_return": expected_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "cumulative_returns": cumulative,
            "correlation_matrix": correlation,
            "tickers": tickers
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Flask Portfolio Risk Analyzer is running!"

if __name__ == "__main__":
    app.run(debug=True)

