# Cross-Market Stock Research Demo

A learning project inspired by Lee et al. (2019), *Global Stock Market Prediction Based on Stock Chart Images Using Deep Q-Network*.

## Research question

When a model is trained on U.S. daily price-and-volume data and evaluated on Indian stocks, do chart-image inputs perform differently from numeric price-and-volume inputs after transaction-cost assumptions?

The web demo will also show a small Indian-stock watchlist using Yahoo Finance data. Quote freshness will be timestamped and labeled. Live market quotes and the research model's daily predictions are separate features; the initial model will not make intraday predictions.

## Current status

- [x] Project scope and initial Python environment files
- [x] Configurable daily price-data downloader
- [ ] Freeze the training and test universes and date ranges
- [ ] Inspect data quality and document missing-data handling
- [ ] Build chart-image and numeric model inputs
- [ ] Train and evaluate models against simple baselines
- [ ] Build the research and quote dashboard

## Setup

Use Python 3.11 or newer. From this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Download daily data

Download U.S. training data (example):

```powershell
python scripts/download_prices.py --market us --tickers AAPL,MSFT,AMZN --start 2001-01-01 --end 2006-01-01
```

Download Indian evaluation data (example):

```powershell
python scripts/download_prices.py --market india --tickers RELIANCE.NS,TCS.NS,INFY.NS --start 2006-01-01 --end 2018-01-01
```

The end date is exclusive. Each run saves a combined CSV under `data/raw/`. The example symbols are only a smoke-test universe; we still need to settle the research universe and date split before treating results as final.

Yahoo Finance access through `yfinance` is intended here as a convenient research/demo data source. The downloader records when data was fetched. It does not claim that quote updates are guaranteed to be real-time or licensed for public redistribution.

## Research reference

Lee, J., Kim, R., Koh, Y., and Kang, J. (2019). “Global Stock Market Prediction Based on Stock Chart Images Using Deep Q-Network.” *IEEE Access*, 7, 167260–167277. https://doi.org/10.1109/ACCESS.2019.2953542

