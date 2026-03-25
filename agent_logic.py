# import os
# from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langgraph.prebuilt import create_react_agent
# from tools import get_transactions, calculate_savings_projection, get_budget_status

# load_dotenv()

# # 1. Initialize Gemini
# # llm = ChatGoogleGenerativeAI(
# #     model="gemini-1.5-flash-latest", 
# #     api_key=os.getenv("GOOGLE_API_KEY"),
# #     temperature=0
# # )

# llm = ChatGoogleGenerativeAI(
#     # model="gemini-1.5-flash", 
#     # model="I have $1000. If I buy a $300 watch, how does it affect my 50/30/20 balance?", 
#     api_key=os.getenv("GOOGLE_API_KEY"), 
#     version="v1",  # <--- Adding this forces the stable endpoint
#     temperature=0
# )


# # 2. Financial Chain-of-Thought (F-CoT) System Prompt (KPI: Reasoning)
# # We strictly tell the AI how to think.
# SYSTEM_PROMPT = """You are a Professional Financial Reasoning Agent.
# You MUST follow this 'Financial Chain-of-Thought':
# 1. GATHER: Use 'get_transactions' to see current spending.
# 2. COMPUTE: Use 'calculate_savings_projection' if the user asks about the future.
# 3. COMPARE: Compare spending to the 50/30/20 rule (50% Needs, 30% Wants, 20% Savings).
# 4. ADVISE: Give a logical recommendation based on the math.

# If a tool returns an error, explain it to the user clearly.
# Never hallucinate numbers. If you don't have data, say so.
# """

# # 3. Initialize the Day 4 Agent
# tools = [get_transactions, calculate_savings_projection, get_budget_status]

# # We changed 'state_modifier' to 'prompt' here
# agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT) 

# def final_ask(query):
#     """The function for the terminal and web app"""
#     # LangGraph returns a stream of states; we want the last message
#     inputs = {"messages": [("user", query)]}
#     result = agent.invoke(inputs)
#     return result["messages"][-1].content


import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from tools import get_transactions, calculate_savings_projection, get_budget_status

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# --- DAY 4 REASONING ENGINE ---
# Use the exact string found from your find_models.py script
# Usually 'models/gemini-1.5-flash' is the most stable
# llm = ChatGoogleGenerativeAI(
#     model="models/gemini-1.5-flash", 
#     api_key=api_key,
#     temperature=0
# )

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", # USE THE EXACT NAME FROM THE LIST
    api_key=api_key,
    temperature=0
)

SYSTEM_PROMPT = """You are a Professional Financial Reasoning Agent.
Follow the 'Financial Chain-of-Thought':
1. GATHER: Use 'get_transactions'.
2. COMPUTE: Use 'calculate_savings_projection'.
3. COMPARE: Use the 50/30/20 rule.
4. ADVISE: Give logical advice based on the data."""

tools = [get_transactions, calculate_savings_projection, get_budget_status]

# Note: We use 'prompt=' here for your version of LangGraph
agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT)
def final_ask(query):
    inputs = {"messages": [("user", query)]}
    try:
        result = agent.invoke(inputs)
        # Get the last message from the AI
        last_message = result["messages"][-1]
        content = last_message.content
        
        # --- NEW CLEANING LOGIC ---
        # If the AI sends a list (which is why you see brackets), find the text part
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    return item.get('text')
        
        # If it's already a string, just return it
        return content 
        
    except Exception as e:
        if "429" in str(e):
            return "⚠️ Quota Exceeded. Please wait 30 seconds for the 'Free Tier' to reset."
        return f"System Error: {str(e)}"