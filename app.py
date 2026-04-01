from fastapi import FastAPI
from typing import List
from data.data_fetch import process_stock 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Sample companies list
COMPANIES = ["INFY.NS", "TCS.NS", "RELIANCE.NS"]

#  Get all companies
@app.get("/companies")
def get_companies():
    return {"companies": COMPANIES}


#  Get last 30 days stock data
@app.get("/data/{symbol}")
def get_stock_data(symbol: str):
    df = process_stock(symbol)

    # Last 30 days
    df = df.tail(30)

    return df.to_dict(orient="records")


# Get summary (52W high, low, avg close)
@app.get("/summary/{symbol}")
def get_summary(symbol: str):
    df = process_stock(symbol)

    summary = {
        "symbol": symbol,
        "52W High": float(df["52W High"].max()),
        "52W Low": float(df["52W Low"].min()),
        "Average Close": float(df["Close"].mean())
    }

    return summary


# Compare two stocks
@app.get("/compare")
def compare_stocks(symbol1: str, symbol2: str):
    df1 = process_stock(symbol1)
    df2 = process_stock(symbol2)

    return {
        symbol1: {
            "avg_close": float(df1["Close"].mean()),
            "latest_price": float(df1["Close"].iloc[-1])
        },
        symbol2: {
            "avg_close": float(df2["Close"].mean()),
            "latest_price": float(df2["Close"].iloc[-1])
        }
    }