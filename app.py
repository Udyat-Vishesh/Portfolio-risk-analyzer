# app.py
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# Set layout
st.set_page_config(layout="wide", page_title="Portfolio Risk Analyzer")
st.title("AI-Based Portfolio Risk Analyzer")

# Ticker input
user_input = st.text_input("Enter tickers (comma-separated, e.g., AAPL, TSLA, BTC-USD, ^NSEI):")
selected_tickers = [ticker.strip().upper() for ticker in user_input.split(",") if ticker.strip()]

# Time period selection
time_period = st.selectbox("Select Time Period", ['1 Week', '6 Months', '1 Year'])
period_days = {'1 Week': 7, '6 Months': 182, '1 Year': 365}
days = period_days[time_period]

# Custom Weights Option
use_custom_weights = st.checkbox("Use Custom Weights")
custom_weights = []
if use_custom_weights and selected_tickers:
    for ticker in selected_tickers:
        weight = st.number_input(f"Weight for {ticker}", min_value=0.0, max_value=1.0, step=0.01)
        custom_weights.append(weight)
    total_weight = sum(custom_weights)
    if total_weight != 1.0:
        st.warning("Total weight must be exactly 1.0")

# Fetch and process data
@st.cache_data
def fetch_data(tickers, days):
    data = yf.download(tickers, period=f"{days}d")['Close']
    returns = data.pct_change().dropna()
    return data, returns

if selected_tickers and (not use_custom_weights or sum(custom_weights) == 1.0):
    data, returns = fetch_data(selected_tickers, days)

    # Portfolio returns
    if use_custom_weights:
        weights = np.array(custom_weights)
    else:
        weights = np.ones(len(selected_tickers)) / len(selected_tickers)

    portfolio_returns = (returns * weights).sum(axis=1)

    # Risk metrics
    def risk_metrics(returns):
        volatility = returns.std()
        sharpe_ratio = returns.mean() / volatility
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        max_drawdown = drawdown.min()
        return volatility, sharpe_ratio, max_drawdown, cumulative

    vol, sharpe, max_dd, cumulative_returns = risk_metrics(portfolio_returns)

    # Show metrics
    st.subheader("Risk Metrics")
    st.metric("Volatility (Std Dev)", f"{vol:.2%}")
    st.metric("Sharpe Ratio", f"{sharpe:.2f}")
    st.metric("Max Drawdown", f"{max_dd:.2%}")

    # Graph selection
    graph_options = ["Cumulative Returns", "Daily Returns", "Drawdown", "Asset Prices"]
    selected_graphs = st.multiselect("Select Graphs to Display (up to 3)", graph_options, default=["Cumulative Returns"])

    if "Cumulative Returns" in selected_graphs:
        st.subheader("Cumulative Portfolio Return")
        st.line_chart(cumulative_returns)

    if "Daily Returns" in selected_graphs:
        st.subheader("Daily Portfolio Returns")
        st.line_chart(portfolio_returns)

    if "Drawdown" in selected_graphs:
        drawdown = (1 + portfolio_returns).cumprod()
        peak = drawdown.cummax()
        drawdown_series = (drawdown - peak) / peak
        st.subheader("Drawdown")
        st.line_chart(drawdown_series)

    if "Asset Prices" in selected_graphs:
        st.subheader("Asset Price Movement")
        st.line_chart(data)

# Note: Later add AI analysis module when user triggers it (to be added on request)
