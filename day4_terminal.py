from agent_logic import final_ask

print("--- 💰 Day 4: Financial Reasoning Agent (Terminal Mode) ---")
print("Type 'exit' to quit.")

while True:
    user_input = input("\nYou: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    
    print("\nThinking...")
    response = final_ask(user_input)
    print(f"\nAI: {response}")