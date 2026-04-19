import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. MUST BE FIRST: Page Configuration
st.set_page_config(page_title="Financeify", page_icon="📊", layout="wide")

# 2. Load External Styling
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"❌ Could not find {file_name}")

local_css("style.css")

# 3. AI Logic Import & Caching
try:
    from agent_logic import final_ask
except ImportError:
    st.error("agent_logic.py not found!")
    final_ask = None

@st.cache_resource
def get_cached_response(query):
    """Wrapper to cache AI responses and prevent quota errors"""
    if final_ask:
        return final_ask(query)
    return "AI logic not available."

# --- SIDEBAR: CSV UPLOADER ---
st.sidebar.header("📁 Data Input")
uploaded_file = st.sidebar.file_uploader("Upload your transactions (CSV)", type="csv")

# --- MAIN UI ---
st.title("💰 Financeify")

# Create Tabs
tab1, tab2 = st.tabs(["📊 Financial Dashboard", "💬 AI Chat Assistant"])

# --- TAB 1: DASHBOARD ---
with tab1:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Categorization Logic
        def categorize(desc):
            desc = str(desc).lower()
            if any(word in desc for word in ['swiggy', 'zomato', 'food', 'restaurant']): return 'Food'
            if any(word in desc for word in ['uber', 'ola', 'petrol', 'travel']): return 'Travel'
            if any(word in desc for word in ['rent', 'bill', 'electricity']): return 'Bills'
            if any(word in desc for word in ['amazon', 'netflix', 'movie']): return 'Entertainment'
            return 'Others'

        if 'Description' in df.columns and 'Amount' in df.columns:
            df['Category'] = df['Description'].apply(categorize)
            
            # --- TOP METRICS (Dynamic) ---
            total_spent = df['Amount'].sum()
            col_l, col_r = st.columns(2)
            with col_l:
                st.metric("Total Expenses", f"Rs.{total_spent:,.2f}")
            with col_r:
                st.metric("Transactions Count", len(df))

            # --- PLOTLY CHART ---
            st.subheader("Spending Analysis")
            chart_data = df.groupby('Category')['Amount'].sum().reset_index()
            fig = px.pie(chart_data, values='Amount', names='Category', hole=0.4)
            st.plotly_chart(fig, width="stretch")
            
            # Sync data for AI
            df.to_csv("transactions.csv", index=False)
        else:
            st.error("CSV needs 'Description' and 'Amount' columns.")
    else:
        st.info("Please upload a CSV file in the sidebar to start.")

# --- TAB 2: AI CHATBOT ---
with tab2:
    st.header("AI Financial Advisor")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Ask about your budget..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_cached_response(user_query)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})