from indicators.vslrt import vslrt
from indicators.hloot import hloot
from indicators.ema import ema
from indicators.sma import sma
from indicators.supertrend import supertrend
from indicators.zerolag import zerolag
from indicators.rti import rti
from indicators.andeanoscelator import andeanoscelator
from indicators.heikenashi import heikenashi
from indicators.lorenzian import lorenzian
import plotly.graph_objects as go
import pandas as pd
import helpers as h

def lC(df, trainedSource):
    # Inputs
    inputs = {
        "dateRange": False,
        "source": "open",
        "neighborsCount": 8,
        "maxBarsBack": 2000,
        "featureCount": 5,
        "featureSeries": {
            "f1_string": {"Feature": "RSI", "f1_paramA": 14, "f1_paramB": 1},
            "f2_string": {"Feature": "WT", "f1_paramA": 10, "f1_paramB": 11},
            "f3_string": {"Feature": "CCI", "f1_paramA": 20, "f1_paramB": 1},
            "f4_string": {"Feature": "ADX", "f1_paramA": 20, "f1_paramB": 1},
            "f5_string": {"Feature": "RSI1", "f1_paramA": 4, "f1_paramB": 1},
        },
        "useLorenzian": True,
        "useVSLRT": False,
        "useHLOOT": False,
        "useEma": False,
        "useSma": False,
        "useSUPERTREND": False,
        "useZeroLag": False,
        "useRTI": False,  
        "enableAO": False, 
        "enableHeikenAshi": False,
        "vslrtLen1": 20, # ==== VSLRT ====
        "vslrtLen2": 50, # ====  ====
        "hlooSource": "open", # ==== HLOOT ====
        "hlootLength": 2,
        "hlootPercent": 0.7,
        "hlootHllength": 53,
        "hlootMav": "VAR", 
        "useReverseOrderHLOOT": False, # ====  ====
        "emaSource": "open", #  ==== EMA Moving Average ====
        "emalen": 8, # ====  ====
        "smaSource": "open", #  ==== SMA Moving Average ====
        "smalen": 200, # ====  ====
        "superPrd": 2, # ==== Pivot Point SUPERTRENDT ==== 
        "superFactor": 3,
        "superPd": 10, # ====  ====
        "useExitCrossZeroLag": False, # ==== ZERO LAG ====
        "useEntryAboveBelowZeroLag": True,
        "smthtype": "Kaufman",
        "srcin": "open",
        "inpPeriodFast": 22,
        "inpPeriodSlow": 144, # ====  ====
        "useRTIrestrictObOs": False, # ==== Relative Trend Index (RTI) by Zeiierman ====
        "useRTImovingAverageCrossingRTI": True,
        "trendDataCount": 100,
        "trendSensitivityPercentage": 95,
        "signalLength": 20,
        "obRTI": 80,
        "osRT": 20, # ====  ====
        "lengthAO": 50, # ==== Andean Oscillator ==== 
        "sigLengthAO": 9, # ====  ====
        "lenFSM": 10,#  ==== Smoothed Heiken Ashi Candles ==== 
        "len2SSM": 10
    }
    
    # dateRange = False
    # source = df['open']
    # neighborsCount = 8
    # maxBarsBack = 2000
    # featureCount = 5
    # colorCompression = 1

    # ==== VSLRT ====
    # useVSLRT = False
    # vslrtLen1 = 20
    # vslrtLen2 = 50

    # ==== HLOOT ====
    # useHLOOT = True
    # hlooSource = "open"
    # hlootLength = 2
    # hlootPercent = 0.7
    # hlootHllength = 53
    hoot = [0.0] * 2
    loot = [0.0] * 2
    # hlootMav = 'VAR'
    # useReverseOrderHLOOT = False

    #  ==== Moving Average ====
    # useEma = False
    # emaSource = "open"
    # emalen = 8
    ema_coord = [0.0] * 2
    # ----
    # useSma = False
    # smaSource = "open"
    # smalen = 200
    smaout_coord = [0.0] * 2

    # ==== Pivot Point SUPERTRENDT ==== 
    # useSUPERTREND = True
    # superPrd = 2
    # superFactor = 3
    # superPd = 10
    super_coord_long = [0.0] * 2
    super_coord_short = [0.0] * 2

    # ==== ZERO LAG ====
    zerocoord_fast = [0.0] * 2
    zerocoord_slow = [0.0] * 2

    # ==== Relative Trend Index (RTI) by Zeiierman ====

    useReverseOrder = False
    trainedSourceOutput = trainedSource

    if inputs["useLorenzian"]:
        lorenzian_long_entry, lorenzian_short_entry, trainedSourceLC = lorenzian(df, trainedSource, inputs["source"], inputs["neighborsCount"], inputs["maxBarsBack"], inputs["featureSeries"], inputs["featureCount"])
        trainedSourceOutput.update(trainedSourceLC)
    if inputs["useVSLRT"]:
        vslrt_long_entry, vslrt_short_entry, trainedSourceVslrt = vslrt(df, trainedSource, inputs["source"], inputs["vslrtLen1"], inputs["vslrtLen2"])
        trainedSourceOutput.update(trainedSourceVslrt)
    if inputs["useHLOOT"]:
        hloot_long_entry, hloot_short_entry, hoot, loot, trainedSourceHloot = hloot(df, trainedSource, inputs["hlooSource"], inputs["hlootLength"], inputs["hlootPercent"], inputs["hlootHllength"], inputs["hlootMav"], inputs["useReverseOrderHLOOT"])
        trainedSourceOutput.update(trainedSourceHloot)
    if inputs["useEma"]:
        ema_long_entry, ema_short_entry, emaout = ema(df, inputs["emaSource"], inputs["emalen"])
    if inputs["useSma"]:
        sma_long_entry, sma_short_entry, smaout = sma(df, inputs["smaSource"], inputs["smalen"])
    if inputs["useSUPERTREND"]:
        super_long_entry, super_short_entry, super_coord_long, super_coord_short = supertrend(df, inputs["superPrd"], inputs["superFactor"], inputs["superPd"])
    if inputs["useZeroLag"]:
        zerolag_long_entry, zerolag_short_entry, zero_coord_fast, zero_coord_slow = zerolag(df, inputs["useExitCrossZeroLag"], inputs["useEntryAboveBelowZeroLag"], inputs["smthtype"], inputs["srcin"], inputs["inpPeriodFast"], inputs["inpPeriodSlow"])
    if inputs["useRTI"]:
        rti_long_entry, rti_short_entry = rti(df, inputs["useRTIrestrictObOs"], inputs["useRTImovingAverageCrossingRTI"], inputs["trendDataCount"], inputs["trendSensitivityPercentage"], inputs["signalLength"], inputs["obRTI"], inputs["osRT"])
    if inputs["enableAO"]:
        ao_long_entry, ao_short_entry = andeanoscelator(df,inputs["lengthAO"], inputs["sigLengthAO"])
    if inputs["enableHeikenAshi"]:
        heiken_long_entry, heiken_short_entry = heikenashi(df, inputs["lenFSM"], inputs["len2SSM"])    
    
    # h.logger.info(f"emaout {ema_long_entry} lenema {len(ema_long_entry)} short {len(ema_long_entry)} lendef {len(df)}")
    # return
    dfPlaceholrers = [] # pd.DataFrame(index=df.index, columns=['close_datetime'], data=True)
    if not df.empty:
        for index in range(len(df)):
            dfPlaceholrers.append(True)

    # result = [all(values) for values in zip(list1, list2, list3)]


    # h.logger.info(f"vslrt_long_entry {vslrt_long_entry}")
    # h.logger.info(f"dfPlaceholrers {dfPlaceholrers}")
    try:
        isLorennzianLong = dfPlaceholrers
        isLorennzianShort = dfPlaceholrers
        if inputs["useLorenzian"]:
            isLorennzianLong = lorenzian_long_entry
            isLorennzianShort = lorenzian_short_entry
        isVSLRTlong = dfPlaceholrers
        isVSLRTshort = dfPlaceholrers
        if inputs["useVSLRT"]:
            isVSLRTlong = vslrt_long_entry
            isVSLRTshort = vslrt_short_entry
        isHLOOTlong = dfPlaceholrers
        isHLOOTshort = dfPlaceholrers
        if inputs["useHLOOT"]:
            isHLOOTlong = hloot_long_entry
            isHLOOTshort = hloot_short_entry
        isUseEMAlong = dfPlaceholrers
        isUseEMAshort = dfPlaceholrers
        if inputs["useEma"]:
            isUseEMAlong = ema_long_entry
            ema_coord = emaout
            isUseEMAshort = ema_short_entry
        isUseSMAlong = dfPlaceholrers
        isUseSMAshort = dfPlaceholrers
        if inputs["useSma"]:
            isUseSMAlong = sma_long_entry
            smaout_coord = smaout
            isUseSMAshort = sma_short_entry
        isSUPERTRENDlong = dfPlaceholrers
        isSUPERTRENDshort = dfPlaceholrers
        if inputs["useSUPERTREND"]:
            isSUPERTRENDlong = super_long_entry
            isSUPERTRENDshort = super_short_entry
            super_coord_long = super_coord_long
            super_coord_short = super_coord_short
        isZEROlong = dfPlaceholrers
        isZEROshort = dfPlaceholrers
        if inputs["useZeroLag"]:
            isZEROlong = zerolag_long_entry
            isZEROshort = zerolag_short_entry
            zerocoord_fast = zero_coord_fast
            zerocoord_slow = zero_coord_slow
        isRTIlong = dfPlaceholrers
        isRTIshort = dfPlaceholrers
        if inputs["useRTI"]:
            isRTIlong = rti_long_entry
            isRTIshort = rti_short_entry
        isAOLong = dfPlaceholrers
        isAOShort = dfPlaceholrers
        if inputs["enableAO"]:
            isAOLong = ao_long_entry
            isAOShort = ao_short_entry
        isHeikenLong = dfPlaceholrers
        isHeikenShort = dfPlaceholrers
        if inputs["enableHeikenAshi"]:
            isHeikenLong = heiken_long_entry
            isHeikenShort = heiken_short_entry
        
        # h.logger.info(f"isVSLRTlong LC {isVSLRTlong}")
        # reverseActive = False
        # if useReverseOrderHLOOT and reversedHOOTentry and isHLOOTlong and reverseActive == False:
        #     reverseActive = True
        #     isHLOOTlong = False
        #     isHLOOTshort = True

        # if useReverseOrderHLOOT and reversedHOOTentry and isHLOOTshort and reverseActive == False:
        #     reverseActive = True
        #     isHLOOTshort = False
        #     isHLOOTlong = True

        # print(len(isVSLRTlong))
        df['long_entry'] = [all(values) for values in zip(isLorennzianLong, isVSLRTlong, isHLOOTlong, isUseEMAlong, isUseSMAlong, isSUPERTRENDlong, isZEROlong, isRTIlong, isAOLong, isHeikenLong)]
        df['short_entry'] = [all(values) for values in zip(isLorennzianShort, isVSLRTshort, isHLOOTshort, isUseEMAshort, isUseSMAshort, isSUPERTRENDshort, isZEROshort, isRTIshort, isAOShort, isHeikenShort)]

        # if useHLOOT:
        return {
            "trained_source": trainedSourceOutput,
            "long_entry": df['long_entry'], 
            "short_entry": df['short_entry'],
            "high_HLOOT": hoot,
            "low_HLOOT": loot,
            "ema_coord": ema_coord,
            "sma_coord": smaout_coord,
            "super_coord_long": super_coord_long,
            "super_coord_short": super_coord_short,
            "zerocoord_fast": zerocoord_fast,
            "zerocoord_slow": zerocoord_slow,
        }
        
        # return df['long_entry'], df['short_entry']
    except Exception as e:
        h.logger.warning(f"issue LC {e}")
    # long_entry = isVSLRTlong
    # short_entry = isVSLRTshort
