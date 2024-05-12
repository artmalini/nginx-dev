from indicators.vslrt import vslrt
from indicators.hloot import hloot
from indicators.ema import ema
from indicators.sma import sma
from indicators.supertrend import supertrend
from indicators.zerolag import zerolag
from indicators.rti import rti
import plotly.graph_objects as go
import pandas as pd
import helpers as h

def lC(df):
    # Inputs
    inputs = {
        "dateRange": False,
        "source": df['open'],
        "neighborsCount": 8,
        "maxBarsBack": 2000,
        "featureCount": 5,
        "useVSLRT": False,
        "useHLOOT": False,
        "useEma": False,
        "useSma": False,
        "useSUPERTREND": False,
        "useZeroLag": False,
        "useRTI": True,   
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
    zerolag_long_entry = [0.0] * 2
    zerolag_short_entry = [0.0] * 2
    zerocoord_fast = [0.0] * 2
    zerocoord_slow = [0.0] * 2

    # ==== Relative Trend Index (RTI) by Zeiierman ====
    rti_long_entry = [0.0] * 2
    rti_short_entry = [0.0] * 2

    useReverseOrder = False

    if inputs["useVSLRT"]:
        vslrt_long_entry, vslrt_short_entry = vslrt(df, inputs["source"], inputs["vslrtLen1"], inputs["vslrtLen2"])
    if inputs["useHLOOT"]:
        hloot_long_entry, hloot_short_entry, hoot, loot = hloot(df, inputs["hlooSource"], inputs["hlootLength"], inputs["hlootPercent"], inputs["hlootHllength"], inputs["hlootMav"], inputs["useReverseOrderHLOOT"])
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
        df['long_entry'] = [all(values) for values in zip(isVSLRTlong, isHLOOTlong, isUseEMAlong, isUseSMAlong, isSUPERTRENDlong, isZEROlong, isRTIlong)]
        df['short_entry'] = [all(values) for values in zip(isVSLRTshort, isHLOOTshort, isUseEMAshort, isUseSMAshort, isSUPERTRENDshort, isZEROshort, isRTIshort)]

        # if useHLOOT:
        return {
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
