import pyupbit
import numpy as np
import pandas as pd
import time
import pandas as pd

#dfs = []
df= pyupbit.get_ohlcv("KRW-ETH",interval="minute60", count=200)
#dfs.append(df)
'''
for i in range(12):
    df= pyupbit.get_ohlcv("KRW-ETH",interval="minute60", to=df.index[0])
    dfs.append(df)
    time.sleep(0.2)
'''
#df = pd.concat(dfs)
#df = df.sort_index()

#OHLCV(open,high,low,close,volume)
#df = pyupbit.get_ohlcv("KRW-ETH",interval="minute60", count=200) 
#range 구하기(고가-저가)
df['range'] = (df['high']-df['low'])*0.1
#target(매수가), range 컬럼을 한칸씩 밑으로 내림(.shift(1))
df['target_price'] = round(df['open'] + df['range'].shift(1),-3)
#다음날 시가
df['tomorrow_open'] = df['open'].shift(-1)
#5일 이평선
df['ma5'] = df['close'].rolling(5).mean()
#10일 이평선
df['ma10'] = df['close'].rolling(10).mean()
#15일 이평선
df['ma15'] = df['close'].rolling(15).mean()
#null 삭제 하기
df=df[df['ma15'].notnull()]

#조건 만족했는지 확인
cond = ((df['high']>df['target_price']) & (df['high']>df['ma15']))
#수익률
df['ror'] = df.loc[cond,'tomorrow_open']/df.loc[cond,'target_price']
#누적 수익률
df['hpr'] = df['ror'].cumprod()
#print(hpr.iloc[-1])
df.loc[cond].to_excel("backtesting.xlsx")

