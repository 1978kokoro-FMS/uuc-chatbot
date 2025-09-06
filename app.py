import streamlit as st
import openai
import os
from supabase import create_client, Client

# 페이지 설정
st.set_page_config(
    page_title="사내 규정 챗봇",
    page_icon="🤖",
    layout="centered"
)

# Enhanced CSS 스타일
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
    }
    
    /* Enhanced glassmorphism header */
    .main-title {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem 2rem;
        border-radius: 25px;
        text-align: center;
        margin: 1rem 0 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        animation: fadeInUp 0.8s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .main-title::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    .main-title h1 {
        color: white !important;
        margin: 0 !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
        letter-spacing: -0.02em;
    }
    
    .main-title p {
        color: rgba(255,255,255,0.9) !important;
        margin: 1rem 0 0 0 !important;
        font-size: 1.2rem !important;
        font-weight: 400;
        text-shadow: 0 1px 5px rgba(0,0,0,0.2);
    }
    
    /* Enhanced message bubbles */
    .user-message {
        background: rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 8px 25px;
        margin: 1rem 0;
        margin-left: 15%;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        font-weight: 500;
        animation: slideInRight 0.5s ease-out;
        position: relative;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
        line-height: 1.6;
    }
    
    .assistant-message {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 25px 25px 25px 8px;
        margin: 1rem 0;
        margin-right: 15%;
        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.2);
        font-weight: 500;
        animation: slideInLeft 0.5s ease-out;
        position: relative;
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
        line-height: 1.6;
    }
    
    /* Chat container with glassmorphism */
    .chat-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Enhanced button styling */
    .stButton > button {
        background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.1)) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        color: white !important;
        border-radius: 30px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: none !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, rgba(255,255,255,0.3), rgba(255,255,255,0.2)) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(1.01) !important;
    }
    
    /* Chat input styling */
    .stChatInput > div > div > div > div {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 25px !important;
        color: white !important;
    }
    
    .stChatInput input {
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 400 !important;
    }
    
    .stChatInput input::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .main-title {
            padding: 2rem 1.5rem;
            margin: 1rem 0 2rem 0;
        }
        
        .main-title h1 {
            font-size: 2.2rem !important;
        }
        
        .main-title p {
            font-size: 1rem !important;
        }
        
        .user-message, .assistant-message {
            margin-left: 5% !important;
            margin-right: 5% !important;
            padding: 1.2rem 1.5rem;
        }
        
        .chat-container {
            padding: 1.5rem;
            margin: 1rem 0;
        }
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }
    
    /* Loading animation for thinking state */
    .thinking {
        animation: pulse 1.5s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced 커스텀 제목
st.markdown("""
<div class="main-title">
    <h1>🤖 회사 규정 안내 챗봇</h1>
    <p>궁금한 회사 규정에 대해 질문해주세요.</p>
</div>
""", unsafe_allow_html=True)

# API 키 설정
try:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not all([OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        st.error("🚨 API Key가 설정되지 않았습니다.")
        st.stop()
    
    openai.api_key = OPENAI_API_KEY
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"🚨 API 설정 중 오류가 발생했습니다: {str(e)}")
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
        
        prompt = f"""당신은 회사 규정 전문가 AI 챗봇입니다. 아래에 제공된 참고 규정만을 바탕으로 사용자의 질문에 대해 답변해주세요.

참고 규정: {context}

질문: {query}

답변:"""
        
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 회사 규정을 명확하고 간결하게 설명해주는 AI 어시스턴트입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return "죄송합니다, 답변을 생성하는 중 오류가 발생했습니다."

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 회사 규정에 대해 무엇이든 물어보세요. 💼"}]

# 대화 초기화 버튼
if len(st.session_state.messages) > 1:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 대화 초기화"):
            st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 회사 규정에 대해 무엇이든 물어보세요. 💼"}]
            st.rerun()

# Enhanced 커스텀 메시지 표시 (컨테이너 없이 직접)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)

# 입력창
if prompt := st.chat_input("질문을 입력하세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 답변 생성 with enhanced loading
    with st.spinner("답변을 생각하고 있어요..."):
        response = get_chatbot_response(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
