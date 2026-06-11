import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import numpy as np

# --- PAGE SETUP ---
st.set_page_config(page_title="Oracle Evaluation Panel", page_icon="📈", layout="wide")
st.title("📊 GT League Oracle - Advanced Evaluation Panel")
st.markdown("Analyzing every prediction as an independent single bet to isolate our mathematical edge.")

# --- DATABASE CONNECTION ---
@st.cache_resource(ttl=10)
def init_connection():
    DB_URL = "postgresql://postgres.wzziydbnbjpfoxxwevog:behumble250%40@aws-1-eu-north-1.pooler.supabase.com:6543/postgres"
    return psycopg2.connect(DB_URL)

conn = init_connection()

# --- LOAD DATA ---
@st.cache_data(ttl=10)
def load_data():
    query = "SELECT * FROM predictions ORDER BY kickoff_utc DESC;"
    return pd.read_sql(query, conn)

df = load_data()

if not df.empty:
    # Separate finished and active setups
    finished_df = df[df['status'].isin(['Won', 'Lost'])].copy()
    pending_df = df[df['status'] == 'Pending'].copy()
    
    # --- CONFIGURATION SIDEBAR ---
    st.sidebar.header("⚙️ Trading Strategy")
    stake_frw = st.sidebar.number_input("Stake per Single Bet (FRW)", min_value=1000, value=10000, step=1000)
    avg_odds = st.sidebar.number_input("Average Single Match Odds", min_value=1.01, value=1.05, step=0.01)
    
    if not finished_df.empty:
        # Sort oldest to newest to calculate streaks and cumulative math correctly
        finished_df = finished_df.sort_values(by='kickoff_utc', ascending=True)
        
        # Calculate single bet financial outcomes
        profit_per_win = stake_frw * (avg_odds - 1.0)
        finished_df['PnL'] = np.where(finished_df['status'] == 'Won', profit_per_win, -stake_frw)
        finished_df['Bankroll'] = finished_df['PnL'].cumsum()
        
        # --- COMPUTE ADVANCED METRICS FROM YOUR SKETCH ---
        total_singles = len(finished_df)
        total_won = len(finished_df[finished_df['status'] == 'Won'])
        overall_accuracy = (total_won / total_singles) * 100
        net_profit = finished_df['PnL'].sum()
        
        # 1. Longest Losing Streak
        # Create a series of 1s for losses and 0s for wins to count consecutive blocks
        is_loss = (finished_df['status'] == 'Lost').astype(int)
        longest_losing_streak = is_loss.groupby((is_loss != is_loss.shift()).cumsum()).cumsum().max()
        
        # 2. Hit rate of 80%+ picks
        high_conf_df = finished_df[finished_df['confidence'] >= 80.0]
        high_conf_total = len(high_conf_df)
        high_conf_won = len(high_conf_df[high_conf_df['status'] == 'Won'])
        high_conf_accuracy = (high_conf_won / high_conf_total * 100) if high_conf_total > 0 else 0.0
        
        # 3. Average Daily Profit
        finished_df['date'] = pd.to_datetime(finished_df['kickoff_utc']).dt.date
        daily_pnl = finished_df.groupby('date')['PnL'].sum()
        avg_daily_profit = daily_pnl.mean()

        # --- TOP LEVEL PERFORMANCE STATS ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Single Bets", total_singles)
        col2.metric("Overall Accuracy", f"{overall_accuracy:.1f}%")
        col3.metric("Longest Losing Streak", f"{longest_losing_streak} Bets")
        col4.metric("Net Profit / Loss", f"{net_profit:,.0f} FRW")
        
        st.divider()
        
        # --- ACCURACY BY CONFIDENCE BAND ---
        st.subheader("🎯 Accuracy & ROI by Confidence Band")
        
        # Define the ranges/bands
        bins = [0, 75, 80, 85, 100]
        labels = ['Under 75%', '75% - 80%', '80% - 85%', '85% - 100%']
        finished_df['Confidence_Band'] = pd.cut(finished_df['confidence'], bins=bins, labels=labels)
        
        band_stats = finished_df.groupby('Confidence_Band', observed=False).apply(
            lambda x: pd.Series({
                'Total Picks': len(x),
                'Won': len(x[x['status'] == 'Won']),
                'Accuracy': (len(x[x['status'] == 'Won']) / len(x) * 100) if len(x) > 0 else 0,
                'Total ROI %': (x['PnL'].sum() / (len(x) * stake_frw) * 100) if len(x) > 0 else 0
            })
        ).reset_index()
        
        band_col1, band_col2 = st.columns(2)
        with band_col1:
            fig_acc = px.bar(band_stats, x='Confidence_Band', y='Accuracy', text='Accuracy', 
                             title="Accuracy (%) per Confidence Level", color='Confidence_Band')
            fig_acc.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_acc, use_container_width=True)
            
        with band_col2:
            fig_roi = px.bar(band_stats, x='Confidence_Band', y='Total ROI %', text='Total ROI %',
                             title="Return on Investment (ROI %) per Confidence Level", color='Confidence_Band')
            fig_roi.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_roi, use_container_width=True)
            
        st.divider()

        # --- DYNAMIC COMPACT LEDGER VIEW ---
        st.subheader("📋 Independent Selection Stream")
        
        # Combine pending and finished back for chronological view, formatted newest first
        all_view_df = df.copy()
        all_view_df['kickoff_formatted'] = pd.to_datetime(all_view_df['kickoff_utc']).dt.strftime('%b %d, %H:%M CAT')
        all_view_df['Date_Group'] = pd.to_datetime(all_view_df['kickoff_utc']).dt.strftime('%d/%m')
        
        unique_dates = all_view_df['Date_Group'].unique()
        
        for date in unique_dates:
            st.markdown(f"#### 🗓️ Predictions {date}")
            day_rows = all_view_df[all_view_df['Date_Group'] == date]
            
            for _, row in day_rows.iterrows():
                if row['status'] == 'Won':
                    border_color = "#00CC96"
                    status_text = "✅ Won"
                    pnl_val = f"+{profit_per_win:,.0f} FRW"
                elif row['status'] == 'Lost':
                    border_color = "#EF553B"
                    status_text = "❌ Lost"
                    pnl_val = f"-{stake_frw:,.0f} FRW"
                else:
                    border_color = "#888888"
                    status_text = "⏳ Pending"
                    pnl_val = "RUNNING"
                
                st.markdown(
                    f"""
                    <div style="border: 1px solid {border_color}; border-radius: 6px; padding: 6px 12px; margin-bottom: 6px; background-color: rgba(255,255,255,0.01); display: flex; align-items: center; justify-content: space-between; font-family: monospace;">
                        <div style="width: 15%; font-weight: bold; color: #aaa;">{row['kickoff_formatted'].split(',')[1].strip()}</div>
                        <div style="width: 35%; font-size: 14px;"><b>{row['home_player']} vs {row['away_player']}</b></div>
                        <div style="width: 15%; color: #888;">{row['prediction']}</div>
                        <div style="width: 15%; font-weight: bold;">🧠 {row['confidence']}%</div>
                        <div style="width: 10%; color: {border_color};">{status_text}</div>
                        <div style="width: 10%; text-align: right; font-weight: bold; color: {border_color};">{pnl_val}</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    else:
        st.info("The database has predictions, but we are waiting for the automated feedback loop to mark the first results as Won or Lost.")
else:
    st.info("No records found in your database's 'predictions' table yet.")