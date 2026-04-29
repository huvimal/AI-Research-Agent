from groq import Groq
from dotenv import load_dotenv
import json, math

load_dotenv()
client = Groq()

def calculator(expression):
    try:
        # Xử lý cả số lẫn chuỗi
        expr = str(expression)
        return str(eval(expr, {"__builtins__": {}}, {"math": math}))
    except Exception as e:
        return f"Error: {e}"

def search_knowledge(query):
    kb = {
        "population": "Vietnam has about 98 million people (2024)",
        "area": "Vietnam area is 331212 km2",
        "gdp": "Vietnam GDP 2024 is about 430 billion USD",
        "capital": "Vietnam capital is Hanoi",
    }
    q = query.lower()
    for key, val in kb.items():
        if key in q:
            return val
    return "No data found"

TOOLS_MAP = {"calculator": calculator, "search_knowledge": search_knowledge}

TOOLS_SCHEMA = [
    {"type":"function","function":{"name":"calculator","description":"Calculate math expressions","parameters":{"type":"object","properties":{"expression":{"type":"string"}},"required":["expression"]}}},
    {"type":"function","function":{"name":"search_knowledge","description":"Search facts about Vietnam","parameters":{"type":"object","properties":{"query":{"type":"string","description":"Use English only: population, gdp, area, capital"}},"required":["query"]}}}
]

SYSTEM = """You are a problem-solving agent. Use tools to find facts and calculate.

IMPORTANT for calculator tool:
- NEVER use function names inside expressions
- ONLY use plain numbers. Example: '430000000000 / 98000000'
- After searching for a fact, extract the NUMBER and use it directly in calculator

Example of CORRECT usage:
  search_knowledge('gdp') => 'Vietnam GDP is 430 billion USD'
  calculator('430000000000 / 98000000')  <- use raw numbers only

Always reply to the user in Vietnamese."""

def react_agent(task):
    print(f"\n{'='*55}")
    print(f"Task: {task}")
    print('='*55)

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": task}
    ]

    for step in range(8):
        r = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )

        msg = r.choices[0].message
        finish = r.choices[0].finish_reason

        if finish == "stop":
            print(f"\nKet qua: {msg.content}")
            break

        if finish == "tool_calls":
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                print(f"\nBuoc {step+1}: {name}({args})")
                result = TOOLS_MAP[name](**args)
                print(f"  => {result}")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })

react_agent("Vietnam population? If 73% use internet, how many users?")
react_agent("Vietnam GDP is 430 billion USD, population is 98 million. Calculate GDP per capita in USD.")