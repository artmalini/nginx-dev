import pandas as pd
import numpy as np
from indicators.libmath import linreg
import helpers as h

slope_price = None
slope_price_lt = None
slope_volume_up = None
slope_volume_down = None
slope_volume_up_lt = None
slope_volume_down_lt = None

# Calculate Buy/Sell Volume
def _rate(df, cond):
    try:
        # Get the size of top/bottom/body of the candle
        tw = df['high'] - np.maximum(df['open'], df['close'])
        bw = np.minimum(df['open'], df['close']) - df['low']
        body = np.abs(df['close'] - df['open'])

        ret = 0.5 * (tw + bw + (cond * 2 * body)) / (tw + bw + body)
        ret = np.where(np.isnan(ret), 0.5, ret)
        return ret
    except Exception as e:
        h.logger.warning(f"_rate {e}")

# Calculate Regression Slope for Buy/Sell Volumes
def _get_trend(df, len):
    try:
        deltaup = df['volume'] * _rate(df, df['open'] <= df['close'])
        deltadown = df['volume'] * _rate(df, df['open'] > df['close'])

        slope_volume_up = linreg(deltaup, len, 0) - linreg(deltaup, len, 1)
        slope_volume_down = linreg(deltadown, len, 0) - linreg(deltadown, len, 1)
        return slope_volume_up, slope_volume_down
    except Exception as e:
        h.logger.warning(f"_get_trend {e}")

def vslrt(df, trainedSource, dfSource, vslrtLen1, vslrtLen2):
    global slope_price
    global slope_price_lt
    global slope_volume_up
    global slope_volume_down
    global slope_volume_up_lt
    global slope_volume_down_lt

    long_signal = None
    short_signal = None
    vslrtSrc = df[dfSource]

    if trainedSource["vslrt"]["trained"] == True:
        slope_price = trainedSource["vslrt"]["slope_price"]
        slope_price_lt = trainedSource["vslrt"]["slope_price_lt"]
        slope_volume_up = trainedSource["vslrt"]["slope_volume_up"]
        slope_volume_down = trainedSource["vslrt"]["slope_volume_down"]
        slope_volume_up_lt = trainedSource["vslrt"]["slope_volume_up_lt"]
        slope_volume_down_lt = trainedSource["vslrt"]["slope_volume_down_lt"]
    try:
        # Get short/long-term regression slope
        slope_price = linreg(vslrtSrc, vslrtLen1, 0) - linreg(vslrtSrc, vslrtLen1, 1)
        slope_price_lt = linreg(vslrtSrc, vslrtLen2, 0) - linreg(vslrtSrc, vslrtLen2, 1)

        # Get buy/sell volume regression slopes for short term period
        slope_volume_up, slope_volume_down = _get_trend(df, vslrtLen1)
        # Get buy/sell volume regression slopes for long term period
        slope_volume_up_lt, slope_volume_down_lt = _get_trend(df, vslrtLen2)

        # h.logger.info(f"slope_volume_up_lt {slope_volume_up_lt}")
        long_signal = (slope_price > 0) & (slope_volume_up > 0) & (slope_volume_up > slope_volume_down) & (slope_price_lt > 0) & (slope_volume_up_lt > 0) & (slope_volume_up_lt > slope_volume_down_lt)
        short_signal = (slope_price < 0) & (slope_volume_down > 0) & (slope_volume_up < slope_volume_down) & (slope_price_lt < 0) & (slope_volume_down_lt > 0) & (slope_volume_up_lt < slope_volume_down_lt)
        
        if trainedSource["vslrt"]["trained"] == False:
            trainedSource["vslrt"]["trained"] = True
            trainedSource["vslrt"]["long_signal"] = long_signal
            trainedSource["vslrt"]["short_signal"] = short_signal
            trainedSource["vslrt"]["slope_price"] = slope_price
            trainedSource["vslrt"]["slope_price_lt"] = slope_price_lt
            trainedSource["vslrt"]["slope_volume_up"] = slope_volume_up
            trainedSource["vslrt"]["slope_volume_down"] = slope_volume_down
            trainedSource["vslrt"]["slope_volume_up_lt"] = slope_volume_up_lt
            trainedSource["vslrt"]["slope_volume_down_lt"] = slope_volume_down_lt

        return long_signal, short_signal, trainedSource
    except Exception as e:
        h.logger.warning(f"vslrt {e}")