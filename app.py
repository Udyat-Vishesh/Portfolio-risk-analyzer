import streamlit as st
import requests
import pandas as pd
import numpy as np
import os
from datetime import date, timedelta
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Portfolio Risk Analyzer", layout="wide")

# --- API CONFIG ---
RAPIDAPI_API_KEY = os.getenv("RAPIDAPI_API_KEY")
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_API_KEY,
    "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
}

SEARCH_URL = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/auto-complete"
PRICE_URL = "https://yh-finance.p.rapidapi.com/stock/v3/get-historical-data"

# --- FUNCTIONS ---

def search_stocks(query):
    if not query:
        return []
    try:
        response = requests.get(SEARCH_URL, headers=HEADERS, params={"q": query, "region": "US"})
        data = response.json()
        suggestions = [
            f"{item['symbol']} | {item.get('shortname', item.get('name', ''))}"
            for item in data.get("quotes", []) if "symbol" in item
        ]
        return suggestions
    except Exception:
        return []

def get_price_data(symbol, start_date, end_date):
    params = {
        "symbol": symbol,
        "region": "US"
    }
    try:
        response = requests.get(PRICE_URL, headers=HEADERS, params=params)
        data = response.json()
        prices = pd.DataFrame(data["prices"])
        prices["date"] = pd.to_datetime(prices["date"], unit='s')
        prices.set_index("date", inplace=True)
        prices = prices.sort_index()
        return prices.loc[start_date:end_date]["close"]
    except Exception:
        st.warning(f"Couldn't fetch data for {symbol}")
        return pd.Series()

def calculate_metrics(price_df, weights):
    returns = price_df.pct_change().dropna()
    weighted_returns = returns.dot(weights)
    expected_return = np.mean(weighted_returns) * 252
    volatility = np.std(weighted_returns) * np.sqrt(252)
    sharpe_ratio = expected_return / volatility if volatility != 0 else 0
    return expected_return, volatility, sharpe_ratio

# --- UI ---

st.title("Portfolio Risk Analyzer")

# --- Search with suggestions ---
query = st.text_input("Search for a stock/ETF/crypto:")
suggestions = search_stocks(query)
selected_asset = None
if suggestions:
    selected_asset = st.selectbox("Select from suggestions:", suggestions)
    if selected_asset:
        st.write(f"Selected: {selected_asset.split('|')[0].strip()}")

# --- Portfolio Selection ---
st.subheader("Build Your Portfolio")
tickers = st.multiselect("Add tickers (manually):", options=["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "NVDA", "META", "NIFTY"], default=["AAPL", "MSFT"])

# --- Date Range ---
st.subheader("Select Date Range")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=date.today() - timedelta(days=365))
with col2:
    end_date = st.date_input("End Date", value=date.today())

# --- Custom Weights ---
weights = []
if tickers:
    st.subheader("Assign Weights to Each Asset")
    for ticker in tickers:
        weight = st.number_input(f"Weight for {ticker} (in %)", min_value=0.0, max_value=100.0, value=round(100/len(tickers), 2))
        weights.append(weight)
    total_weight = sum(weights)
    if total_weight != 100:
        st.warning("Total weights should sum up to 100%.")
    weights = [w/100 for w in weights]  # normalize

# --- Risk Analysis ---
if st.button("Analyze Portfolio") and tickers:
    price_data = pd.DataFrame()
    for ticker in tickers:
        price_data[ticker] = get_price_data(ticker, start_date, end_date)

    if not price_data.empty and len(weights) == len(tickers):
        expected_return, volatility, sharpe_ratio = calculate_metrics(price_data, weights)
        st.subheader("Portfolio Metrics:")
        st.write(f"**Expected Annual Return:** {expected_return*100:.2f}%")
        st.write(f"**Annual Volatility (Risk):** {volatility*100:.2f}%")
        st.write(f"**Sharpe Ratio:** {sharpe_ratio:.2f}")

        st.subheader("Price Chart")
        st.line_chart(price_data)

        st.subheader("Individual Asset Performance")
        normalized = price_data / price_data.iloc[0]
        st.line_chart(normalized)

