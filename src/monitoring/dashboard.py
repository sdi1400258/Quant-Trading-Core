import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from datetime import datetime

# Set page config
st.set_page_config(page_title="Trading Analytics", layout="wide")

st.title("Algorithmic Trading Analytics Dashboard")

# Paths
MONITORING_DIR = "monitoring"
EQUITY_CURVE_PATH = os.path.join(MONITORING_DIR, "equity_curve.csv")
TRADES_LOG_PATH = os.path.join(MONITORING_DIR, "trade_audit_trail.csv")

def load_data():
    if not os.path.exists(EQUITY_CURVE_PATH) or not os.path.exists(TRADES_LOG_PATH):
        st.error("Monitoring data not found. Please run the trading pipeline first (main.py).")
        return None, None
    
    equity_df = pd.read_csv(EQUITY_CURVE_PATH)
    equity_df['Date'] = pd.to_datetime(equity_df['Date'])
    
    trades_df = pd.read_csv(TRADES_LOG_PATH)
    trades_df['Date'] = pd.to_datetime(trades_df['Date'])
    
    return equity_df, trades_df

equity_df, trades_df = load_data()

if equity_df is not None:
    # --- Sidebar Metrics ---
    st.sidebar.header("Strategy Performance")
    
    initial_capital = equity_df['Equity'].iloc[0]
    final_capital = equity_df['Equity'].iloc[-1]
    total_return = (final_capital / initial_capital) - 1
    
    st.sidebar.metric("Total Return", f"{total_return:.2%}")
    st.sidebar.metric("Final Equity", f"${final_capital:,.2f}")
    st.sidebar.metric("Trade Count", len(trades_df))
    
    # --- Main Dashboard ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Equity Curve")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=equity_df['Date'], y=equity_df['Equity'], mode='lines', name='Equity'))
        fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Asset Distribution (Value-Based)")
        # Calculate position market value using the most recent trade price
        last_trades = trades_df.sort_values('Date').groupby('Symbol').last().reset_index()
        # Simplified market value representation
        last_trades['Market_Value'] = last_trades['Qty'] * last_trades['Price']
        
        # Only show symbols with significant long positions
        active_holdings = last_trades[last_trades['Qty'] > 0.001]
        
        if not active_holdings.empty:
            fig_pie = px.pie(active_holdings, values='Market_Value', names='Symbol', title='Portfolio Weighting')
            fig_pie.update_layout(template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.write("No active holdings.")

    # --- Trade Table ---
    st.subheader("Trade History")
    st.dataframe(trades_df.sort_values('Date', ascending=False), use_container_width=True)

    # --- Detailed Analysis ---
    st.subheader("Profit/Loss per Trade")
    # Simple estimate of realized PnL per trade pair could go here
    st.info("Additional analytics can be reached by expanding this section.")
    
    with st.expander("Raw Data View"):
        st.write("Equity Curve Data")
        st.dataframe(equity_df.tail())

else:
    st.info("Run the pipeline to see analytics.")
