import requests
import datetime
import streamlit as st

response = requests.get("https://api.binance.com/api/v3/exchangeInfo")
data = response.json()
number_of_pairs = len(data["symbols"])
pairs = data["symbols"]

# Filtering and counting the pairs based on the criteria
usdt_pairs = [pair for pair in pairs if pair["quoteAsset"] == "USDT"]
btc_pairs = [pair for pair in pairs if pair["quoteAsset"] == "BTC"]
eth_pairs = [pair for pair in pairs if pair["quoteAsset"] == "ETH"]
busd_pairs = [pair for pair in pairs if pair["quoteAsset"] == "BUSD"]

number_of_usdt_pairs = len(usdt_pairs)
number_of_btc_pairs = len(btc_pairs)
number_of_eth_pairs = len(eth_pairs)

number_of_usdt_pairs, number_of_btc_pairs, number_of_eth_pairs

non_btc_pairs = [pair["symbol"] for pair in pairs if pair["quoteAsset"] != "BTC"]
non_eth_pairs = [pair["symbol"] for pair in pairs if pair["quoteAsset"] != "ETH"]

print(f"There are {number_of_pairs} trading pairs available on Binance.")
print(f"There are {len(usdt_pairs)} trading pairs against USDT.")
print(f"There are {len(btc_pairs)} trading pairs against BTC.")
print(f"There are {len(eth_pairs)} trading pairs against ETH.")
print(f"There are {len(busd_pairs)} trading pairs against BUSD.")
print(non_btc_pairs)
print(non_eth_pairs)

non_btc_pairs = [pair["symbol"] for pair in pairs if pair["quoteAsset"] != "BTC"]
non_eth_pairs = [pair["symbol"] for pair in pairs if pair["quoteAsset"] != "ETH"]

selected_coin = st.sidebar.selectbox("Choose a base coin", options = ["USDT", "BTC", "ETH", "BUSD", "Not BTC", "Not ETH"])




