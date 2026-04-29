import time
from groq import Groq
from dotenv import load_dotenv
from ddgs import DDGS
from datetime import datetime
import json, os, math

load_dotenv()
client = Groq()

# ── Tools ─────────────────────────────────────────────────
def web_search(query: str, max_results: int = 5) -> str:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "Không tìm thấy kết quả"
        return "\n\n".join([f"[{r['title']}]\n{r['body']}" for r in results])
    except Exception as e:
        return f"Lỗi: {e}"

def calculator(expression: str) -> str:
    try:
        expr = str(expression)
        return str(eval(expr, {"__builtins__": {}}, {"math": math}))
    except Exception as e:
        return f"Lỗi: {e}"

def save_report(filename: str, content: str) -> str:
    os.makedirs("reports", exist_ok=True)
    path = f"reports/{filename}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Đã lưu báo cáo: {path}"

TOOLS_MAP = {
    "web_search": web_search,
    "calculator": calculator,
    "save_report": save_report
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search for information on the internet",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query in English"},
                    "max_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate math expressions using plain numbers only",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression with plain numbers only, e.g. '430000000000 / 98000000'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_report",
            "description": "Save the research report to a Markdown file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "File name ending with .md"},
                    "content": {"type": "string", "description": "Full report content in Markdown format"}
                },
                "required": ["filename", "content"]
            }
        }
    }
]

# ── System Prompt ──────────────────────────────────────────
SYSTEM = """You are a professional Research Agent. When given a topic to research:

1. Search the web at least 3 times with different angles
2. Synthesize information from multiple sources
3. Write a complete report in Vietnamese with this format:
   # Title
   ## Overview
   ## Main Content (3-5 sections)
   ## Statistics & Numbers (if available)
   ## Conclusion
4. Save the report using the save_report tool

IMPORTANT:
- Always search multiple times before writing the report
- Use English keywords for web_search
- In calculator, use plain numbers only, never variable names"""

# ── Gọi API với retry khi rate limit ──────────────────────
def call_api(messages):
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                max_tokens=4000

            )
            return r
        except Exception as e:
            if "rate_limit" in str(e) or "429" in str(e):
                wait = 20 * (attempt + 1)
                print(f"  Rate limit, chờ {wait}s rồi thử lại...")
                time.sleep(wait)
            else:
                raise e
    raise Exception("Đã thử 3 lần nhưng vẫn bị rate limit.")

# ── Agent Loop ─────────────────────────────────────────────
def research_agent(topic: str):
    print(f"\n{'='*55}")
    print(f"Research Agent bắt đầu nghiên cứu: {topic}")
    print('='*55)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"report_{timestamp}.md"

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Research this topic and save the report as '{filename}':\n\n{topic}"}
    ]

    step = 0
    while step < 12:
        step += 1
        r = call_api(messages)

        msg = r.choices[0].message
        finish = r.choices[0].finish_reason

        if finish == "stop":
            print(f"\nAgent hoàn thành! Kiểm tra thư mục 'reports/'")
            if msg.content:
                print(f"Agent: {msg.content}")
            break

        if finish == "tool_calls":
            # Lọc reasoning field
            messages.append({
                "role": msg.role,
                "content": msg.content or "",
                "tool_calls": msg.tool_calls
            })

            for tc in msg.tool_calls:
                # Lọc tên tool thừa
                name = tc.function.name.split("<")[0].strip()

                if name not in TOOLS_MAP:
                    print(f"  Bỏ qua tool không hợp lệ: {tc.function.name}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": "Tool not found, please use valid tools only."
                    })
                    continue

                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError:
                    args = {}

                if name == "web_search":
                    print(f"\n[Bước {step}] Tìm kiếm: '{args.get('query', '')}'")
                elif name == "save_report":
                    print(f"\n[Bước {step}] Lưu báo cáo: {args.get('filename', '')}")
                else:
                    print(f"\n[Bước {step}] {name}()")

                result = TOOLS_MAP[name](**args)

                if name == "web_search":
                    result = result[:2000]
                    print(f"  → Tìm thấy {len(result)} ký tự dữ liệu")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })

# ── Main ───────────────────────────────────────────────────
def main():
    print("Research Agent — Tuần 3 Project")
    print("Gõ 'quit' để thoát\n")

    while True:
        topic = input("Nhập topic muốn nghiên cứu: ").strip()
        if topic.lower() == "quit":
            break
        if not topic:
            continue
        research_agent(topic)
        print(f"\nBáo cáo đã lưu trong thư mục 'reports/'")

if __name__ == "__main__":
    main()