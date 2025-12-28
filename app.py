import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# Sahifa sozlamalari
st.set_page_config(page_title="Pro Trader Journal", layout="wide")

# Ma'lumotlar bazasi
conn = sqlite3.connect('trade_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS trades (id INTEGER PRIMARY KEY, date TEXT, pair TEXT, type TEXT, amount REAL)')
conn.commit()

# --- SIDEBAR (KIRITISH) ---
st.sidebar.header("📊 Yangi Trade")
pair = st.sidebar.text_input("Instrument (masalan: BTCUSDT)").upper()
amount = st.sidebar.number_input("Profit/Loss ($)", min_value=0.0, step=10.0)
type_trade = st.sidebar.selectbox("Natija", ["TAKE PROFIT", "STOP LOSS"])

if st.sidebar.button("Saqlash"):
    val = amount if type_trade == "TAKE PROFIT" else -amount
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    c.execute("INSERT INTO trades (date, pair, type, amount) VALUES (?, ?, ?, ?)", (date, pair, type_trade, val))
    conn.commit()
    st.sidebar.success("Saqlandi!")

# --- ASOSIY PANEL ---
st.title("🚀 AI Trade Dashboard")

# Ma'lumotlarni o'qish
df = pd.read_sql_query("SELECT * FROM trades", conn)

if not df.empty:
    # Hisob-kitoblar
    initial_balance = 1000.0
    df['cumulative_profit'] = df['amount'].cumsum()
    df['balance'] = initial_balance + df['cumulative_profit']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Joriy Balans", f"${df['balance'].iloc[-1]:.2f}", f"{df['cumulative_profit'].iloc[-1]:.2f}$")
    
    wins = len(df[df['type'] == 'TAKE PROFIT'])
    win_rate = (wins / len(df)) * 100
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Jami Tradelar", len(df))

    # GRAFIK (Interaktiv)
    st.subheader("📈 Hisob o'sish grafigi (Equity Curve)")
    fig = px.line(df, x=df.index, y='balance', markers=True, 
                  template="plotly_dark", color_discrete_sequence=['#00e676'])
    st.plotly_chart(fig, use_container_width=True)

    # JADVAL
    st.subheader("📜 Savdolar tarixi")
    st.dataframe(df[['date', 'pair', 'type', 'amount']].sort_index(ascending=False), use_container_width=True)
else:
    st.info("Hali tradelar mavjud emas. Sidebar orqali birinchi tradeni qo'shing.")

# Ma'lumotni tozalash
if st.sidebar.button("Barcha ma'lumotlarni o'chirish"):
    c.execute("DELETE FROM trades")
    conn.commit()
    st.rerun()