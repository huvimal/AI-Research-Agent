🕵️‍♂️ Professional AI Research Agent
Dự án này là một Tác nhân AI thông minh (AI Agent) được phát triển trong tuần thứ 3 của lộ trình học tập để trở thành AI Engineer. Khác với chatbot thông thường, Research Agent có khả năng tự suy luận, sử dụng các công cụ bên ngoài (Tìm kiếm web, tính toán) và tự động tổng hợp báo cáo nghiên cứu chuyên sâu.

🌟 Tính năng nổi bật
Quy trình suy luận ReAct: Agent thực hiện quy trình "Suy nghĩ (Thought) -> Hành động (Action) -> Quan sát (Observation)" để giải quyết các vấn đề phức tạp.

Sử dụng công cụ (Tool Use): Tự động quyết định khi nào cần sử dụng web_search để lấy thông tin mới nhất hoặc calculator để tính toán chính xác số liệu.

Tổng hợp báo cáo tự động: Kết quả nghiên cứu được trình bày bài bản theo định dạng Markdown và lưu trữ tự động trong thư mục reports/.

Xử lý giới hạn API: Tích hợp cơ chế kiểm soát lỗi và độ trễ để đảm bảo Agent hoạt động ổn định với mô hình ngôn ngữ lớn (LLM).

📁 Cấu trúc dự án

research_agent.py: Mã nguồn trung tâm chứa logic điều phối Agent và định nghĩa các công cụ (Tools).

requirements.txt: Danh sách các thư viện cần thiết (groq, duckduckgo-search, python-dotenv).

.env: Lưu trữ API Key bí mật (được bảo vệ bởi .gitignore).

reports/: Thư mục chứa các kết quả nghiên cứu đã hoàn thành.

🚀 Hướng dẫn cài đặt
1. Clone repository
git clone https://github.com/huvimal/AI-Research-Agent.git
cd AI-Research-Agent
2. Thiết lập API Key
Tạo file .env và thêm mã API Groq của bạn:

GROQ_API_KEY=your_api_key_here

3. Cài đặt môi trường
python -m venv .venv
# Windows: .\.venv\Scripts\activate | Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt

🛠 Cách sử dụng
Khởi động Agent và nhập chủ đề bạn muốn nghiên cứu:

python research_agent.py

Sau khi hoàn thành, Agent sẽ thông báo đường dẫn file báo cáo trong thư mục reports/.

👤 Tác giả
Lê Mai Vĩnh Hưng
Lĩnh vực: Data Engineering, AI, Blockchain.
