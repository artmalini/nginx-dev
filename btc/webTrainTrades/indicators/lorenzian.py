from indicators.libmath import l_nz
import math
import pandas as pd
import numpy as np
from numba import njit, prange
import helpers as h

    
f1Array = []
f2Array = []
f3Array = []
f4Array = []
f5Array = []

pineRma = [0]
pineRma1 = [0]
adxRma = [0]
adxDX = [0]
closeU = [0]
closeD = [0]
closeU1 = [0]
closeD1 = [0]

historicMin = [1e10,1e10]
historicMax = [-1e10,-1e10]
historicMinCCI = [1e10,1e10]
historicMaxCCI = [-1e10,-1e10]
closeRsi = [0]
closeRsi1 = [0]
resultCCI = [0]

nwtCi = [0]
hlc3Ci = [0]

close = [0]
high = [0]
low = [0]
trSmooth = [0,0]
smoothDirectionalMovementPlus = [0,0]
smoothnegMovement = [0,0]

def get_lorentzian_distance(i, feature_count) :
    global f1Array
    global f2Array
    global f3Array
    global f4Array
    global f5Array
    distance = 0

    try:
        if feature_count == 5:
            distance = (
                math.log(1 + (abs(f1Array[0] - f1Array[i]))) +
                math.log(1 + (abs(f2Array[0] - f2Array[i]))) +
                math.log(1 + (abs(f3Array[0] - f3Array[i]))) +
                math.log(1 + (abs(f4Array[0] - f4Array[i]))) +
                math.log(1 + (abs(f5Array[0] - f5Array[i])))
            )
        if feature_count == 4:
            distance = (
                math.log(1 + (abs(f1Array[0] - f1Array[i]))) +
                math.log(1 + (abs(f2Array[0] - f2Array[i]))) +
                math.log(1 + (abs(f3Array[0] - f3Array[i]))) +
                math.log(1 + (abs(f4Array[0] - f4Array[i])))
            )
        if feature_count == 3:
            distance = (
                math.log(1 + (abs(f1Array[0] - f1Array[i]))) +
                math.log(1 + (abs(f2Array[0] - f2Array[i]))) +
                math.log(1 + (abs(f3Array[0] - f3Array[i])))
            )

        if feature_count < 3:
            distance = (
                math.log(1 + (abs(f1Array[0] - f1Array[i]))) +
                math.log(1 + (abs(f2Array[0] - f2Array[i])))
            )
    except Exception as e:
        h.logger.warning(f'get_lorentzian_distance {e}')

    return distance


def rescale(src, oldMin, oldMax, newMin, newMax) :
    # h.logger.info(f"Rescale rescale-src {src} oldMin {oldMin} oldMax {oldMax} newMin {newMin} newMax {newMax}")
    return newMin + (newMax - newMin) * (src - oldMin) / max(oldMax - oldMin, 1e10)

def lor_sma(source, length):
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
        h.logger.warning(f'lorenzian sma {e}')
    return sma_values

def lor_ema(source, length):
    ema_values = []
    try:
        if source and length:
            alpha = 2 / (length + 1)

            for i in range(length):
                if i == len(source):
                    break
                if i == 0:
                    ema_values.append(source[i])  # First value is same as source
                else :
                    previous_ema = ema_values[-1]
                    current_value = source[i]
                    ema = alpha * current_value + (1 - alpha) * previous_ema
                    ema_values.append(ema)

            return ema_values
    except Exception as e:
        h.logger.warning(f'lor_ema {e} {ema_values} range(length) {range(length)} len(source){len(source)}')    
    return [0]

# --------------------------------------------------------

def pine_rma(src, length):
    global pineRma

    try:
        alpha = 1 / length
        if pineRma[1] == 0 :
            pineRma = [lor_sma(src, length)[-1]] + pineRma[:-1]
        else:
            pineRma = [alpha * src[0] + (1 - alpha) * pineRma[1]] + pineRma[:-1]
    except Exception as e:
        h.logger.warning(f'pine rma {e}')
    return pineRma

def pine_rsi(src, y):
    global closeU
    global closeD
    global closeRsi

    try:
        closeU = [max(src[0] - src[1], 0)] + closeU[:-1]
        closeD = [max(src[1] - src[0], 0)] + closeD[:-1]
        
        pineRma = pine_rma(closeD, y)[0]
        epsilon = 1e-10
        safe_denominator = np.where(pineRma == 0, epsilon, pineRma)
        rs = pine_rma(closeU, y)[0] / safe_denominator
        closeRsi = [100 - 100 / (1 + rs)] + closeRsi[:-1]
    except Exception as e:
        h.logger.warning(f'pine rsi {e}')
    return closeRsi


def n_rsi(src, f_paramA, f_paramB):
    rescaleResult = 0
    try:
        rescaleResult = rescale(lor_ema(pine_rsi(src, f_paramA), f_paramB)[-1], 0, 100, 0, 1)
    except Exception as e:
        h.logger.warning(f'rescaleResult {e}')
    return rescaleResult

# --------------------------------------------------------

def pine_rma_one(src, length):
    global pineRma1

    try:
        alpha = 1 / length
        if pineRma1[1] == 0 :
            pineRma1 = [lor_sma(src, length)[-1]] + pineRma1[:-1]
        else:
            pineRma1 = [alpha * src[0] + (1 - alpha) * pineRma1[1]] + pineRma1[:-1]
    except Exception as e:
        h.logger.warning(f'pine rma_one {e}')
    return pineRma1

def pine_rsi_one(src, y):
    global closeU1
    global closeD1
    global closeRsi1

    try:
        closeU1 = [max(src[0] - src[1], 0)] + closeU1[:-1]
        closeD1 = [max(src[1] - src[0], 0)] + closeD1[:-1]
        
        pineRma = pine_rma_one(closeD1, y)[0]
        epsilon = 1e-10
        safe_denominator = np.where(pineRma == 0, epsilon, pineRma)
        rs = pine_rma_one(closeU1, y)[0] / safe_denominator
        closeRsi1 = [100 - 100 / (1 + rs)] + closeRsi1[:-1]
    except Exception as e:
        h.logger.warning(f'pine rsi_one {e}')
    return closeRsi1


def n_rsi_one(src, f_paramA, f_paramB):
    rescaleResult = 0
    try:
        rescaleResult = rescale(lor_ema(pine_rsi_one(src, f_paramA), f_paramB)[-1], 0, 100, 0, 1)
    except Exception as e:
        h.logger.warning(f'rescaleResult_one {e}')
    return rescaleResult

# --------------------------------
def normalize(src, arbMin, arbMax) :
    global historicMin
    global historicMax

    try:
        historicMin = [min(src, historicMin[0])] + historicMin[:-1]
        historicMax = [max(src, historicMax[0])] + historicMax[:-1]
        
        denominator = max(historicMax[0] - historicMin[0], 1e-10)
        normalized_value = arbMin + (arbMax - arbMin) * (src - historicMin[0]) / denominator

        return normalized_value
    except Exception as e:
        h.logger.warning(f'normalize {e}')
    return 0

def n_wt(src, n1=10, n2=10):
    global nwtCi
    result = 0
    convertAbsolute = []

    try:
        ema1 = lor_ema(src, n1)
        lenSrc = len(src)
        for idx in range(len(ema1)):
            if lenSrc > idx:
                convertAbsolute.append(abs(src[idx] - ema1[idx]))
        # h.logger.info(f"n_wt convertAbsolute {convertAbsolute}")
        ema2 = lor_ema(convertAbsolute, n1)
        nwtResult = 0.015 * ema2[-1]

        if nwtResult == 0:
            nwtCi = [0] + nwtCi[:-1]
        if nwtResult != 0:
            nwtCi = [(src[0] - ema1[-1]) / (0.015 * ema2[-1])] + nwtCi[:-1]

        wt1 = lor_ema(nwtCi, n2) #tci
        wt2 = lor_sma(wt1, 4)
        # h.logger.info(f"n_wt wt1[-1] {wt1[-1]}  wt2[-1] {wt2[-1]}")
        result = normalize((wt1[-1] - wt2[-1]), 0, 1)

        return result
    except Exception as e:
        h.logger.warning(f'n_wt {e}')
    return result

# -----------------------------------------------------
def normalize_cci(src, arbMin, arbMax) :
    global historicMinCCI
    global historicMaxCCI

    try:
        historicMinCCI = [min(src, historicMinCCI[0])] + historicMinCCI[:-1]
        historicMaxCCI = [max(src, historicMaxCCI[0])] + historicMaxCCI[:-1]
        
        denominator = max(historicMaxCCI[0] - historicMinCCI[0], 1e-10)
        normalized_value = arbMin + (arbMax - arbMin) * (src - historicMinCCI[0]) / denominator
        return normalized_value
        # return (arbMin + (arbMax - arbMin) * (src - historicMin)) / max(historicMax - historicMin, 1e-10)
    except Exception as e:
        h.logger.warning(f'normalize cci {e}')
    return 0

def lor_cci(src, n1):
    global hlc3Ci
    global resultCCI
    convertAbsolute = []

    try:
        sma_tp = lor_sma(hlc3Ci, n1)
        lenSrc = len(sma_tp)
        for idx in range(len(sma_tp)):
            if lenSrc > idx:
                convertAbsolute.append(abs(hlc3Ci[idx] - sma_tp[idx]))

        mean_deviation = lor_sma(convertAbsolute, n1)
        
        # h.logger.info(f"hlc3Ci[0] {hlc3Ci[0]} sma_tp[-1] {sma_tp[-1]} 0.015 * mean {0.015 * mean_deviation[-1]}" )
        # Commodity Channel Index
        resultCCI = [(hlc3Ci[0] - sma_tp[-1]) / (0.015 * mean_deviation[-1])] + resultCCI[:-1]
        # 
        # print(resultCCI)
        
        return resultCCI
    except Exception as e:
        h.logger.warning(f'lor_cci {e}')
    return [0]

def n_cci(src, n1, n2):
    result = 0
    try:
        processCCI = lor_ema(lor_cci(src, n1), n2)
        result = normalize_cci(processCCI[-1], 0, 1)

        return result
    except Exception as e:
        h.logger.warning(f'n_cci {e}')
    return result

# ----------------------------------------------
def adx_rma(src, length):
    global adxRma

    try:
        alpha = 1 / length
        if adxRma[1] == 0 :
            adxRma = [lor_sma(src, length)[-1]] + adxRma[:-1]
        else:
            adxRma = [alpha * src[0] + (1 - alpha) * adxRma[1]] + adxRma[:-1]
    except Exception as e:
        h.logger.warning(f'adx rma {e}')
    return adxRma

def n_adx(n1):
    global high
    global low
    global close
    global trSmooth
    global smoothDirectionalMovementPlus
    global smoothnegMovement
    global adxDX
    result = 0

    try:
        length = n1
        tr = max(max(high[0] - low[0], abs(high[0] - close[1])), abs(low[0] - close[1]))

        if high[0] - high[1] > low[1] - low[0] :
            directionalMovementPlus = max(high[0] - high[1], 0)
        else:
            directionalMovementPlus = 0

        if low[1] - low[0] > high[0] - high[1]:
            negMovement = max(low[1] - low[0], 0)
        else:
            negMovement = 0

        trSmooth = [(trSmooth[1] - trSmooth[1] / length) + tr] + trSmooth[:-1]
        smoothDirectionalMovementPlus = [(smoothDirectionalMovementPlus[1] - smoothDirectionalMovementPlus[1] / length) + directionalMovementPlus] + smoothDirectionalMovementPlus[:-1]
        smoothnegMovement = [(smoothnegMovement[1] - smoothnegMovement[1] / length) + negMovement] + smoothnegMovement[:-1]

        diPositive = smoothDirectionalMovementPlus[0] / trSmooth[0] * 100
        diNegative = smoothnegMovement[0] / trSmooth[0] * 100
        adxDX = [abs(diPositive - diNegative) / (diPositive + diNegative) * 100] + adxDX[:-1]

        adx = adx_rma(adxDX, length)
        result = rescale(adx[0], 0, 100, 0, 1)

        return result
    except Exception as e:
        h.logger.warning(f'n_adx {e}')
    return result

def series_from(src, feature_string, f_paramA, f_paramB):
    try:
        if feature_string == "RSI":
            result = n_rsi(src, f_paramA, f_paramB)
            # h.logger.info(f"result n_rsi {result}")
            return result
        if feature_string == "WT":
            result = n_wt(src, f_paramA, f_paramB)
            # h.logger.info(f"result n_wt {result}")
            return result
        if feature_string == "CCI":
            result = n_cci(src, f_paramA, f_paramB)
            # h.logger.info(f"result n_cci {result}")
            return result
        if feature_string == "ADX":
            result = n_adx(f_paramA)
            # h.logger.info(f"result n_adx {result}")
            return result
        if feature_string == "RSI1":
            result = n_rsi_one(src, f_paramA, f_paramB)
            # h.logger.info(f"result n_rsi_one {result}")
            return result

    except Exception as e:
        h.logger.warning(f'series_from {e}')

# def get_lorentzian_distance(df, i, featureSeries, featureArrays) :
#     return  math.log(1 + abs(featureSeries.f1 - array.get(featureArrays.f1, i)))

def lorenzian(df, source, neighborsCount, maxBarsBack, featureSeries, featureCount=2):
    long_signal = []
    short_signal = []
    global high
    global low
    global close
    global pineRma
    global pineRma1
    global adxRma
    global adxDX
    global closeU
    global closeD
    global closeU1
    global closeD1
    global closeRsi
    global closeRsi1
    global nwtCi
    global hlc3Ci
    global resultCCI
    global f1Array
    global f2Array
    global f3Array
    global f4Array
    global f5Array
    
    try:
        if not df.empty:            
            close = [0] * featureSeries["f1_string"]["f1_paramA"]
            hlc3 = [0] * featureSeries["f2_string"]["f1_paramA"]
            nwtCi = [0] * featureSeries["f2_string"]["f1_paramB"]
            hlc3Ci = [0] * featureSeries["f3_string"]["f1_paramA"]
            resultCCI = [0] * featureSeries["f3_string"]["f1_paramA"]
            high = [0] * featureSeries["f4_string"]["f1_paramA"]
            low = [0] * featureSeries["f4_string"]["f1_paramA"]

            pineRma = [0] * featureSeries["f1_string"]["f1_paramA"]
            adxRma = [0] * featureSeries["f4_string"]["f1_paramA"]
            adxDX = [0] * featureSeries["f4_string"]["f1_paramA"]
            closeU = [0] * featureSeries["f1_string"]["f1_paramA"]
            closeD = [0] * featureSeries["f1_string"]["f1_paramA"]
            closeRsi = [0] * featureSeries["f1_string"]["f1_paramA"]

            pineRma1 = [0] * featureSeries["f5_string"]["f1_paramA"]
            closeU1 = [0] * featureSeries["f5_string"]["f1_paramA"]
            closeD1 = [0] * featureSeries["f5_string"]["f1_paramA"]
            closeRsi1 = [0] * featureSeries["f5_string"]["f1_paramA"]

            f1Array = [0] * maxBarsBack
            f2Array = [0] * maxBarsBack
            f3Array = [0] * maxBarsBack
            f4Array = [0] * maxBarsBack
            f5Array = [0] * maxBarsBack

            direction = {
                "long": 1, 
                "short": -1, 
                "neutral": 0
            }
            y_train_series = np.array([direction["neutral"], direction["neutral"],direction["neutral"],direction["neutral"]])
            # y_train_series = [0]
            feature_count = featureCount
            y_train_array = np.zeros(maxBarsBack)
            # distances = []
            # predictions = []
            distances = [0] * (neighborsCount)
            predictions = [0] * (neighborsCount)
            countPredictions = 0
            # prediction = 0
            # sizeLoop = np.zeros(maxBarsBack - 1)
            
            distancesIndex = round((neighborsCount * 3 / 4)) - 1
            if distancesIndex < 0:
                distancesIndex = 0
            if distancesIndex >= neighborsCount:
                distancesIndex = neighborsCount - 1

            for index in range(len(df)):
                last_distance = -1.0
                prediction = 0                

                close = [df["close"].iloc[index]] + close[:-1]
                high = [df["high"].iloc[index]] + high[:-1]
                low = [df["low"].iloc[index]] + low[:-1]
                hlResult = (df["high"].iloc[index] + df["low"].iloc[index] + df["close"].iloc[index])
                if hlResult == 0:
                    hlc3 = [0] + hlc3[:-1]
                    hlc3Ci = [0] + hlc3Ci[:-1]
                if hlResult != 0:
                    hlc3 = [hlResult / 3] + hlc3[:-1]
                    hlc3Ci = [hlResult / 3] + hlc3Ci[:-1]

                # size = min(maxBarsBack - 1, len(y_train_array) - 1)
                # sizeLoop = min(maxBarsBack - 1, size)
                sizeLoop = np.zeros(maxBarsBack)
                shiftindex = index - 4

                # if index >= maxBarsBack:
                #     h.logger.info(f"SIZE LOOP {len(sizeLoop)}")

                if shiftindex <= 0 :
                    y_train_series[-1] = direction["neutral"]
                    y_train_series = np.roll(y_train_series, 1)
                if shiftindex > 0 :
                    if source.iloc[shiftindex] < source.iloc[index]:
                        y_train_series[-1] = direction["short"]
                        y_train_series = np.roll(y_train_series, 1)
                    if source.iloc[shiftindex] > source.iloc[index] :
                        y_train_series[-1] = direction["long"]
                        y_train_series = np.roll(y_train_series, 1)
                    if source.iloc[shiftindex] == source.iloc[index] :
                        y_train_series[-1] = direction["neutral"]
                        y_train_series = np.roll(y_train_series, 1)

                y_train_array[-1] = y_train_series[0]
                y_train_array = np.roll(y_train_array, 1)
                f1Array = [(series_from(close, featureSeries["f1_string"]["Feature"], featureSeries["f1_string"]["f1_paramA"], featureSeries["f1_string"]["f1_paramB"]))] + f1Array[:-1]
                f2Array = [(series_from(hlc3, featureSeries["f2_string"]["Feature"], featureSeries["f2_string"]["f1_paramA"], featureSeries["f2_string"]["f1_paramB"]))] + f2Array[:-1]
                f3Array = [(series_from(close, featureSeries["f3_string"]["Feature"], featureSeries["f3_string"]["f1_paramA"], featureSeries["f3_string"]["f1_paramB"]))] + f3Array[:-1]
                f4Array = [(series_from(close, featureSeries["f4_string"]["Feature"], featureSeries["f4_string"]["f1_paramA"], featureSeries["f4_string"]["f1_paramB"]))] + f4Array[:-1]
                f5Array = [(series_from(close, featureSeries["f5_string"]["Feature"], featureSeries["f5_string"]["f1_paramA"], featureSeries["f5_string"]["f1_paramB"]))] + f5Array[:-1]
                
                # if index == 30:
                #     print(df.index)
                #     h.logger.info(f"check {len(f1Array)} f1Array {f1Array}")
                #     h.logger.info(f"check {len(f2Array)} f2Array {f2Array}")
                #     h.logger.info(f"check {len(f3Array)} f3Array {f3Array}")
                #     h.logger.info(f"check {len(f4Array)} f4Array {f4Array}")
                #     h.logger.info(f"check {len(f5Array)} f5Array {f5Array}")
                #     return
                # h.logger.info(f"y_train_array[i] {y_train_array[i]}  i: {i}")

                if index >= maxBarsBack:
                    for i in range(len(sizeLoop)):
                        d = get_lorentzian_distance(i, feature_count)
                        if d >= last_distance and i % 4 == 0:
                            last_distance = d
                            distances = distances[1:] + [d]
                            predictions = predictions[1:] + [y_train_array[i]]
                            countPredictions += 1

                            if countPredictions == neighborsCount:
                                # h.logger.info(f"countPredictions {countPredictions} len(predictions) {len(predictions)}  len(distances) {len(distances)} round((neighborsCount * 3 / 4) - 1) {round((neighborsCount * 3 / 4) - 1)} distances {distances[round((neighborsCount * 3 / 4) - 1)]} lorenzian dist {d} ")
                                last_distance = distances[distancesIndex]
                                countPredictions -= 1
                    prediction = sum(predictions)
                    # print(prediction)

                # if index == 14001:
                #     return
                
                if prediction > 0 :
                    long_signal.append(True)
                    short_signal.append(False)
                if prediction < 0 :
                    short_signal.append(True)
                    long_signal.append(False)
                if prediction == 0 :
                    short_signal.append(False)
                    long_signal.append(False)

        
    except Exception as e:
         h.logger.warning(f'Lorenzian {e}')

    return long_signal, short_signal