# from indicators.libmath import l_ema
import sys
import pandas as pd
import math
import helpers as h

def isZero(val, eps):
    return abs(val) <= eps

def SUM(fst, snd):
    EPS = 1e-10
    res = fst + snd
    if isZero(res, EPS):
        res = 0
    else:
        if not isZero(res, 1e-4):
            res = res
        else:
            res = 15
    return res

def rti_sma(df, index, source, length):
    sma_values = []
    try:
        if not df.empty and length:
            for i in range(length):
                sum_val = 0
                value = None
                index = index - length + i
                if index < 0:
                    value = df[source].iloc[0]
                if index >= 0:  # Ensure index is non-negative
                    value = df[source].iloc[index]
                if not pd.isnull(value):  # Skip NaN values
                    sum_val += value / length
                sma_values.append(sum_val)

            return sma_values
    except Exception as e:
        h.logger.warning(f'rti sma {e}')
        return sma_values

def pine_stdev(df, index, source, length):
    # avg = sum(src[-length:]) / length
    avg = rti_sma(df, index, source, length)

    # h.logger.info(f"pine_stdev avg {avg}")
    sumOfSquareDeviations = 0.0

    for i in range(length):
        if index == 0:
            sum_val = SUM(df[source].iloc[0], -avg[i])
        else:
            sum_val = SUM(df[source].iloc[index - i], -avg[i])
        sumOfSquareDeviations += sum_val * sum_val

    stdev = math.sqrt(sumOfSquareDeviations / length)
    return stdev

def rti_ema(source, length):
    ema_values = []
    try:
        if source and length:
            alpha = 2 / (length + 1)

            for i in range(length):
                if i == 0:
                    ema_values.append(source[i])  # First value is same as source
                else:
                    previous_ema = ema_values[-1]
                    current_value = source[i]
                    ema = alpha * current_value + (1 - alpha) * previous_ema
                    ema_values.append(ema)

            return ema_values
    except Exception as e:
        h.logger.warning(f'rti_ema {e} {ema_values}')
        return ema_values

def rti(df, useRTIrestrictObOs, useRTImovingAverageCrossingRTI, trendDataCount, trendSensitivityPercentage, signalLength, obRTI, osRTI):
    long_signal = []
    short_signal = []
    
    try:
        if not df.empty :

            RelativeTrendIndex = [0] * signalLength
            upper_array = [sys.maxsize] * (trendDataCount - 1)
            lower_array = [sys.maxsize] * (trendDataCount - 1)

            for index in range(len(df)):
                stdev = pine_stdev(df, index, "close", 1)

                upper_trend = df["close"].iloc[index] + stdev
                lower_trend = df["close"].iloc[index] - stdev

                upper_array = [upper_trend] + upper_array[:-1]
                lower_array = [lower_trend] + lower_array[:-1]
                upper_array.sort()
                lower_array.sort()

                upper_index  = round(trendSensitivityPercentage / 100 * trendDataCount) - 1
                lower_index  = round((100 - trendSensitivityPercentage) / 100 * trendDataCount) - 1
                UpperTrend   = upper_array[upper_index]
                LowerTrend   = lower_array[lower_index]

                # upper_index  = round(trendSensitivityPercentage / 100 * trendDataCount) - 1
                # lower_index  = round((100 - trendSensitivityPercentage) / 100 * trendDataCount) - 1
                # UpperTrend   = upper_trend
                # LowerTrend   = lower_trend

                # if index == 4012:
                #     h.logger.info(f"upper_index {upper_index} lower_index {lower_index} UpperTrend  {UpperTrend} upper_array {upper_array}")
                #     return
                # h.logger.info(f"UpperTrend  {UpperTrend} LowerTrend {LowerTrend}  {UpperTrend - LowerTrend}")

                if UpperTrend - LowerTrend == 0:
                    RelativeTrendIndex = [1] + RelativeTrendIndex[:-1]
                if UpperTrend - LowerTrend != 0:
                    RelativeTrendIndex = [((df["close"].iloc[index] - LowerTrend) / (UpperTrend - LowerTrend))*100] + RelativeTrendIndex[:-1]

                MA_RelativeTrendIndex = rti_ema(RelativeTrendIndex, signalLength)
                # if index == 320 :
                #     h.logger.info(f"MA_RelativeTrendIndex {MA_RelativeTrendIndex}")
                #     return

                isRTILong = False
                isRTIShort = False
                isRTIAverageCroosLong = False
                isRTIAverageCroosShort = False
                if useRTIrestrictObOs == False:
                    isRTILong = RelativeTrendIndex[-1] > 50 and RelativeTrendIndex[-1] < obRTI
                if useRTIrestrictObOs == True:
                    isRTILong = RelativeTrendIndex[-1] > 50
                if isRTIShort == False:
                    isRTIShort = RelativeTrendIndex[-1] < 50 and RelativeTrendIndex[-1] > osRTI
                if isRTIShort == True:
                    isRTIShort = RelativeTrendIndex[-1] < 50

                if useRTImovingAverageCrossingRTI == False:
                    isRTIAverageCroosLong = isRTILong
                    isRTIAverageCroosShort = isRTIShort
                if useRTImovingAverageCrossingRTI == True:
                    isRTIAverageCroosLong = (RelativeTrendIndex[-1] > MA_RelativeTrendIndex[-1]) and isRTILong
                    isRTIAverageCroosShort = (RelativeTrendIndex[-1] < MA_RelativeTrendIndex[-1]) and isRTIShort

                long_signal.append(isRTIAverageCroosLong)
                short_signal.append(isRTIAverageCroosShort)
        
    except Exception as e:
         h.logger.warning(f'RTI {e}')

    return long_signal, short_signal