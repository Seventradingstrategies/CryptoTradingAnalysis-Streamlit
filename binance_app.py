import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Function to fetch OHLCV data from Binance
def fetch_ohlcv_data(symbol, interval='1d', limit=1000, num_data_points=999):
    df_list = []
    last_timestamp = None
    progress = 0  # Initialize progress

    # Create a progress bar in Streamlit
    progress_bar = st.sidebar.progress(0)

    while num_data_points > 0:
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': min(limit, num_data_points)
        }

        if last_timestamp:
            params['endTime'] = last_timestamp

        response = requests.get('https://api.binance.com/api/v3/klines', params=params)
        data = response.json()
        df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)

        df_list.append(df)
        last_timestamp = df['open_time'].min()
        fetched_points = len(df)
        num_data_points -= fetched_points

        # Update the progress bar
        progress += fetched_points
        progress_bar.progress(progress / (progress + num_data_points))

    progress_bar.empty()
    final_df = pd.concat(df_list, axis=0)
    return final_df[['open_time', 'open', 'high', 'low', 'close', 'volume']].reset_index(drop=True)

response_spot = requests.get("https://api.binance.com/api/v3/exchangeInfo")

if response_spot.status_code == 200:
    data_spot = response_spot.json()
    if "symbols" in data_spot:
        pairs_spot = data_spot["symbols"]
        spot_symbols = [pair["symbol"] for pair in pairs_spot]
        # Continue with your existing logic...
    else:
        st.error("The 'symbols' key does not exist in the API response.")
else:
    st.error(f"Failed to get data from Binance API. Status code: {response_spot.status_code}")

# Sidebar options
selected_option = st.sidebar.selectbox(
    "Choose an option",
    options=["USDT", "BTC", "ETH", "BUSD"],
    key="option_select"
)

def filter_pairs(option):
    return [pair["symbol"] for pair in pairs_spot if pair["quoteAsset"] == option]

coin_pairs = filter_pairs(selected_option)

# Display the number of available pairs
st.title(f"Trading Pairs for {selected_option}")
st.subheader(f"Number of pairs: {len(coin_pairs)}")

# Fetch OHLCV data for the selected trading pair
if coin_pairs:
    selected_pair = st.sidebar.selectbox("Choose a trading pair for OHLCV", options=coin_pairs, key="ohlcv_pair_select")
    interval = st.sidebar.selectbox("Choose time interval", options=['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d'], key="interval_key")
    ohlcv_data = fetch_ohlcv_data(selected_pair, interval, num_data_points=999)  # or any other number you prefer

    # Calculate returns
    ohlcv_data['returns'] = ohlcv_data['close'].pct_change() * 100  # in percentage

    # Calculate cumulative returns
    ohlcv_data['cumulative_returns'] = ((1 + ohlcv_data['returns'] / 100).cumprod() - 1) * 100  # in percentage

    # Calculate returns
    ohlcv_data['volumes'] = ohlcv_data['volume'].pct_change() * 100  # in percentage

    # Calculate cumulative returns
    ohlcv_data['cumulative_volumes'] = ((1 + ohlcv_data['volumes'] / 100).cumprod() - 1) * 100  # in percentage

    # Calculate log returns
    ohlcv_data['log_returns'] = np.log(ohlcv_data['close'] / ohlcv_data['close'].shift(1)) * 100  # in percentage

    # Calculate mean return and volatility
    mean_return = ohlcv_data['returns'].mean()
    volatility = ohlcv_data['returns'].std()

    # Calculate standard deviation of returns
    std_return = ohlcv_data['returns'].std()
    ohlcv_data['std_return'] = std_return

    # Calculate standard deviation of absolute returns
    std_absolute_return = ohlcv_data['returns'].abs().std()
    ohlcv_data['std_absolute_return'] = std_absolute_return

    # Replace NaN values with 0
    ohlcv_data.fillna(0, inplace=True)

    # Display the OHLCV data with returns, cumulative returns, and log returns
    st.subheader(f"OHLCV Data with Returns for {selected_pair} ({interval})")
    st.write(ohlcv_data)

    # Display the mean return and volatility
    st.subheader(f"Mean Return and Volatility for {selected_pair} ({interval})")
    st.write(f"Mean Return: {mean_return:.2f}%")
    st.write(f"Volatility: {volatility:.2f}%")

    st.write(f"means it will deviate {volatility: .2f}% from the mean 1 SD away")

    # Calculate rolling mean return and rolling standard deviation for returns
    window_size = 20  # You can make this dynamic using Streamlit's sidebar if you like
    ohlcv_data['rolling_mean_return'] = ohlcv_data['returns'].rolling(window=window_size).mean()
    ohlcv_data['rolling_std_return'] = ohlcv_data['returns'].rolling(window=window_size).std()

    # Calculate Bollinger Bands for +1, +2, +3 SD
    for n in [1, 2, 3]:
        ohlcv_data[f'upper_band_{n}'] = ohlcv_data['rolling_mean_return'] + (ohlcv_data['rolling_std_return'] * n)
        ohlcv_data[f'lower_band_{n}'] = ohlcv_data['rolling_mean_return'] - (ohlcv_data['rolling_std_return'] * n)

    # Sidebar for rolling window size
    rolling_window = st.sidebar.slider('Select Rolling Window Size:', min_value=1, max_value=100, value=20)

    # Calculate rolling mean return and rolling volatility with a window of 20 (for example)
    ohlcv_data['rolling_mean_return'] = ohlcv_data['returns'].rolling(window=rolling_window).mean()
    ohlcv_data['rolling_volatility'] = ohlcv_data['returns'].rolling(window=rolling_window).std()

    # Plot rolling mean return and rolling volatility
    for metric in ['rolling_mean_return', 'rolling_volatility']:
        fig = go.Figure(data=[go.Scatter(x=ohlcv_data['open_time'], y=ohlcv_data[metric], mode='lines')])
        fig.update_layout(title=f'{metric.replace("_", " ").capitalize()} for {selected_pair} ({interval})',
                          xaxis_title='Time',
                          yaxis_title=metric.replace("_", " ").capitalize())
        st.plotly_chart(fig)

    # Display candlestick chart using Plotly
    fig = go.Figure(data=[go.Candlestick(x=ohlcv_data['open_time'],
                                         open=ohlcv_data['open'],
                                         high=ohlcv_data['high'],
                                         low=ohlcv_data['low'],
                                         close=ohlcv_data['close'])])
    fig.update_layout(title=f'Candlestick chart for {selected_pair} ({interval})',
                      xaxis_title='Time',
                      yaxis_title='Price',
                      xaxis_rangeslider_visible=False)
    st.plotly_chart(fig)

    # Display line charts for returns, cumulative returns, and log returns
    for metric in ['returns', 'cumulative_returns', 'log_returns', 'volumes', "cumulative_volumes"]:
        fig = go.Figure(data=[go.Scatter(x=ohlcv_data['open_time'], y=ohlcv_data[metric], mode='lines')])
        fig.update_layout(title=f'{metric.capitalize()} for {selected_pair} ({interval})',
                          xaxis_title='Time',
                          yaxis_title=metric.capitalize())
        st.plotly_chart(fig)

    # Add Bollinger Bands to the "RETURNS" plot
    fig = go.Figure()

    # Plot the returns
    fig.add_trace(go.Scatter(x=ohlcv_data['open_time'], y=ohlcv_data['returns'], mode='lines', name='Returns'))

    # Plot the Bollinger Bands
    for n in [1, 2, 3]:
        fig.add_trace(go.Scatter(x=ohlcv_data['open_time'], y=ohlcv_data[f'upper_band_{n}'], mode='lines',
                                 name=f'Upper Band +{n}SD'))
        fig.add_trace(go.Scatter(x=ohlcv_data['open_time'], y=ohlcv_data[f'lower_band_{n}'], mode='lines',
                                 name=f'Lower Band -{n}SD'))

    # Update layout for hovermode
    fig.update_layout(
        title=f'Returns and Bollinger Bands for {selected_pair} ({interval})',
        xaxis_title='Time',
        yaxis_title='Returns (%)',
        hovermode='x unified') # Show info for all traces at the closest X position

    st.plotly_chart(fig)
