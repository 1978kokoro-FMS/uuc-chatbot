# app.py

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

# --- 2. API 키 및 Supabase 클라이언트 설정 (✨ 가장 안전한 방식) ---
# Streamlit 앱을 배포할 때는 st.secrets을 사용합니다.
# 로컬에서 테스트할 때는 .streamlit/secrets.toml 파일을 만들어 키를 보관하세요.
try:
    OPENAI_API_KEY = st.secrets["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"]
    openai.api_key = OPENAI_API_KEY

    SUPABASE_URL = st.secrets["https://rbjddlpvpxisurewahtu.supabase.co"]
    SUPABASE_KEY = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJiamRkbHB2cHhpc3VyZXdhaHR1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTYzNjMxNDEsImV4cCI6MjA3MTkzOTE0MX0.AKmGTR0C1tF608hNV3F2RComqpaPb3IWdarwQIDzuuU"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except KeyError:
    st.error("🚨 OpenAI 또는 Supabase의 API Key가 설정되지 않았습니다. Streamlit Secrets를 확인해주세요.")
    st.stop()


# --- 3. 챗봇 로직 (기존 chatbot.py의 핵심 함수) ---
# 기존에 만드신 함수를 그대로 가져옵니다.
def get_chatbot_response(query):
    """
    사용자의 질문에 답변하는 메인 함수
    """
    try:
        # 1. 사용자 질문을 임베딩 벡터로 변환
        response = openai.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding
        
        # 2. Supabase DB에서 관련 문서 검색 (RPC 호출)
        results = supabase.rpc('match_documents', {
            'query_embedding': query_embedding,
            'match_threshold': 0.3,
            'match_count': 5
        }).execute()
        
        if not results.data:
            return "관련된 규정 내용을 찾을 수 없습니다."

        # 3. 검색된 내용을 바탕으로 프롬프트 생성
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
        
        # 4. OpenAI의 ChatGPT를 이용해 최종 답변 생성
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 회사 규정을 명확하고 간결하게 설명해주는 AI 어시스턴트입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

    except Exception as e:
        # 사용자에게 보여지는 오류 메시지는 간단하게 처리하는 것이 좋습니다.
        print(f"오류 상세 정보: {e}") # 개발자 확인용 로그
        return "죄송합니다, 답변을 생성하는 중 오류가 발생했습니다. 다시 시도해주세요."


# --- 4. Streamlit UI 및 대화 로직 ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 회사 규정에 대해 무엇이든 물어보세요."}]

# 이전 대화 기록을 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 질문을 대화 기록에 추가하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 챗봇 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("답변을 생각하고 있어요..."):
            # ✨ 기존 함수를 여기서 호출합니다.
            response = get_chatbot_response(prompt) 
            st.markdown(response)
    
    # 챗봇 답변을 대화 기록에 추가

    st.session_state.messages.append({"role": "assistant", "content": response})
