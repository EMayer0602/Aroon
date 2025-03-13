#Aroon_KI_GE1.py
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import locale
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

# Set German locale
try:
    locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
except:
    locale.setlocale(locale.LC_ALL, 'deu_deu')

# Get data
ticker = "BTC-EUR"
stock = yf.Ticker(ticker)
df = stock.history(period="1y")

# Calculate Aroon indicators (25-period)
def calculate_aroon(data, period=25):
    data = data.copy()
    data['Aroon Up'] = data['High'].rolling(period + 1).apply(lambda x: float(np.argmax(x)) / period * 100)
    data['Aroon Down'] = data['Low'].rolling(period + 1).apply(lambda x: float(np.argmin(x)) / period * 100)
    data['Aroon Oscillator'] = data['Aroon Up'] - data['Aroon Down']
    return data

# Apply calculation
df = calculate_aroon(df)

# Create subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
date_fmt = DateFormatter('%d.%m.%Y')

# Plot 1: Price
ax1.plot(df.index, df['Close'], label='Kurs', color='black')
ax1.set_title(f'{ticker} Kursverlauf')
ax1.legend()
ax1.grid(True)
ax1.xaxis.set_major_formatter(date_fmt)

# Plot 2: Aroon Indicators
ax2.plot(df.index, df['Aroon Up'], label='Aroon Aufwärts', color='green')
ax2.plot(df.index, df['Aroon Down'], label='Aroon Abwärts', color='red')
ax2.axhline(y=70, color='gray', linestyle='--')
ax2.axhline(y=30, color='gray', linestyle='--')
ax2.set_title('Aroon Indikatoren')
ax2.legend()
ax2.grid(True)
ax2.xaxis.set_major_formatter(date_fmt)

plt.setp(ax1.get_xticklabels(), rotation=45)
plt.setp(ax2.get_xticklabels(), rotation=45)
plt.tight_layout()
plt.show()

# Generate trading signals with long and short trades
signals = pd.DataFrame(index=df.index)
signals['Signal'] = 'Halten'
signals['Position'] = None
signals['Kurs'] = df['Close']

# Long trades
signals.loc[(df['Aroon Up'] > 70) & (df['Aroon Down'] < 30), 'Signal'] = 'Kaufen'
signals.loc[(df['Aroon Up'] < 30) & (df['Aroon Down'] > 70), 'Signal'] = 'Verkaufen'

# Short trades
signals.loc[(df['Aroon Down'] > 70) & (df['Aroon Up'] < 30), 'Signal'] = 'Leerverkauf'
signals.loc[(df['Aroon Up'] > 70) & (df['Aroon Down'] < 30), 'Signal'] = 'Deckung Leerverkauf'

# Filter only trading signals
trades = signals[signals['Signal'] != 'Halten'].copy()

# Calculate trade statistics
def calculate_trade_stats(trades_df):
    stats = {
        'Gesamtanzahl Trades': len(trades_df),
        'Long Trades': len(trades_df[trades_df['Signal'].isin(['Kaufen', 'Verkaufen'])]),
        'Short Trades': len(trades_df[trades_df['Signal'].isin(['Leerverkauf', 'Deckung Leerverkauf'])]),
    }
    
    # Calculate basic returns (simplified)
    trades_df['Kursänderung'] = trades_df['Kurs'].pct_change()
    stats['Durchschnittliche Kursänderung'] = trades_df['Kursänderung'].mean() * 100
    
    return pd.Series(stats)

# Format numbers for display
pd.options.display.float_format = lambda x: f'{x:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

# Print results
print("\nHandelssignale:")
print("=" * 50)
print(trades[['Signal', 'Kurs']].to_string())

print("\nHandelsstatistik:")
print("=" * 50)
stats = calculate_trade_stats(trades)
for key, value in stats.items():
    if isinstance(value, float):
        print(f"{key}: {value:.2f}%")
    else:
        print(f"{key}: {value}")

# Last 5 days of data
print("\nLetzten 5 Handelstage:")
print("=" * 50)
result_df = df[['Close', 'Aroon Up', 'Aroon Down', 'Aroon Oscillator']].tail()
result_df.columns = ['Schlusskurs', 'Aroon Aufwärts', 'Aroon Abwärts', 'Aroon Oszillator']
print(result_df)
