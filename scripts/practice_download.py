import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
start_date = "2006-01-01"
end_date = "2018-01-01"
frames = []

for ticker in tickers:
    prices = yf.download(
        ticker,
        start = start_date,
        end = end_date,
        auto_adjust = False,
        progress = False,
        multi_level_index = False,
    )
    prices.insert(0, "Ticker", ticker)
    frames.append(prices)

all_prices = pd.concat(frames)
print("Sum of missing values:\n", all_prices.isna().sum())
all_prices.to_csv("data/raw/india_testing_sample.csv")
print(all_prices.shape)
print(all_prices.describe())
print("Rows with zero volume:")

print(all_prices[all_prices["Volume"] == 0])
trading_prices = all_prices[all_prices["Volume"] > 0].copy()

trading_prices.to_csv("data/processed/india_testing_sample_trading.csv")
print(trading_prices.groupby("Ticker").size())

#creating 32 X 32 windows for each stock
reliance_data = trading_prices[trading_prices["Ticker"] == 'RELIANCE.NS'].sort_index()
first_window = reliance_data.iloc[:32]

model_input = first_window[["Adj Close", "Volume"]]
print(model_input.head())
print("Input shape:", model_input.shape)
normalized_input = (
    (model_input - model_input.min())
    / (model_input.max() - model_input.min())
)
print(normalized_input.head())
print("Normalized input statistics:")
print(normalized_input.agg(["min", "max"]))

chart_image = np.zeros((32, 32), dtype=np.uint8)

for day in range(32):
    price_value = normalized_input["Adj Close"].iloc[day]
    price_row = int(round((1 - price_value) * 14))
    chart_image[price_row, day] = 1
    volume_value = normalized_input["Volume"].iloc[day]
    volume_row = 17 + int(round((1 - volume_value) * 14))
    chart_image[volume_row:, day] = 1

print("Middle rows filled:", int(chart_image[15:17, :].sum()))
print("Image shape:", chart_image.shape)
print("Filled pixels:", chart_image.sum())

print(first_window[["Close","Volume"]])
print(first_window.shape)
second_window = reliance_data.iloc[1:33]

plt.imshow(chart_image, cmap="gray_r", interpolation="nearest", aspect="auto")
plt.title("32-day price and volume image")
plt.xlabel("Trading day")
plt.ylabel("Image row")
plt.show()
