from groq import Groq
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()
client = Groq()

class AgentWithMemory:
    def __init__(self):
        self.short_term = []    # lịch sử hội thoại gần nhất
        self.long_term = []     # facts quan trọng được lưu lại
        self.max_short = 10     # giữ 10 tin nhắn gần nhất

    def remember(self, fact: str):
        """Lưu fact quan trọng vào long-term memory."""
        entry = {"fact": fact, "time": datetime.now().strftime("%H:%M")}
        self.long_term.append(entry)
        return f"Đã ghi nhớ: {fact}"

    def recall(self) -> str:
        """Lấy toàn bộ long-term memory."""
        if not self.long_term:
            return "Chưa có gì được ghi nhớ."
        return "".join([f"[{m['time']}] {m['fact']}" for m in self.long_term])

    def build_system_prompt(self):
        memory_str = self.recall()
        return f"""Bạn là trợ lý thông minh có khả năng ghi nhớ thông tin.
Khi người dùng chia sẻ thông tin quan trọng về bản thân (tên, sở thích, công việc...),
hãy gọi tool remember() để lưu lại.

Thông tin đã ghi nhớ:
{memory_str}

Trả lời bằng tiếng Việt."""

    def chat(self, user_msg):
        TOOLS = [
            {"type":"function","function":{"name":"remember","description":"Lưu thông tin quan trọng vào bộ nhớ dài hạn","parameters":{"type":"object","properties":{"fact":{"type":"string","description":"Thông tin cần ghi nhớ"}},"required":["fact"]}}},
            {"type":"function","function":{"name":"recall","description":"Xem lại toàn bộ thông tin đã ghi nhớ","parameters":{"type":"object","properties":{}}}}
        ]

        self.short_term.append({"role": "user", "content": user_msg})
        recent = self.short_term[-self.max_short:]

        r = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role":"system","content":self.build_system_prompt()}] + recent,
            tools=TOOLS, tool_choice="auto"
        )

        msg = r.choices[0].message
        if r.choices[0].finish_reason == "tool_calls":
            self.short_term.append(msg)
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = self.remember(**args) if tc.function.name == "remember" else self.recall()
                self.short_term.append({"role":"tool","tool_call_id":tc.id,"content":result})

            r2 = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role":"system","content":self.build_system_prompt()}] + self.short_term[-self.max_short:]
            )
            reply = r2.choices[0].message.content
        else:
            reply = msg.content

        self.short_term.append({"role": "assistant", "content": reply})
        return reply

# Demo
agent = AgentWithMemory()
convos = [
    "Tên tôi là Hưng, tôi đang học AI Engineer",
    "Tôi thích Python và đang làm dự án RAG",
    "Bạn có nhớ tôi tên gì không?",
    "Gợi ý cho tôi bước học tiếp theo phù hợp với background của tôi",
]
for msg in convos:
    print(f"User: {msg}")
    print(f"Agent: {agent.chat(msg)}")