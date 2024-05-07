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

class visualGraph :
    def __init__(self, source):
        self.klines = source

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
                    lorenzian = lC(df)
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

                    # Create figure with Candlestick, long entry, and short entry traces
                    dataObjects = [candlestick_trace, long_entry_points_trace, short_entry_points_trace]

                    if len(lorenzian["high_HLOOT"]) > 3 and len(lorenzian["low_HLOOT"]) > 3:
                        dataObjects.append(hoot_2_trace)
                        dataObjects.append(loot_2_trace)

                    if len(lorenzian["ema_coord"]) > 3 :
                        dataObjects.append(ema_long_trace)
                    if len(lorenzian["sma_coord"]) > 3 :
                        dataObjects.append(sma_long_trace)

                    fig = go.Figure(data=dataObjects)

                    # Update layout
                    fig.update_layout(
                        title='BTCUSDT Candlestick Chart with DMI Long/Short Entries',
                        xaxis_title='Date',
                        yaxis_title='Price'
                    )
                    fig.update_layout(xaxis_rangeslider_visible=False)

                    # Show the plot with WebGL rendering
                    fig.show()


                    trackBenefits(lorenzian["long_entry"], lorenzian["short_entry"], df, 1000)

            else:
                print("Column 'close_datetime' not found in DataFrame.")
        except Exception as e:
            print("An error occurred in process:", str(e))


    def start(self):
        self.buildChart()
        return