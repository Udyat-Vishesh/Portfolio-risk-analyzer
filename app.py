import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import datetime

st.set_page_config(page_title="AI Portfolio Risk Analyzer", layout="wide")

st.title("AI-Based Portfolio Risk Analyzer")
st.write("Analyze and visualize risk-return metrics for your custom portfolio.")

# Get API Key from Streamlit secrets
api_key = st.secrets["RAPIDAPI"]["API_KEY"]
host = "yahoo-finance15.p.rapidapi.com"

# Custom date range
start_date = st.date_input("Start Date", datetime.date(2023, 1, 1))
end_date = st.date_input("End Date", datetime.date.today())

# Stock input with multi-select
tickers = st.text_input("Enter stock/ETF/crypto names (comma separated)", value="AAPL,MSFT,TSLA").upper()
ticker_list = [ticker.strip() for ticker in tickers.split(",") if ticker.strip()]

# Function to fetch historical data
def fetch_data(ticker):
    url = f"https://yahoo-finance15.p.rapidapi.com/api/yahoo/hi/history/{ticker}/1d"

    querystring = {"from": str(start_date), "to": str(end_date)}

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": host
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        try:
            data = response.json()["items"]
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index("date", inplace=True)
            df["returns"] = df["close"].pct_change()
            return df
        except Exception as e:
            st.error(f"Error parsing data for {ticker}: {e}")
            return None
    else:
        st.warning(f"Failed to retrieve data for {ticker}")
        return None

# Process portfolio
if ticker_list:
    portfolio_data = {}
    for ticker in ticker_list:
        df = fetch_data(ticker)
        if df is not None:
            portfolio_data[ticker] = df

    if portfolio_data:
        st.subheader("Risk and Return Summary")
        metrics = []
        for ticker, df in portfolio_data.items():
            mean_return = df["returns"].mean()
            volatility = df["returns"].std()
            metrics.append({
                "Ticker": ticker,
                "Annual Return (%)": round(mean_return * 252 * 100, 2),
                "Annual Risk (Volatility %)": round(volatility * (252 ** 0.5) * 100, 2)
            })
        st.dataframe(pd.DataFrame(metrics))

        # Plot Performance
        perf_df = pd.DataFrame()
        for ticker, df in portfolio_data.items():
            df["cum_return"] = (1 + df["returns"]).cumprod()
            perf_df[ticker] = df["cum_return"]
        st.plotly_chart(px.line(perf_df, title="Cumulative Returns Over Time"), use_container_width=True)

    else:
        st.info("No valid data found. Please check ticker names and date range.")
else:
    st.info("Enter tickers to begin analysis.")
