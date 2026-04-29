import os
import json
import math
from groq import Groq
from dotenv import load_dotenv
from ddgs import DDGS

load_dotenv()
client = Groq()

# ── Tools ──────────────────────────────────────────────
def web_search(query: str, max_results: int = 4) -> str:
    """Tìm kiếm thông tin trên internet."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "Không tìm thấy kết quả"
        output = [f"Tiêu đề: {r['title']}\nNội dung: {r['body']}" for r in results]
        return "\n---\n".join(output)
    except Exception as e:
        return f"Lỗi tìm kiếm: {e}"

def calculator(expression: str) -> str:
    """Tính toán biểu thức toán học. Đảm bảo input là chuỗi không chứa dấu phẩy."""
    try:
        # Xử lý trường hợp AI truyền số có dấu phẩy (vd: 98,000,000)
        clean_expr = str(expression).replace(',', '')
        # Giới hạn các hàm toán học an toàn từ thư viện math
        safe_dict = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        return str(eval(clean_expr, {"__builtins__": {}}, safe_dict))
    except Exception as e:
        return f"Lỗi tính toán: {e}. Vui lòng thử lại với định dạng số thuần (vd: 1000000)."

def summarize_text(text: str, max_words: int = 100) -> str:
    """Tóm tắt đoạn văn bản dài."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."

TOOLS_MAP = {
    "web_search": web_search,
    "calculator": calculator,
    "summarize_text": summarize_text,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Tìm kiếm thông tin mới nhất trên internet",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Từ khóa tìm kiếm"},
                    "max_results": {"type": "integer"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Tính toán toán học. Luôn truyền biểu thức dưới dạng chuỗi (string).",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Ví dụ: '98000000 * 0.73'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_text",
            "description": "Tóm tắt văn bản",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "max_words": {"type": "integer"}
                },
                "required": ["text"]
            }
        }
    }
]

def web_agent(task, verbose=True):
    print(f"\nTask: {task}\n{'-'*50}")
    messages = [
        {
            "role": "system", 
            "content": (
                "Bạn là research agent thông minh. "
                "QUAN TRỌNG: Khi dùng tool calculator, bạn phải truyền biểu thức là một chuỗi (string), "
                "TUYỆT ĐỐI không dùng dấu phẩy để ngăn cách hàng nghìn (ví dụ dùng 1000000 thay vì 1,000,000). "
                "Trả lời bằng tiếng Việt chính xác và ngắn gọn."
            )
        },
        {"role": "user", "content": task}
    ]

    for step in range(6):
        r = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            max_tokens=1000
        )
        msg = r.choices[0].message
        finish = r.choices[0].finish_reason

        if finish == "stop":
            print(f"\n==> KẾT QUẢ CUỐI CÙNG:\n{msg.content}")
            return msg.content

        if finish == "tool_calls":
            messages.append(msg)
            for tc in msg.tool_calls:
                name = tc.function.name
                args = json.loads(tc.function.arguments)
                
                # In log để theo dõi
                val = list(args.values())[0] if args else ''
                if verbose:
                    print(f"[Bước {step+1}] Thực thi: {name}({val})")
                
                result = TOOLS_MAP[name](**args)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)[:2000]})

# Test
web_agent("Dân số Việt Nam 2024 là bao nhiêu? Nếu 73% dùng internet thì có bao nhiêu người dùng?")