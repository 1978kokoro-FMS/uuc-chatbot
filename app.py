# app.py (원래 챗봇 코드)
import streamlit as st
import openai
from supabase import create_client, Client

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="사내 규정 챗봇",
    page_icon="🤖",
    layout="centered"
)

st.title("💬 회사 규정 안내 챗봇")
st.caption("궁금한 회사 규정에 대해 질문해주세요.")

# --- 2. API 키 및 Supabase 클라이언트 설정 ---
try:
    OPENAI_API_KEY = st.secrets["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"]
    openai.api_key = OPENAI_API_KEY

    SUPABASE_URL = st.secrets["https://rbjddlpvpxisurewahtu.supabase.co"]
    SUPABASE_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJiamRkbHB2cHhpc3VyZXdhaHR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYzNjMxNDEsImV4cCI6MjA3MTkzOTE0MX0.AKmGTR0C1tF608hNV3F2RComqpaPb3IWdarwQIDzuuU"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except KeyError:
    st.error("🚨 OpenAI 또는 Supabase의 API Key가 설정되지 않았습니다. Streamlit Secrets를 확인해주세요.")
    st.stop()

# --- 3. 챗봇 로직 ---
def get_chatbot_response(query):
    try:
        response = openai.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding

        results = supabase.rpc('match_documents', {
            'query_embedding': query_embedding,
            'match_threshold': 0.3,
            'match_count': 5
        }).execute()

        if not results.data:
            return "관련된 규정 내용을 찾을 수 없습니다."

        context = " ".join([item['content'] for item in results.data])
        prompt = f"""
        당신은 회사 규정 전문가 AI 챗봇입니다. 아래에 제공된 '참고 규정'만을 바탕으로 사용자의 '질문'에 대해 답변해주세요.
        규정 내용에 없는 것을 추측해서 답변하면 안 됩니다. 참고 규정에 답변이 없으면 "관련 규정을 찾을 수 없습니다."라고 답변하세요.

        [참고 규정]
        {context}

        [질문]
        {query}

        [답변]
        """

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 회사 규정을 명확하고 간결하게 설명해주는 AI 어시스턴트입니다."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"오류 상세 정보: {e}") 
        return "죄송합니다, 답변을 생성하는 중 오류가 발생했습니다. 다시 시도해주세요."

# --- 4. Streamlit UI 및 대화 로직 ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 회사 규정에 대해 무엇이든 물어보세요."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("답변을 생각하고 있어요..."):
            response = get_chatbot_response(prompt) 
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


