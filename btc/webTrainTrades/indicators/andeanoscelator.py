import math
import helpers as h

def ao_ema(source, length):
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
        h.logger.warning(f'ao_ema {e} {ema_values}')
        return ema_values

def andeanoscelator(df, lengthAO, sigLengthAO):
    long_signal = []
    short_signal = []
    
    try:
        if not df.empty:
            alphaAO = 2 / (lengthAO + 1)
            up1 = [0] * 2
            up2 = [0] * 2
            dn1 = [0] * 2
            dn2 = [0] * 2
            bullAO = [0] * sigLengthAO
            bearAO = [0] * sigLengthAO
            signalAO = [0]

            for index in range(len(df)):
                CAO = df["close"].iloc[index]
                OAO = df["open"].iloc[index]
                
                if up1[0] == 0:
                    up1 = [CAO] + up1[:-1]
                if up1[0] != 0:
                    up1 = [max(CAO, OAO, up1[1] - (up1[1] - CAO) * alphaAO), CAO] + up1[:-1]
                if up2[0] == 0:
                    up2 = [CAO * CAO] + up2[:-1]
                if up2[0] != 0:
                    up2 = [max(CAO * CAO, OAO * OAO, up2[1] - (up2[1] - CAO * CAO) * alphaAO)] + up2[:-1]

                if dn1[0] == 0:
                    dn1 = [CAO] + dn1[:-1]
                if dn1[0] != 0:
                    dn1 = [min(CAO, OAO, dn1[1] + (CAO - dn1[1]) * alphaAO)] + dn1[:-1]
                if dn2[0] == 0:
                    dn2 = [CAO * CAO] + dn2[:-1]
                if dn2[0] != 0:
                    dn2 = [min(CAO * CAO, OAO * OAO, dn2[1] + (CAO * CAO - dn2[1]) * alphaAO)] + dn2[:-1]

                bullAO = [math.sqrt(dn2[0] - dn1[0] * dn1[0])] + bullAO[:-1]
                bearAO = [math.sqrt(up2[0] - up1[0] * up1[0])] + bearAO[:-1]

                signalBullishStronger = max(bullAO[0], bearAO[0]) == bullAO[0]
                if signalBullishStronger:
                    signalAO = ao_ema(bullAO, sigLengthAO)
                if signalBullishStronger == False:
                    signalAO = ao_ema(bearAO, sigLengthAO)

                isAOLong = bullAO[0] > signalAO[-1]
                isAOShort = bearAO[0] > signalAO[-1]

                long_signal.append(isAOLong)
                short_signal.append(isAOShort)
        
    except Exception as e:
         h.logger.warning(f'andeanoscelator {e}')

    h.logger.info(f"long {long_signal}")
    h.logger.info(f"short {short_signal}")
    return long_signal, short_signal