import pyupbit
import numpy as np
import pandas as pd
import time
import pandas as pd

my_money = 1000000
target_volatility = 2

dfs = []
df= pyupbit.get_ohlcv("KRW-ETH",interval="minute60", count=200)
dfs.append(df)

for i in range(12):
    df= pyupbit.get_ohlcv("KRW-ETH",interval="minute60", to=df.index[0])
    dfs.append(df)
    time.sleep(0.2)

df = pd.concat(dfs)
df = df.sort_index()

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

#RSI 구하기
def RSI(ticker, period, column='close'):

    df = pyupbit.get_ohlcv(ticker, interval="day", count=200)

    delta = df[column].diff(1)
    delta = delta.dropna()
    up = delta.copy()
    down = delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    df['up'] = up
    df['down'] = down
    df=df[df['up'].notnull()]
    #AVG_Gain = avg(df, period, column='up')
    #AVG_Loss = abs(avg(df, period, column='down'))
    df['AU'] = 0
    df['AD'] = 0
    #sma(Simple Moving Average:단순이동평균)
    #df['AU'] = df['up'].rolling(14).mean()
    #df['AD'] = np.abs(df['down'].rolling(14).mean())

    #ewma(Exponential Moving Average)
    df['AU'] = up.ewm(com=period -1 , min_periods=period).mean()
    df['AD'] = np.abs(down.ewm(com=period -1, min_periods=period).mean())

    df['RS'] = df['AU']/df['AD']
    df['RSI'] = 100.0 - (100.0 / (1.0 + df['RS']))

    return df['RSI']

df['RSI'] = RSI('KRW-ETH',14)

#조건 만족했는지 확인
cond = ((df['high']>df['target_price']) & (df['high']>df['ma15']))# & (df['RSI']>df['RSI'].shift(1)))
#수익률
df['ror'] = df.loc[cond,'tomorrow_open']/df.loc[cond,'target_price']
#누적 수익률
df['hpr'] = df['ror'].cumprod()
#print(hpr.iloc[-1])
df.loc[cond].to_excel("backtesting_ETH_1hrs.xlsx")
#전일 변동성%(전일고가-전일저가)/현재가
#df['volatility'] = df['range'].shift(1)/df['close']*100
#투자금비율 구하기
#df['invest_ratio'] = np.where(target_volatility<df['volatility'],
#                              round(target_volatility/df['volatility'],3),
#                              0.25)

#매수 진행 확인(매수=1)
#df['check'] = np.where((df['high'] > df['target_price']) & (df['open']>df['ma15']),
#                     1,
#                     0)


#df['sell_price'] = df['buy_price']*0.9995/df['target_price']*0.9995*df['close']
#df['buy_price'] = df['sell_price'].shift(1)

"""
if target_price < current_price and ma15 < current_price:   
                krw = get_balance("KRW")
                real_target = round(target_price,-3)
                total = (krw*0.9995)/real_target

df['new_range'] = (df['high'] - df['low'])*ma13_noise
#df['noise'] = (1-(abs(df['open']-df['close'])/(df['high'] - df['low'])))*0.1


df['new_target'] = df['open'] + df['new_range'].shift(1)

#ror(수익율), np.whare(조건문,참을때 값, 거짓을때 값)
df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'],
                     1)
df['new_ror'] = np.where(df['high'] > df['new_target'],
                     df['close'] / df['new_target'],
                     1)
#누적 곱 계산(cumpred) =>누적 수익률
df['hpr'] = df['ror'].cumprod()
df['new_hpr'] = df['new_ror'].cumprod()
#Draw Down 계산(누적 최대 값과 현재 hpr차이/누적 최대값*100)
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
df['new_dd'] = (df['new_hpr'].cummax() - df['new_hpr']) / df['new_hpr'].cummax() * 100
#MDD 계산
#print("MDD(%): ", df['dd'].max())
#print("NEW_MDD(%): ", df['new_dd'].max())

#print("누적 수익률: ",df['hpr'])
#print("new_누적 수익률: ",df['new_hpr'])
df.to_excel("testing_noise.xlsx")"""
