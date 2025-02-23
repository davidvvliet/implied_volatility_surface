import sys
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from scipy.stats import norm
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
import plotly.graph_objects as go
from datetime import datetime, date

st.title("Implied Volatility Surface")


# def black_scholes(p, S, K, T, r):
#     d1 = (np.log(S / K) + (r + 0.5 * sig**2) * T) / (sig * np.sqrt(T))
#     d2 = d1 - sig * np.sqrt(T)
#     return S * norm.cdata(d1) - K * np.exp(-r * T) * norm.cdata(d2)
    

def plot(data):

    xi = np.linspace(data['Days To Expiration'].min(), data['Days To Expiration'].max(), 250)
    yi = np.linspace(data['Strike'].min(), data['Strike'].max(), 250)
    # xi = np.unique(data['Days To Expiration'])
    # yi = np.unique(data['Strike'])

    X, Y = np.meshgrid(xi, yi)

    Z = griddata((data['Days To Expiration'], data['Strike']), data['Implied Vol'], (X, Y), method='cubic')
    Z = np.clip(Z, data['Implied Vol'].min(), data['Implied Vol'].max())

    # fig = plt.figure(figsize=(8, 6))
    # ax = fig.add_subplot(111, projection='3d')

    # ax.plot_surface(X, Y, Z, cmap='viridis')

    
    # # Z = gaussian_filter(data['Implied Vol'], sigma=0.5)
    # # fig = plt.figure(figsize=(8, 6))
    # # ax = fig.add_subplot(111, projection='3d')

    # # ax.plot_trisurf(data['Days To Expiration'], data['Strike'], Z, cmap='viridis')

    # ax.set_xlabel('Days To Expiration')
    # ax.set_ylabel('Strike')
    # ax.set_zlabel('Implied Vol')


    # st.pyplot(fig, clear_figure=True)

    fig = go.Figure()

    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='RdYlGn'))

    fig.update_layout(
        scene=dict(
            xaxis_title='Days To Expiration',
            yaxis_title='Strike',
            zaxis_title='Implied Vol'
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        title="Implied Volatility Surface"
    )

    st.plotly_chart(fig)
    

def gen_surface(ticker):
    asset = yf.Ticker(ticker)

    if not asset.options:
        st.error("Please enter a valid stock ticker")
        return
    expDates = asset.options



    today = date.today()
    callData = []
    putData = []
    # iterate through each expiration date
    for exp in expDates:
        #obtain the options chain for that expiry date
        # print(exp)
        expDate = datetime.strptime(exp, "%Y-%m-%d").date()
        daysToExp = (expDate - today).days

        oChain = asset.option_chain(exp)

        calls = oChain.calls
        puts = oChain.puts

        for i in range(len(calls.strike)):
            callData.append([daysToExp, calls.strike[i], calls.impliedVolatility[i]])

    data = pd.DataFrame(callData, columns=["Days To Expiration", "Strike", "Implied Vol"])
    try: 
        plot(data)
    except:
        return

def fe():

    # args = sys.argv
    ticker = st.text_input("Please enter a stock ticker")
    if ticker:
        print(ticker)
        gen_surface(ticker)

fe()