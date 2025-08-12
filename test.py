from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import ta  # technical analysis library
import time

client = Client()

def get_symbols():
    # Get all symbols that end in USDT (spot trading)
    info = client.get_exchange_info()
    return [
        s['symbol'] for s in info['symbols']
        if s['symbol'].endswith('USDT') and s['status'] == 'TRADING'
    ]

def get_klines(symbol, interval='1h', limit=100):
    try:
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'num_trades',
            'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
        ])
        df['close'] = pd.to_numeric(df['close'])
        df['volume'] = pd.to_numeric(df['volume'])
        return df
    except BinanceAPIException as e:
        print(f"[Error] {symbol}: {e}")
        return None

def analyze(symbol):
    df = get_klines(symbol)
    if df is None or df.empty:
        return None

    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd_diff()  # Histogram
    df['macd_line'] = macd.macd()  # DIF
    df['macd_signal'] = macd.macd_signal()  # DEA
    df['ema20'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()

    latest = df.iloc[-1]
    # Strategy logic
    if (
        latest['rsi'] < 30 and
        latest['macd'] > 0 and
        latest['macd_line'] > latest['macd_signal']
    ):
        return {
            'symbol': symbol,
            'rsi': latest['rsi'],
            'macd': latest['macd'],
            'dif': latest['macd_line'],
            'dea': latest['macd_signal'],
            'close': latest['close'],
        }
    return None

def main():
    symbols = get_symbols()
    print(f"Checking {len(symbols)} symbols...\n")
    results = []

    for symbol in symbols:
        if not symbol.endswith('USDT'):
            continue
        time.sleep(0.1)  # avoid hitting API rate limit
        result = analyze(symbol)
        if result:
            results.append(result)

    print("\n🟢 Potential Buys Today:")
    for r in results:
        print(f"{r['symbol']} | RSI: {r['rsi']:.2f} | MACD: {r['macd']:.4f} | DIF: {r['dif']:.4f} | DEA: {r['dea']:.4f}")

if __name__ == "__main__":
    main()
