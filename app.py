import streamlit as st
import requests
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("RAPIDAPI_KEY")

st.set_page_config(page_title="Portfolio Risk Analyzer", layout="wide")

st.title("AI-Powered Portfolio Risk Analyzer")

# User input for stock search
search_query = st.text_input("Enter stock names (e.g., Tesla, Apple):")
suggestions = []

if search_query:
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/auto-complete"
    querystring = {"q": search_query, "region": "US"}
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        suggestions = [item["symbol"] + " - " + item["shortname"] for item in data["quotes"] if "symbol" in item]

selected_suggestions = st.multiselect("Select assets from suggestions:", suggestions)

tickers = [s.split(" - ")[0] for s in selected_suggestions]

# Custom date range
start_date = st.date_input("Start Date", value=datetime.date(2020, 1, 1))
end_date = st.date_input("End Date", value=datetime.date.today())

# Custom weights
use_custom_weights = st.checkbox("Use Custom Weights")
weights = []

if use_custom_weights and tickers:
    total_weight = 0
    for ticker in tickers:
        weight = st.number_input(f"Weight for {ticker} (as decimal)", min_value=0.0, max_value=1.0, step=0.01)
        weights.append(weight)
        total_weight += weight

    if total_weight != 1.0:
        st.warning("Total weights must sum to 1.")
else:
    weights = [1 / len(tickers)] * len(tickers) if tickers else []

# Fetch historical data
def fetch_data(symbol):
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v3/get-historical-data"
    querystring = {"symbol": symbol, "region": "US"}
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json().get("prices", [])
        df = pd.DataFrame(data)
        df = df[df["type"] == "history"]
        df["date"] = pd.to_datetime(df["date"], unit="s")
        df.set_index("date", inplace=True)
        df = df[["close"]]
        df.rename(columns={"close": symbol}, inplace=True)
        df = df.loc[(df.index >= pd.to_datetime(start_date)) & (df.index <= pd.to_datetime(end_date))]
        return df
    return pd.DataFrame()

# Process data
price_data = pd.DataFrame()
for ticker in tickers:
    df = fetch_data(ticker)
    if not df.empty:
        price_data = pd.concat([price_data, df], axis=1)

if not price_data.empty:
    # Portfolio returns
    daily_returns = price_data.pct_change().dropna()
    weighted_returns = (daily_returns * weights).sum(axis=1)
    portfolio_returns = (1 + weighted_returns).cumprod()

    # Risk Metrics
    volatility = weighted_returns.std()
    avg_daily_return = weighted_returns.mean()
    sharpe_ratio = avg_daily_return / volatility * np.sqrt(252)

    metrics = pd.DataFrame({
        "Metric": ["Volatility", "Average Daily Return", "Sharpe Ratio"],
        "Value": [round(volatility, 4), round(avg_daily_return, 4), round(sharpe_ratio, 4)]
    })

    st.subheader("Risk Metrics")
    st.dataframe(metrics.style.highlight_max(axis=0, color='lightgreen'))

    # Graph Options
    st.subheader("Portfolio Graphs")
    selected_graphs = st.multiselect(
        "Choose graphs to display:",
        ["Portfolio Trend", "Normalized Comparison", "Individual Asset Performance"],
        default=["Portfolio Trend"]
    )

    if "Portfolio Trend" in selected_graphs:
        st.plotly_chart(px.line(portfolio_returns, title="Portfolio Growth Over Time"))

    if "Normalized Comparison" in selected_graphs:
        normalized = price_data / price_data.iloc[0]
        st.plotly_chart(px.line(normalized, title="Normalized Asset Prices"))

    if "Individual Asset Performance" in selected_graphs:
        st.plotly_chart(px.line(daily_returns.cumsum(), title="Individual Asset Cumulative Returns"))

else:
    st.warning("No data to display. Please check ticker names or date range.")
