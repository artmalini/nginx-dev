import matplotlib.pyplot as plt
# import mplfinance as mpf
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"
import pandas as pd
from strategies.lorenzianClassification.lorenzianClassification import lC
from strategies.dms.directionalMovementIndexStrategy import directionalMovement
from trackBenefits import trackBenefits
import helpers as h
import json

class visualGraph :
    def __init__(self, source, trainedSource):
        self.klines = source
        self.trainedSource = trainedSource
        self.setTrainedSouce(trainedSource)

        self.trainedSource = {
            "lorenzian": {
                "trained": False,
                "long_signal": None,
                "short_signal": None,
                "high": None,
                "low": None,
                "close": None,
                "pineRma": None,
                "pineRma1": None,
                "adxRma": None,
                "adxDX": None,
                "closeU": None,
                "closeD": None,
                "closeU1": None,
                "closeD1": None,  
                "closeRsi": None,
                "closeRsi1": None,
                "nwtCi": None,
                "hlc3Ci": None,
                "resultCCI": None,
                "historicMin": None,
                "historicMax": None,
                "historicMinCCI": None,
                "historicMaxCCI": None,
                "trSmooth": None,
                "smoothDirectionalMovementPlus": None,
                "smoothnegMovement": None,
                "y_train_series": None,
                "y_train_array": None,
                "distances": None,
                "predictions": None,
                "prediction": None
            },
            "vslrt": {
                "trained": False,
                "long_signal": None,
                "short_signal": None,
                "slope_price": None,
                "slope_price_lt": None,
                "slope_volume_up": None,
                "slope_volume_down": None,
                "slope_volume_up_lt": None,
                "slope_volume_down_lt": None
            },
            "hloot": {
                "trained": False,
                "long_signal": None,
                "short_signal": None,
                "longStop": None,
                "shortStop": None,
                "dir": None,
                "longStopl": None,
                "shortStopl": None,
                "dirl": None,
                "hoot": None,
                "loot": None,
                "vud1": None,
                "vdd1": None,
                "vud1l": None,
                "vdd1l": None
            }
        }
        self.jsonTrainedSource = None

    def setTrainedSouce(self, existedTrasinedSource):
        # TO DO it should switch to mainTrainer
        return
        self.trainedSource = existedTrasinedSource

    def buildChart(self):
        # Convert 'close_datetime' column to datetime type
        try:
            if 'close_datetime' in self.klines.columns:

                if all(col in self.klines.columns for col in ['open', 'high', 'low', 'close']):

                    # self.klines['close_datetime'] = pd.to_datetime(self.klines['close_datetime'])
                    # trace = go.Candlestick(x=self.klines['close_datetime'],
                    #                     open=self.klines['open'],
                    #                     high=self.klines['high'],
                    #                     low=self.klines['low'],
                    #                     close=self.klines['close'])

                    # fig = go.Figure(data=[trace])
                    # fig.update_layout(xaxis_rangeslider_visible=False)
                    # fig.update_layout(title='BTCUSDT Candlestick Chart', xaxis_title='Date', yaxis_title='Price')
                    # fig.show()
                    # 
                    # 
                    # --------------------------------------------

                    # Convert data to DataFrame
                    df = pd.DataFrame(self.klines)
                    df['close_datetime'] = pd.to_datetime(df['close_datetime'])
                    df.set_index('close_datetime', inplace=True)
                    # Calculate long and short entry points
                    lorenzian = lC(df, self.trainedSource)
                    self.trainedSource.update(lorenzian["trained_source"])

                    self.jsonTrainedSource = json.dumps(self.trainedSource, default=str)

                    # h.logger.info(f"Long entry {long_entry}")
                    # return
                    # h.logger.info(f"DF {df}")
                    
                    # long_entry, short_entry = directionalMovement(df)
                    # h.logger.info(f"{long_entry}")
                    #  return
                
                    # Track current position
                    current_position = None

                    # Create lists to store entry points
                    long_entry_points = []
                    short_entry_points = []

                    # Loop through signals and determine entry points based on current position
                    for i in range(len(df)):
                        if lorenzian["long_entry"][i]:
                            if current_position != 'long':
                                long_entry_points.append(i)
                                current_position = 'long'
                        elif lorenzian["short_entry"][i]:
                            if current_position != 'short':
                                short_entry_points.append(i)
                                current_position = 'short'

                    # Convert entry points indices to DatetimeIndex
                    long_entry_points = df.iloc[long_entry_points].index
                    short_entry_points = df.iloc[short_entry_points].index
                    
                    # Create Candlestick trace
                    candlestick_trace = go.Candlestick(
                        x=df.index,
                        open=df['open'],
                        high=df['high'],
                        low=df['low'],
                        close=df['close'],
                        name='Candlestick'
                    )

                    # Create long entry points trace
                    long_entry_points_trace = go.Scatter(
                        x=long_entry_points,
                        y=df.loc[long_entry_points, 'low'] - 20,  # Adjust the y position for better visualization
                        mode='markers',
                        marker=dict(color='green', size=10, symbol='triangle-up'),
                        name='Long Entry'
                    )

                    # Create short entry points trace
                    short_entry_points_trace = go.Scatter(
                        x=short_entry_points,
                        y=df.loc[short_entry_points, 'high'] + 20,  # Adjust the y position for better visualization
                        mode='markers',
                        marker=dict(color='red', size=10, symbol='triangle-down'),
                        name='Short Entry'
                    )

                    if len(lorenzian["high_HLOOT"]) > 3 and len(lorenzian["low_HLOOT"]) > 3:
                        hoot_2_trace = go.Scatter(
                            x=df.index,
                            y=[None] * 2 + lorenzian["high_HLOOT"][:-2],  # Assuming hoot[2] is a list of values corresponding to each index 
                            mode='lines',
                            line=dict(color='blue', width=1),   #  dash='dash'
                            name='Hoot[2]'
                        )

                        # Create loot[2] trace
                        loot_2_trace = go.Scatter(
                            x=df.index,
                            y=[None] * 2 + lorenzian["low_HLOOT"][:-2],  # Assuming loot[2] is a list of values corresponding to each index
                            mode='lines',
                            line=dict(color='red', width=1),
                            name='Loot[2]'
                        )

                    if len(lorenzian["ema_coord"]) > 3 : 
                        ema_long_trace = go.Scatter(
                            x=df.index,
                            y=lorenzian["ema_coord"], 
                            mode='lines',
                            line=dict(color='#64c53c', width=2), # light green
                            name='ema coord'
                        )

                    if len(lorenzian["sma_coord"]) > 3 : 
                        sma_long_trace = go.Scatter(
                            x=df.index,
                            y=lorenzian["sma_coord"], 
                            mode='lines',
                            line=dict(color='#19e316', width=2), # light green
                            name='sma coord'
                        )

                    if len(lorenzian["super_coord_long"]) > 3 :
                        super_long_trace = go.Scatter(
                            x=df.index,
                            y=lorenzian["super_coord_long"], 
                            mode='lines',
                            line=dict(color='#19e316', width=2), # light green
                            name='Supertrend Long'
                        )

                    if len(lorenzian["super_coord_short"]) > 3 :
                        super_short_trace = go.Scatter(
                            x=df.index,
                            y=lorenzian["super_coord_short"], 
                            mode='lines',
                            line=dict(color='blue', width=2), # blue
                            name='Supertrend Short'
                        )

                    if len(lorenzian["zerocoord_fast"]) > 3 :
                        zero_long_trace = go.Scatter(
                            x=df.index,
                            y=lorenzian["zerocoord_fast"], 
                            mode='lines',
                            line=dict(color='purple', width=1), # purple
                            name='Zero coord Fast'
                        )

                    if len(lorenzian["zerocoord_slow"]) > 3 :
                        zero_short_trace = go.Scatter(
                            x=df.index,
                            y=lorenzian["zerocoord_slow"], 
                            mode='lines',
                            line=dict(color='gray', width=1),
                            name='Zero coord Slow'
                        ) 

                    # Create figure with Candlestick, long entry, and short entry traces
                    dataObjects = [candlestick_trace, long_entry_points_trace, short_entry_points_trace]

                    if len(lorenzian["high_HLOOT"]) > 3 and len(lorenzian["low_HLOOT"]) > 3:
                        dataObjects.append(hoot_2_trace)
                        dataObjects.append(loot_2_trace)

                    if len(lorenzian["ema_coord"]) > 3 :
                        dataObjects.append(ema_long_trace)
                    if len(lorenzian["sma_coord"]) > 3 :
                        dataObjects.append(sma_long_trace)
                    if len(lorenzian["super_coord_long"]) > 3 :
                        dataObjects.append(super_long_trace)
                    if len(lorenzian["super_coord_short"]) > 3 :
                        dataObjects.append(super_short_trace)
                    if len(lorenzian["zerocoord_fast"]) > 3 :
                        dataObjects.append(zero_long_trace)
                    if len(lorenzian["zerocoord_slow"]) > 3 :
                        dataObjects.append(zero_short_trace)

                    fig = go.Figure(data=dataObjects)

                    # Update layout
                    fig.update_layout(
                        title='BTCUSDT Candlestick Chart with DMI Long/Short Entries',
                        xaxis_title='Date',
                        yaxis_title='Price'
                    )
                    fig.update_layout(xaxis_rangeslider_visible=False)

                    # Show the plot with WebGL rendering
                    # fig.show()


                    trackBenefits(lorenzian["long_entry"], lorenzian["short_entry"], df, 1000)

            else:
                print("Column 'close_datetime' not found in DataFrame.")
        except Exception as e:
            print("An error occurred in process:", str(e))


    def start(self):
        self.buildChart()
        return self.jsonTrainedSource