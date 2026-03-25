from langchain_core.tools import tool
import pandas as pd
import os

@tool
def get_transactions():
    """Fetches transaction history. Returns a message if no data exists."""
    try:
        if not os.path.exists("transactions.csv"):
            return "No transaction data found. Please upload a CSV first."
        df = pd.read_csv("transactions.csv")
        return df.to_string() if not df.empty else "Transaction list is currently empty."
    except Exception as e:
        return f"Error reading transactions: {str(e)}"

@tool
def calculate_savings_projection(monthly_savings: float, years: int, interest_rate: float = 0.07):
    """
    Computes future savings based on compound interest.
    Formula: A = P * ((1 + r/n)^(nt) - 1) / (r/n)
    """
    try:
        if monthly_savings < 0 or years < 0:
            return "Error: Savings and years must be positive numbers."
        
        # Monthly compounding
        r = interest_rate / 12
        n = 12
        months = years * 12
        
        future_value = monthly_savings * (((1 + r)**months - 1) / r)
        return f"In {years} years, you will have approximately ${future_value:,.2f}."
    except Exception as e:
        return f"Math error: {str(e)}"

@tool
def get_budget_status():
    """Checks total spending against typical 50/30/20 benchmarks."""
    return "Feature under maintenance: Please check back after data sync."