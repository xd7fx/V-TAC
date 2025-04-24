from langchain_experimental.agents import create_csv_agent
from langchain.chat_models import ChatOpenAI
import os

# ✅ تأكد أن توكنك محفوظ في environment variable أو اكتبه هنا مؤقتًا
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or "sk-xxx"  # استبدله بتوكنك الفعلي

# ✅ مسار ملف CSV (يفضل يكون ثابت داخل مجلد data)
CSV_PATH = os.path.join("data", "matches.csv")

def get_agent():
    llm = ChatOpenAI(
        temperature=0.3,
        model="gpt-4-turbo",
        openai_api_key=OPENAI_API_KEY
    )

    agent = create_csv_agent(
        llm=llm,
        path=CSV_PATH,
        verbose=True,
        allow_dangerous_code=True  # يسمح له يشغل كود تحليل
    )

    return agent
