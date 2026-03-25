import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Try to import the logic safely
try:
    from agent_logic import final_ask
except ImportError:
    final_ask = None

st.set_page_config(page_title="Financeify", page_icon="📊", layout="wide")

# --- SIDEBAR: CSV UPLOADER ---
st.sidebar.header("📁 Data Input")
uploaded_file = st.sidebar.file_uploader("Upload your transactions (CSV)", type="csv")

# Create Tabs for a clean look
tab1, tab2 = st.tabs(["📊 Financial Dashboard", "💬 AI Chat Assistant"])

# --- TAB 1: CATEGORIZATION & GRAPHS ---
with tab1:
    st.header("Financial Categorization Engine")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Simple Categorization Logic (The "Engine")
        # We look for keywords in the description to assign categories
        def categorize(desc):
            desc = str(desc).lower()
            if any(word in desc for word in ['swiggy', 'zomato', 'restaurant', 'food']): return 'Food'
            if any(word in desc for word in ['uber', 'petrol', 'ola', 'train']): return 'Travel'
            if any(word in desc for word in ['rent', 'bill', 'electricity']): return 'Bills'
            if any(word in desc for word in ['netflix', 'amazon', 'movie']): return 'Entertainment'
            return 'Others'

        # Apply the engine (Assuming your CSV has a column named 'Description' and 'Amount')
        if 'Description' in df.columns and 'Amount' in df.columns:
            df['Category'] = df['Description'].apply(categorize)
            
            # Show the categorized data
            st.subheader("Categorized Data")
            st.dataframe(df, use_container_width=True)
            
            # --- THE GRAPH ---
            st.subheader("Spending Analysis")
            chart_data = df.groupby('Category')['Amount'].sum().reset_index()
            fig = px.pie(chart_data, values='Amount', names='Category', title='Spending by Category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
            
            # Save for the AI to read
            df.to_csv("transactions.csv", index=False)
            st.success("✅ Data synced with AI Brain!")
        else:
            st.error("CSV must have 'Description' and 'Amount' columns.")
    else:
        st.info("Please upload a CSV file in the sidebar to see the graphs and categorization.")

# --- TAB 2: AI CHATBOT (DAY 3) ---
with tab2:
    st.header("AI Financial Advisor")
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if user_query := st.chat_input("Ask about your budget or the 50/30/20 rule..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            if final_ask is None:
                st.error("Error: agent_logic.py not found.")
            else:
                with st.spinner("Analyzing..."):
                    response = final_ask(user_query)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})