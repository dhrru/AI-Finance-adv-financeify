import streamlit as st
import pandas as pd
import plotly.express as px
import os
from database_manager import initialize_db, register_user, login_user, update_user_data, fetch_user_data
from report_generator import generate_pdf_report

# --- 1. CONFIGURATION & DATABASE STARTUP ---
st.set_page_config(page_title="Financeify", page_icon="💰", layout="wide")

@st.cache_resource
def startup_db():
    """Initializes the database once and caches the result to prevent loops."""
    initialize_db()

startup_db()

# --- 2. STYLING & AI BRAIN IMPORT ---
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass 

local_css("style.css")

try:
    from agent_logic import final_ask
except ImportError:
    st.error("agent_logic.py not found! Ensure it is in the project directory.")
    final_ask = None

@st.cache_resource
def get_cached_response(query):
    if final_ask:
        return final_ask(query)
    return "AI logic not available."

# --- 3. LOGIC HELPERS ---
def categorize(desc):
    """Categorizes transactions based on keyword matching."""
    desc = str(desc).lower()
    if any(word in desc for word in ['swiggy', 'zomato', 'food', 'restaurant', 'starbucks']): return 'Food'
    if any(word in desc for word in ['uber', 'ola', 'petrol', 'travel', 'pump', 'cv raman']): return 'Travel'
    if any(word in desc for word in ['rent', 'bill', 'electricity', 'wifi', 'airtel']): return 'Bills'
    if any(word in desc for word in ['amazon', 'netflix', 'movie', 'shopping', 'shoes']): return 'Entertainment'
    return 'Others'

# --- 4. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# --- 5. PAGE: AUTHENTICATION ---
def show_auth_page():
    st.title("💰 Financeify Pro MAX")
    st.write("Secure AI-Driven Financial Management")
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            u_log = st.text_input("Username", key="l_user")
            p_log = st.text_input("Password", type="password", key="l_pass")
            if st.button("Sign In", use_container_width=True):
                uid = login_user(u_log, p_log)
                if uid:
                    st.session_state.logged_in = True
                    st.session_state.user_id = uid
                    st.session_state.username = u_log
                    # Sync initial data to CSV for the AI Agent
                    df_init = fetch_user_data(uid)
                    if not df_init.empty:
                        df_init.to_csv("transactions.csv", index=False)
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        
        with tab2:
            u_reg = st.text_input("Choose Username", key="r_user")
            p_reg = st.text_input("Choose Password", type="password", key="r_pass")
            if st.button("Create Account", use_container_width=True):
                if register_user(u_reg, p_reg):
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Username already taken.")

# --- 6. PAGE: DASHBOARD & AI ---
def show_dashboard():
    # Sidebar Logout
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        if os.path.exists("transactions.csv"):
            os.remove("transactions.csv")
        st.rerun()

    st.title("💸 Wealth Dashboard")
    
    # Fetch Data from SQLite
    df = fetch_user_data(st.session_state.user_id)
    
    # Update Data Drawer
    with st.expander("📁 Update Financial Records"):
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        if uploaded_file:
            new_df = pd.read_csv(uploaded_file)
            if 'Description' in new_df.columns and 'Amount' in new_df.columns:
                new_df['Category'] = new_df['Description'].apply(categorize)
                update_user_data(st.session_state.user_id, new_df)
                new_df.to_csv("transactions.csv", index=False) # AI Sync
                st.success("Records updated!")
                st.rerun()
            else:
                st.error("CSV requires 'Description' and 'Amount' columns.")

    # Main Tabs
    tab1, tab2 = st.tabs(["📊 Financial Analytics", "💬 AI Wealth Advisor"])

    with tab1:
        if not df.empty:
            # --- Calculations ---
            total_spent = df['Amount'].sum()
            cat_totals = df.groupby('Category')['Amount'].sum()
            top_cat = cat_totals.idxmax()
            
            # --- Metrics Row ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Expenses", f"Rs.{total_spent:,.2f}")
            m2.metric("Total Records", len(df))
            m3.metric("Top Category", top_cat)

            st.divider()

            # --- Charts Layout ---
            col_l, col_r = st.columns([1, 1])
            with col_l:
                st.subheader("Spending Distribution")
                fig_pie = px.pie(cat_totals.reset_index(), values='Amount', names='Category', hole=0.5,
                                 color_discrete_sequence=px.colors.sequential.Tealgrn)
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_r:
                st.subheader("Transaction Log")
                st.dataframe(df, use_container_width=True, height=350)

            # --- Trend Analysis ---
            if 'Date' in df.columns:
                st.subheader("Expense Trend")
                df['Date'] = pd.to_datetime(df['Date'])
                trend = df.groupby('Date')['Amount'].sum().reset_index().sort_values('Date')
                fig_line = px.area(trend, x='Date', y='Amount')
                fig_line.update_traces(line_color='#2e7bcf', fillcolor='rgba(46, 123, 207, 0.2)')
                st.plotly_chart(fig_line, use_container_width=True)

            # --- PDF REPORT SECTION ---
            st.divider()
            st.subheader("📄 Generate Financial Audit")
            try:
                pdf_output = generate_pdf_report(st.session_state.username, df, total_spent, top_cat)
                st.download_button(
                    label="Download Audit Report (PDF)",
                    data=pdf_output,
                    file_name=f"Report_{st.session_state.username}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Report generation error: {e}")
        else:
            st.info("No data available. Use the drawer above to upload your CSV records.")

    with tab2:
        st.header("AI Financial Advisor")
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        if query := st.chat_input("Ask about your budget or saving goals..."):
            st.session_state.messages.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing data..."):
                    response = get_cached_response(query)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

# --- 7. ROUTING ---
if st.session_state.logged_in:
    show_dashboard()
else:
    show_auth_page()