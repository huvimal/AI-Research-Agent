from groq import Groq
from dotenv import load_dotenv
import json, math

load_dotenv()
client = Groq()

# ── Định nghĩa các tools ──────────────────────────────────
def calculator(expression: str) -> str:
    """Tính toán biểu thức toán học."""
    try:
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return str(result)
    except Exception as e:
        return f"Lỗi: {e}"

def get_weather(city: str) -> str:
    """Giả lập lấy thời tiết (thực tế dùng API)."""
    weather_data = {
        "hà nội": "28°C, có mây, độ ẩm 75%",
        "hcm": "32°C, nắng, độ ẩm 60%",
        "đà nẵng": "30°C, nhiều mây, độ ẩm 70%",
    }
    return weather_data.get(city.lower(), f"Không có dữ liệu thời tiết cho {city}")

def get_current_time() -> str:
    """Lấy thời gian hiện tại."""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S ngày %d/%m/%Y")

# Map tên tool → hàm Python thực tế
TOOLS_MAP = {
    "calculator": calculator,
    "get_weather": get_weather,
    "get_current_time": get_current_time,
}

# ── Mô tả tools cho LLM ──────────────────────────────────
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Tính toán biểu thức toán học",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Biểu thức cần tính, ví dụ: '2 + 3 * 4'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Lấy thông tin thời tiết của một thành phố",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Tên thành phố"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Lấy thời gian hiện tại",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# ── Agent loop ────────────────────────────────────────────
def run_agent(user_message):
    print(f"User: {user_message}")
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )

        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # LLM trả lời thẳng — không cần gọi tool
        if finish_reason == "stop":
            print(f"Agent: {msg.content}")
            break

        # LLM muốn gọi tool
        if finish_reason == "tool_calls":
            messages.append(msg)  # thêm quyết định của LLM vào history

            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"  → Gọi tool: {name}({args})")
                result = TOOLS_MAP[name](**(args if args else {}))
                print(f"  ← Kết quả: {result}")

                # Đưa kết quả tool vào history
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

# Test
run_agent("Tính 15% của 850,000 đồng rồi cho biết thời tiết Hà Nội hôm nay")
run_agent("Bây giờ là mấy giờ và thời tiết HCM thế nào?")
run_agent("Nếu tôi có 1,200,000 đồng và chi tiêu 35% thì còn lại bao nhiêu?")