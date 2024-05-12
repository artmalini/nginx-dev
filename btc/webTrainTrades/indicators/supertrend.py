import pandas as pd
from indicators.libmath import l_pivothigh, l_pivotlow, l_nz
import math
import helpers as h

sum = [0] * 2
trueRange = [0]

def set_range_length(superPd):
    global trueRange
    trueRange = [0] * superPd

def m_sma(source, length):
    sma_values = []

    try:
        if source and length:
            for i in range(len(source)):
                sum_val = 0
                for j in range(length):
                    index = i - length + j + 1
                    if index >= 0:  # Ensure index is non-negative
                        value = source[index]
                        if not pd.isnull(value):  # Skip NaN values
                            sum_val += value / length
                sma_values.append(sum_val)

            return sma_values
    except Exception as e:
        h.logger.warning(f'supertrend sma {e}')
    return sma_values

def m_rma(src, length):
    global sum

    # h.logger.info(f'm_rma sma {m_sma(src, length)[0]}')
    try:
        alpha = 1 / length
        if sum[1] == 0:
            sum = [m_sma(src, length)[0]] + sum[:-1]
        else:
            sum = [alpha * src[0] + (1 - alpha) * sum[1]] + sum[:-1]

        # sum := na(sum[1]) ? ta.sma(src, length) : alpha * src + (1 - alpha) * nz(sum[1])
    
    except Exception as e:
         h.logger.warning(f'l_rma {e}')
    return sum

def l_atr(df, index, length):
    global trueRange

    # h.logger.info(f"trueRange {trueRange}")
    try:
        if not df.empty:
            # reset trueRange
            # set_range_length(length)
            if index == 0:
                trueRange = [df["high"].iloc[index] - df["low"].iloc[index]] + trueRange[:-1]
            elif not df["close"].iloc[index - 1]:
                trueRange = [df["high"].iloc[index] - df["low"].iloc[index]] + trueRange[:-1]
            else:
                trueRange = [max(max(df["high"].iloc[index] - df["low"].iloc[index], abs(df["high"].iloc[index]- df["close"].iloc[index - 1])), abs(df["low"].iloc[index] - df["close"].iloc[index - 1]))] + trueRange[:-1]
            result = m_rma(trueRange, length)

            return result[0]
    except Exception as e:
         h.logger.warning(f'l_atr {e}')
    return 1

def supertrend(df, superPrd, superFactor, superPd):
    long_signal = [False]
    short_signal = [False]
    super_coord_long = [None]
    super_coord_short = [None]
    try:
        if not df.empty:
            set_range_length(superPd)

            ph = l_pivothigh(df, superPrd, superPrd)
            pl = l_pivotlow(df, superPrd, superPrd)
            # h.logger.info(f"pivotHigh {ph}")
            # h.logger.info(f"pivotLow {pl}")
            
            center = [0,0]
            TUp = [0,0]
            TDown = [0,0]
            Trend = [1,1]
            for index in range(len(df)):
                if index > 0 :
                    lastpp = None
                    if ph[index] != None:
                        lastpp = ph[index]
                    elif pl[index] != None:
                        lastpp = pl[index]
                    else:
                        lastpp = None

                    if lastpp:
                        if center[0] == 0:
                            center = [lastpp] + center[:-1]
                        else:
                            center = [(center[0] * 2 + lastpp) / 3] + center[:-1]

                    findAtr = l_atr(df, index, superPd)
                    Up = center[0] - (superFactor * findAtr)
                    Dn = center[0] + (superFactor * findAtr)
                    # h.logger.info(f"MY LATR Up {Up} Dn {Dn} findAtr {findAtr} center {center[0]} ---- df[open] {df['open'].iloc[index]}")
                    # if index == 60:
                    #     break

                    if df["close"].iloc[index - 1] > TUp[1]:
                        TUp = [max(Up, TUp[1])] + TUp[:-1]
                    if df["close"].iloc[index - 1] < TUp[1]:
                        TUp = [Up] + TUp[:-1]

                    if df["close"].iloc[index - 1] < TDown[1]:
                        TDown = [min(Dn, TDown[1])] + TDown[:-1]
                    if df["close"].iloc[index - 1] > TDown[1]:
                        TDown = [Dn] + TDown[:-1]
                    
                    # Trend
                    if df["close"].iloc[index] > TDown[1]:
                        Trend = [1] + Trend[:-1]
                    elif df["close"].iloc[index] < TUp[1]:
                        Trend = [-1] + Trend[:-1]
                    else:
                        Trend = [l_nz(Trend[1], 1)] + Trend[:-1]
                    
                    if Trend[0] == 1:
                        super_coord_long.append(TUp[0])
                        super_coord_short.append(None)
                    if Trend[0] == -1:
                        super_coord_short.append(TDown[0])
                        super_coord_long.append(None)

                    long_signal.append(Trend[0] == 1)
                    short_signal.append(Trend[0] == -1)
        
    except Exception as e:
         h.logger.warning(f'Supertrend {e}')
    h.logger.info(long_signal)
    h.logger.info(short_signal)
    return long_signal, short_signal, super_coord_long, super_coord_short