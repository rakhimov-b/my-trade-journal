import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px  # Grafiklar uchun
from datetime import datetime

st.set_page_config(page_title="Pro Trading Dashboard", layout="wide")

st.title("🚀 Smart Trade Journal v2.0")

# Google Sheets ulanishi
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl="0")

if not df.empty:
    # Ma'lumotlarni tayyorlash
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['cumulative_profit'] = df['amount'].cumsum()

    # Tepadagi asosiy ko'rsatkichlar (Cards)
    col1, col2, col3, col4 = st.columns(4)
    total_pnl = df['amount'].sum()
    win_rate = (len(df[df['type'] == 'TAKE PROFIT']) / len(df)) * 100
    
    col1.metric("Umumiy PnL", f"${total_pnl:,.2f}", delta=f"{total_pnl:,.2f}")
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Jami Savdolar", len(df))
    col4.metric("Eng katta foyda", f"${df['amount'].max():,.2f}")

    # Grafiklar bo'limi
    st.markdown("---")
    g1, g2 = st.columns([2, 1])

    with g1:
        st.subheader("Balans o'sishi")
        fig_line = px.line(df, x='date', y='cumulative_profit', title="Equity Curve")
        st.plotly_chart(fig_line, use_container_width=True)

    with g2:
        st.subheader("Natijalar ulushi")
        fig_pie = px.pie(df, names='type', color='type', 
                         color_discrete_map={'TAKE PROFIT':'#00CC96', 'STOP LOSS':'#EF553B'})
        st.plotly_chart(fig_pie, use_container_width=True)

# Sidebar (O'zgarishsiz qoladi)
st.sidebar.header("Yangi Trade")
# ... (avvalgi inputlar koda shu yerda davom etadi)
