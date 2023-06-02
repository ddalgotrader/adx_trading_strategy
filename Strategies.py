import pandas as pd 
import numpy as np
import talib as ta


def sma(data, freq,window, plot_data={1:[('SMA',None, 'red')]}):
    
    df=data.copy()
    
    freq = f"{freq}min"
    df = df.resample(freq).agg({"Open": "first", "High": "max", "Low": "min", "Close": "last",  'spread':'mean','pips':'mean'}).dropna()
        
    df["returns"] = np.log(df['Close'] / df['Close'].shift(1))
    df['position']=np.nan
    df['SMA']=df['Close'].rolling(window=window).mean()
    first_cross_idx=df.index[0]
    df['Close_shifted']=df['Close'].shift(1)
    
    for i in range(len(df)):
        condition1_one_bar=((df['Open'].iloc[i]<df['SMA'].iloc[i]) & (df['Close'].iloc[i]>df['SMA'].iloc[i]))
        condition2_one_bar=((df['Open'].iloc[i]>df['SMA'].iloc[i]) & (df['Close'].iloc[i]<df['SMA'].iloc[i]))
        condition1_two_bars=((df['Close_shifted'].iloc[i]>df['SMA'].iloc[i]) & (df['Close'].iloc[i]<df['SMA'].iloc[i]))
        condition2_two_bars=((df['Close_shifted'].iloc[i]<df['SMA'].iloc[i]) & (df['Close'].iloc[i]>df['SMA'].iloc[i]))
        
           
        if condition1_one_bar or condition1_two_bars or condition2_one_bar or condition2_two_bars:
            
            first_cross_idx=df.index[i]
            break
            
    conditions=[
    (df['Close']>df['SMA']) & (df.index>=first_cross_idx),
    (df['Close']<df['SMA']) & (df.index>=first_cross_idx),
    ]
    values=[1,-1]
    df["position"] = np.select(conditions, values,0)
    
    
    
    df.dropna(inplace = True)
    
    return df

def adx(data , freq=14, window=20, down_level=25, plot_data={2:[('plus_di',None, 'green'),('minus_di',None,'red'),               ('adx','down_level', 'blue')]}):

        ''' Prepares the Data for Backtesting.
        '''
        df = data.copy()

        freq = f"{freq}min"

        df = df.resample(freq).agg({"Open": "first", "High": "max", "Low": "min", "Close": "last", "vol": "sum", 'spread':'mean','pips':'mean'}).dropna()

        df["returns"] = np.log(df['Close'] / df['Close'].shift(1))

        df['adx']=ta.ADX(df['High'],df['Low'], df['Close'], window)
        df['plus_di']=ta.PLUS_DI(df['High'],df['Low'], df['Close'], window)
        df['minus_di']=ta.MINUS_DI(df['High'],df['Low'], df['Close'], window)
        df['plus_di_shift']=df['plus_di'].shift(1)
        df['minus_di_shift']=df['minus_di'].shift(1)

        conditions=[ (df['plus_di']>df['minus_di']) & (df['adx']>down_level),
                     (df['minus_di']>df['plus_di']) & (df['adx']>down_level)]

        values=[1,-1]

        df['position']=np.select(conditions,values,0)

        df.dropna(inplace = True)


        return df