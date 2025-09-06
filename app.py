# app.py (안전한 버전)
import streamlit as st
import openai
from supabase import create_client, Client

# 페이지 설정
st.set_page_config(
    page_title="사내 규정 챗봇",
    page_icon="🤖",
    layout="centered"
)

# 간단한 CSS 스타일
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-header {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .stChatMessage {
        border-radius: 15px !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; color: #333; font-size: 2.5rem;">
        🤖 회사 규정 안내 챗봇
    </h1>
    <p style="margin: 1rem 0 0 0; color: #666; font-size: 1.2rem;">
        궁금한 회사 규정에 대해 질문해주세요.
    </p>
</div>
""", unsafe_allow_html=True)

# API 키 설정
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    openai.api_key = OPENAI_API_KEY
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except KeyError:
    st.error("🚨 API Key가 설정되지 않았습니다.")
    st.stop()

# 챗봇 로직
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
        
        [참고 규정]
        {conte
