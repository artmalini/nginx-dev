import pandas as pd
import numpy as np
import math
import ta_py as ta
from indicators.libmath import linreg, l_highest, l_sum, l_lowest, l_nz
import helpers as h

varFunc = [0.0] * 2
longStop = [0.0] * 2
shortStop = [0.0] * 2
dir = [-1] * 2
longStopl = [0.0] * 2
shortStopl = [0.0] * 2
varFuncl = [0.0] * 2
dirl = [-1] * 2
hoot = []
loot = []

vud1 = [0.0] * 9
vdd1 = [0.0] * 9
vud1l = [0.0] * 9
vdd1l = [0.0] * 9

def Var_Func(df, index, hlootSrc, hlootSrclowest, length, hllength, mav):
    global varFunc
    global vud1
    global vdd1
    hlootSrcPrevious = 0
    try:
       hlootSrcPrevious = hlootSrc[index - 1]
    except:
        hlootSrcPrevious = hlootSrc[index]

    try:
        
        valpha = 2 / (length + 1)
        
        vud1 = [np.where(hlootSrc[index] > hlootSrcPrevious, hlootSrc[index] - hlootSrcPrevious, 0)] + vud1[:-1]
        vdd1 = [np.where(hlootSrc[index] < hlootSrcPrevious, hlootSrcPrevious - hlootSrc[index], 0)] + vdd1[:-1] 
        
        # print(vud1)
        vUD = l_sum(vud1, 9)
        vDD = l_sum(vdd1, 9)
        
        vCMO = (vUD - vDD) / (vUD + vDD) if (vUD + vDD) != 0 else 0
        
        varFunc = [(valpha * abs(vCMO) * hlootSrc[index]) + (1 - valpha * abs(vCMO)) * varFunc[1]] + varFunc[:-1] 
        # Shift values in varFunc list to make space for the new VAR value       
        # h.logger.info(f"Var_Func {varFunc[0]}")
        return varFunc[0]
    except Exception as e:
        h.logger.warning(f"Var_Func {e}")

def Var_Funcl(df, index, hlootSrc, hlootSrclowest, length, hllength, mav):
    try:
        global varFuncl
        global vud1l 
        global vdd1l
        hlootSrclowestPrevious = 0
        try:
            hlootSrclowestPrevious = hlootSrclowest[index - 1]
        except:
            hlootSrclowestPrevious = hlootSrclowest[index]

        valphal = 2 / (length + 1)

        vud1l = [np.where(hlootSrclowest[index] > hlootSrclowestPrevious, hlootSrclowest[index] - hlootSrclowestPrevious, 0)] + vud1l[:-1] 
        vdd1l = [np.where(hlootSrclowest[index] < hlootSrclowestPrevious, hlootSrclowestPrevious - hlootSrclowest[index], 0)] + vdd1l[:-1] 
        vUDl = l_sum(vud1l, 9)
        vDDl = l_sum(vdd1l, 9)

        vCMOl = (vUDl - vDDl) / (vUDl + vDDl) if (vUDl + vDDl) != 0 else 0

        varFuncl = [(valphal * abs(vCMOl) * hlootSrclowest[index]) + (1 - valphal * abs(vCMOl)) * varFuncl[1]] + varFuncl[:-1]

        # h.logger.info(f"Var_Funcl result {varFuncl[0]}")
        return varFuncl[0]
    except Exception as e:
        h.logger.warning(f"Var_Funcl {e}")

def Wwma_Func(hlootSrc, length):
    wwalpha = 1 / length
    WWMA = np.zeros_like(hlootSrc)
    for i in range(len(hlootSrc)):
        WWMA[i] = wwalpha * hlootSrc[i] + (1 - wwalpha) * (WWMA[i-1] if i > 0 else 0)
    return WWMA

def Zlema_Func(hlootSrc, length):
    zxLag = length // 2 if length % 2 == 0 else (length - 1) // 2
    zxEMAData = hlootSrc + hlootSrc - hlootSrc.shift(zxLag)
    ZLEMA = zxEMAData.ewm(span=length, adjust=False).mean()
    return ZLEMA

def Tsf_Func(hlootSrc, length):
    lrc = hlootSrc.rolling(window=length, min_periods=0).apply(lambda x: np.polyfit(range(length), x, 1)[0], raw=True)
    lrc1 = hlootSrc.shift(length).rolling(window=length, min_periods=0).apply(lambda x: np.polyfit(range(length), x, 1)[0], raw=True)
    lrs = lrc - lrc1
    TSF = lrc + lrs
    return TSF

def Wwma_Funcl(hlootSrcl, length):
    wwalphal = 1 / length
    WWMAl = np.zeros_like(hlootSrcl)
    for i in range(len(hlootSrcl)):
        WWMAl[i] = wwalphal * hlootSrcl[i] + (1 - wwalphal) * (WWMAl[i-1] if i > 0 else 0)
    return WWMAl

def Zlema_Funcl(hlootSrcl, length):
    zxLagl = length // 2 if length % 2 == 0 else (length - 1) // 2
    zxEMADatal = hlootSrcl + hlootSrcl - hlootSrcl.shift(zxLagl)
    ZLEMAl = zxEMADatal.ewm(span=length, adjust=False).mean()
    return ZLEMAl

def Tsf_Funcl(hlootSrcl, length):
    lrcl = hlootSrcl.rolling(window=length, min_periods=0).apply(lambda x: np.polyfit(range(length), x, 1)[0], raw=True)
    lrc1l = hlootSrcl.shift(length).rolling(window=length, min_periods=0).apply(lambda x: np.polyfit(range(length), x, 1)[0], raw=True)
    lrsl = lrcl - lrc1l
    TSFl = lrcl + lrsl
    return TSFl

def getMA(df, index, hlootSrc, hlootSrclowest, length, hllength, mav):
    if mav == 'SMA':
        return hlootSrc.rolling(window=length, min_periods=0).mean()
    elif mav == 'EMA':
        return hlootSrc.ewm(span=length, adjust=False).mean()
    elif mav == 'WMA':
        weights = np.arange(1, length+1)
        return hlootSrc.rolling(window=length, min_periods=0).apply(lambda x: np.dot(x, weights)/weights.sum(), raw=True)
    elif mav == 'DEMA':
        return 2 * hlootSrc.ewm(span=length, adjust=False).mean() - hlootSrc.ewm(span=length, adjust=False).mean().ewm(span=length, adjust=False).mean()
    elif mav == 'TMA':
        sma1 = hlootSrc.rolling(window=math.ceil(length / 2), min_periods=0).mean()
        return sma1.rolling(window=math.floor(length / 2) + 1, min_periods=0).mean()
    elif mav == 'VAR':
        return Var_Func(df, index, hlootSrc, hlootSrclowest, length, hllength, mav)
    elif mav == 'WWMA':
        return Wwma_Func(hlootSrc, length)
    elif mav == 'ZLEMA':
        return Zlema_Func(hlootSrc, length)
    elif mav == 'TSF':
        return Tsf_Func(hlootSrc, length)
    elif mav == 'HULL':
        return 2 * hlootSrc.ewm(span=length, adjust=False).mean() - hlootSrc.ewm(span=math.isqrt(length), adjust=False).mean()

def getMAl(df, index, hlootSrc, hlootSrclowest, length, hllength, mav):
    if mav == 'SMA':
        return hlootSrclowest.rolling(window=length, min_periods=0).mean()
    elif mav == 'EMA':
        return hlootSrclowest.ewm(span=length, adjust=False).mean()
    elif mav == 'WMA':
        weights = np.arange(1, length+1)
        return hlootSrclowest.rolling(window=length, min_periods=0).apply(lambda x: np.dot(x, weights)/weights.sum(), raw=True)
    elif mav == 'DEMA':
        return 2 * hlootSrclowest.ewm(span=length, adjust=False).mean() - hlootSrclowest.ewm(span=length, adjust=False).mean().ewm(span=length, adjust=False).mean()
    elif mav == 'TMA':
        sma1 = hlootSrclowest.rolling(window=math.ceil(length / 2), min_periods=0).mean()
        return sma1.rolling(window=math.floor(length / 2) + 1, min_periods=0).mean()
    elif mav == 'VAR':
        return Var_Funcl(df, index, hlootSrc, hlootSrclowest, length, hllength, mav)
    elif mav == 'WWMA':
        return Wwma_Funcl(hlootSrclowest, length)
    elif mav == 'ZLEMA':
        return Zlema_Funcl(hlootSrclowest, length)
    elif mav == 'TSF':
        return Tsf_Funcl(hlootSrclowest, length)
    elif mav == 'HULL':
        return 2 * hlootSrclowest.ewm(span=length, adjust=False).mean() - hlootSrclowest.ewm(span=math.isqrt(length), adjust=False).mean()


def hloot(df, trainedSource, hlooSource, length, percent, hllength, hlootMav, useReverseOrderHLOOT):
    # try:
    # global hlootSrc
    # global hlootSrclowest
    long_signal = []
    short_signal = []
    global longStop
    global shortStop
    global dir
    global longStopl
    global shortStopl
    global dirl
    global hoot
    global loot


    global vud1
    global vdd1
    global vud1l
    global vdd1l

    if trainedSource["hloot"]["trained"] == True:
        long_signal = trainedSource["hloot"]["long_signal"]
        short_signal = trainedSource["hloot"]["short_signal"]
        longStop = trainedSource["hloot"]["longStop"]
        shortStop = trainedSource["hloot"]["shortStop"]
        dir = trainedSource["hloot"]["dir"]
        longStopl = trainedSource["hloot"]["longStopl"]
        shortStopl = trainedSource["hloot"]["shortStopl"]
        dirl = trainedSource["hloot"]["dirl"]
        hoot = trainedSource["hloot"]["hoot"]
        loot = trainedSource["hloot"]["loot"]
        vud1 = trainedSource["hloot"]["vud1"]
        vdd1 = trainedSource["hloot"]["vdd1"]
        vud1l = trainedSource["hloot"]["vud1l"]
        vdd1l = trainedSource["hloot"]["vdd1l"]

    try:
        if not df.empty and length:
            # hlootSrc = [l_highest(df['high'], hllength)] + hlootSrc[:-1]
            # h.logger.info(f'DF HIGH {df["high"]}')
            hlootSrc = l_highest(df, 'high', hllength)
            # hlootSrcPrevious = hlootSrc[1]
            hlootSrclowest = l_lowest(df, 'low', hllength)
            # hlootSrclowestPrevious = hlootSrclowest[1]
            # h.logger.info(f"hlootSrc {hlootSrc}")
            # h.logger.info(f"hlootSrclowest {hlootSrclowest}")
            # build starting hoot and loot 2 items
            for index in range(0, 2):
                hoot.append(hlootSrc[0])

                loot.append(hlootSrclowest[0])
            for index in range(len(df)):
                MAvg = getMA(df, index, hlootSrc, hlootSrclowest, length, hllength, hlootMav)
                fark = MAvg * percent * 0.01
                longStop = [MAvg - fark] + longStop[:-1]
                longStopPrev = l_nz(longStop[1], longStop[0])
                longStopExec = np.where(MAvg > longStopPrev, np.maximum(longStop[0], longStopPrev), longStop[0])
                shortStop = [MAvg + fark] + shortStop[:-1]
                shortStopPrev = l_nz(shortStop[1], shortStop[0])
                shortStopExec = np.where(MAvg < shortStopPrev, np.minimum(shortStop[0], shortStopPrev), shortStop[0])
                tempDir = dir[0] if dir[0] != None else 1
                if dir[0] == -1 and MAvg > shortStopPrev:
                    tempDir = 1
                elif dir[0] == 1 and MAvg < longStopPrev:
                    tempDir = -1
                dir = [tempDir] + dir[:-1]    
                MT = longStopExec if dir[0] == 1 else shortStopExec
                hoot.append(np.where(MAvg > MT, MT * (200 + percent) / 200, MT * (200 - percent) / 200))
                HOTTC = 'blue'
                # h.logger.info(f"HOOT {hoot}")

                MAvgl = getMAl(df, index, hlootSrc, hlootSrclowest, length, hllength, hlootMav)
                farkl = MAvgl * percent * 0.01
                longStopl = [MAvgl - farkl] + longStopl[:-1]
                longStopPrevl = l_nz(longStopl[1], longStopl[0])
                longStoplExec = np.where(MAvgl > longStopPrevl, np.maximum(longStopl[0], longStopPrevl), longStopl[0])
                shortStopl = [MAvgl + farkl] + shortStop[:-1]
                shortStopPrevl = l_nz(shortStopl[1], longStopl[0])
                shortStoplExec = np.where(MAvgl < shortStopPrevl, np.minimum(shortStopl[0], shortStopPrevl), shortStopl[0])
                # dirl[0] = 1
                # dirl[0] = l_nz(dirl[1], dirl[0])

                tempDirl = dirl[0] if dirl[0] != None else 1
                if dirl[0] == -1 and MAvgl > shortStopPrevl:
                    tempDirl = 1
                elif dirl[0] == 1 and MAvgl < longStopPrevl:
                    tempDirl = -1
                dirl = [tempDirl] + dirl[:-1] 
                # h.logger.info(dirl)
                MTl = longStoplExec if dirl[0] == 1 else shortStoplExec
                # loot = [np.where(MAvgl > MTl, MTl * (200 + percent) / 200, MTl * (200 - percent) / 200)] + loot[:-1]
                loot.append(np.where(MAvgl > MTl, MTl * (200 + percent) / 200, MTl * (200 - percent) / 200))
                LOTTC = 'red'
                # h.logger.info(f"LOOT {loot}")
                # h.logger.info(f"long exmpl {hoot} ")
                if useReverseOrderHLOOT == False :
                    long_signal.append(df[hlooSource][index] > hoot[index - 2])
                    short_signal.append(df[hlooSource][index] < loot[index - 2])
                    
                if useReverseOrderHLOOT == True :
                    short_signal.append(df[hlooSource][index] > hoot[index - 2])
                    long_signal.append(df[hlooSource][index] < loot[index - 2])
        # h.logger.info(f"hoot {hoot} ")
        # h.logger.info(f"long_signal {long_signal}  ")
        # h.logger.info(f"short_signal {short_signal} ")
    except Exception as e:
        h.logger.warning(f'DF {e}')

    if trainedSource["hloot"]["trained"] == False:
        trainedSource["hloot"]["trained"] = True
        trainedSource["hloot"]["long_signal"] = long_signal
        trainedSource["hloot"]["short_signal"] = short_signal
        trainedSource["hloot"]["longStop"] = longStop
        trainedSource["hloot"]["shortStop"] = shortStop
        trainedSource["hloot"]["dir"] = dir
        trainedSource["hloot"]["longStopl"] = longStopl
        trainedSource["hloot"]["shortStopl"] = shortStopl
        trainedSource["hloot"]["dirl"] = dirl
        trainedSource["hloot"]["hoot"] = hoot
        trainedSource["hloot"]["loot"] = loot
        trainedSource["hloot"]["vud1"] = vud1
        trainedSource["hloot"]["vdd1"] = vdd1
        trainedSource["hloot"]["vud1l"] = vud1l
        trainedSource["hloot"]["vdd1l"] = vdd1l

    # MAvg = getMA(df, hlootSrc, hlootSrcPrevious, hlootSrclowest, hlootSrclowestPrevious, length, hllength, hlootMav)
    return long_signal, short_signal, hoot, loot, trainedSource
