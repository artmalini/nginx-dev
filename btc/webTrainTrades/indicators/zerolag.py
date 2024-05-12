# from indicators.libmath import l_ema
import helpers as h

def z_ema(df, index, source, length):
    ema_values = []
    try:
        if not df.empty and length:
            alpha = 2 / (length + 1)
            
            for i in range(length):
                idx = index - length + i + 1
                if idx <= 0:
                    ema_values.append(df[source].iloc[0])  # First value is same as source
                elif i == 0:
                    ema_values.append(df[source].iloc[idx])
                else:
                    previous_ema = ema_values[-1]
                    current_value = df[source].iloc[idx]
                    ema = alpha * current_value + (1 - alpha) * previous_ema
                    ema_values.append(ema)

            return ema_values
    except Exception as e:
        h.logger.warning(f'z_ema {e} {ema_values} lenDf {len(df)} idx {idx}')
        return ema_values
    
def zsmall_ema(source, length):
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
        h.logger.warning(f'zsmall_ema {e} {ema_values}')
        return ema_values

def zlagtema(df, index, srcin, len):
    try:
        ema1 = z_ema(df, index, srcin, len)
        ema2 = zsmall_ema(ema1, len)
        ema3 = zsmall_ema(ema2, len)
        out = [3 * (ema1[idx] - ema2[idx]) + ema3[idx] for idx in range(len)]
        ema1a = zsmall_ema(out, len)
        ema2a = zsmall_ema(ema1a, len)
        ema3a = zsmall_ema(ema2a, len)
        outf = [3 * (ema1a[idx] - ema2a[idx]) + ema3a[idx] for idx in range(len)]

        # h.logger.info(f"outf[-1]: {outf[-1]} outf[-2] {outf[-2]} outf: {outf}")
        return outf
    except Exception as e:
        h.logger.warning(f'zlagtema {e} index {index}')
    return [0] * len

def zerolag(df, useExitCrossZeroLag, useEntryAboveBelowZeroLag, smthtype, srcin, inpPeriodFast, inpPeriodSlow):
    long_signal = []
    short_signal = []
    zerocoord_fast = []
    zerocoord_slow = []
    
    kfl = 0.666
    ksl = 0.0645
    amafl = 2
    amasl = 30
    t3hot = 0.7
    t3swt = "T3 New"
    try:
        if not df.empty:
            # emaout = l_ema(df, source, emalen)
            haclose = [0,0]
            haopen = [0,0]
            for index in range(len(df)):
                # if index > 0 :
                haclose = [(df["open"].iloc[index] + df["high"].iloc[index] + df["low"].iloc[index] + df["close"].iloc[index]) / 4] + haclose[:-1]
                if haopen[1] == 0:
                    haopen = [(df["open"].iloc[index] + df["close"].iloc[index]) / 2] + haopen[:-1]
                if haopen[1] != 0: 
                    haopen = [(haopen[1] + haclose[1] / 2)] + haopen[:-1]

                hahigh = max(df["high"].iloc[index], max(haopen[0], haclose[0]))
                halow = min(df["low"].iloc[index],  min(haopen[0], haclose[0]))
                hamedian = (hahigh + halow) / 2
                hatypical = (hahigh + halow + haclose[0]) / 3
                haweighted =  (hahigh + halow + haclose[0] + haclose[0]) / 4 
                haaverage =  (haopen[0] + hahigh + halow + haclose[0]) / 4

                temafast = zlagtema(df, index, srcin, inpPeriodFast)
                temaslow = zlagtema(df, index, srcin, inpPeriodSlow)

                
                goLongZig = temafast[-2] < temaslow[-2] and temafast[-1] > temaslow[-1]
                goShortZig = temafast[-2] > temaslow[-2] and temafast[-1] < temaslow[-1]

                # h.logger.info(f"temafast[-1]: {temafast[-1]} temaslow[-2]: {temaslow[-2]}")
                # h.logger.info(f"goLongZig: {goLongZig} goShortZig: {goShortZig}")
                # if index == 0 :
                #     break
                
                zerocoord_fast.append(temafast[-1])
                zerocoord_slow.append(temaslow[-1])

                long_signal.append(goLongZig)
                short_signal.append(goShortZig)
        
    except Exception as e:
         h.logger.warning(f'ZeroLag {e}')

    # h.logger.info(f'ZeroLag short_signal {short_signal}')
    # h.logger.info(f'zerocoord_fast {zerocoord_fast}')
    return long_signal, short_signal, zerocoord_fast, zerocoord_slow