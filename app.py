import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

# App title
st.set_page_config(page_title="Portfolio Risk Analyzer", layout="wide")
st.title("AI-Powered Portfolio Risk Analyzer")

# Function to fetch real-time ticker data from Yahoo Finance via RapidAPI
def search_tickers(query):
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/auto-complete"
    params = {"q": query, "region": "US"}
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()["quotes"]
        return [f"{item['symbol']} - {item['shortname']}" for item in results]
    else:
        return []

# Select stocks
st.subheader("Select Stocks/ETFs/Crypto")
user_input = st.text_input("Enter stock names (e.g., Tesla, Apple, Bitcoin)", "")
suggested = search_tickers(user_input) if user_input else []
selected_stocks = st.multiselect("Suggestions:", options=suggested, key="stock_select")

# Custom weights
use_custom_weights = st.checkbox("Use custom weights?")
weights = []
if use_custom_weights and selected_stocks:
    for stock in selected_stocks:
        weight = st.number_input(f"Weight for {stock} (%)", min_value=0.0, max_value=100.0, step=1.0)
        weights.append(weight / 100)
    if sum(weights) != 1.0:
        st.warning("The total of weights must be 100%.")

# Custom date range
st.subheader("Select Date Range")
start_date = st.date_input("Start Date", value=datetime(2023, 1, 1))
end_date = st.date_input("End Date", value=datetime.today())

# Risk Metrics Calculation (dummy placeholder, replace with real API calls)
def get_dummy_data(stocks, start, end):
    dates = pd.date_range(start=start, end=end, freq='B')
    data = {stock: (pd.Series(range(len(dates))) * 1.5).values for stock in stocks}
    return pd.DataFrame(data, index=dates)

if selected_stocks:
    # Extract tickers only
    tickers = [s.split(" - ")[0] for s in selected_stocks]
    df = get_dummy_data(tickers, start_date, end_date)
    st.subheader("Portfolio Data")
    st.dataframe(df)

    st.subheader("Risk Metrics")
    returns = df.pct_change().dropna()
    risk_metrics = {
        "Average Return (%)": returns.mean() * 100,
        "Volatility (%)": returns.std() * 100,
        "Sharpe Ratio": (returns.mean() / returns.std()).fillna(0)
    }
    metrics_df = pd.DataFrame(risk_metrics)
    st.dataframe(metrics_df.style.highlight_max(axis=0, color="lightgreen"))

    # Graph options
    st.subheader("Graphs")
    graph_options = ["Cumulative Returns", "Daily Returns", "Correlation Heatmap"]
    selected_graphs = st.multiselect("Choose graphs to display", graph_options)

    if "Cumulative Returns" in selected_graphs:
        cumulative = (1 + returns).cumprod()
        fig = px.line(cumulative, title="Cumulative Returns")
        st.plotly_chart(fig, use_container_width=True)

    if "Daily Returns" in selected_graphs:
        fig = px.line(returns, title="Daily Returns")
        st.plotly_chart(fig, use_container_width=True)

    if "Correlation Heatmap" in selected_graphs:
        corr = returns.corr()
        fig = px.imshow(corr, text_auto=True, title="Correlation Heatmap")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Please type a stock name to get suggestions and build a portfolio.")
