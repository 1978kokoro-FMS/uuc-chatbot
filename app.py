# 맨 위에 이 코드만 추가해서 테스트
st.markdown("""
<style>
.stApp {
    background: red !important;
}
</style>
""", unsafe_allow_html=True)


# app.py (최종 보안 버전 + 심플한 UI)
import streamlit as st
import openai
from supabase import create_client, Client

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="사내 규정 챗봇",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. 심플한 커스텀 CSS ---
st.markdown("""
<style>
    /* 전체 배경 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    /* 헤더 스타일 */
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 800px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* 챗 메시지 컨테이너 */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 15px !important;
        margin: 1rem 0 !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* 사용자 메시지 스타일 */
    .stChatMessage[data-testid="chat-message-user"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-user"] .stMarkdown {
        color: white !important;
    }
    
    /* 어시스턴트 메시지 스타일 */
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: linear-gradient(135deg, #f093fb, #f5576c) !important;
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] .stMarkdown {
        color: white !important;
    }
    
    /* 챗 입력창 스타일 */
    .stChatInputContainer {
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 25px !important;
        border: 2px solid #667eea !important;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2) !important;
        padding: 0.5rem !important;
    }
    
    .stChatInputContainer textarea {
        border: none !important;
        background: transparent !important;
        border-radius: 20px !important;
        font-size: 16px !important;
    }
    
    /* 챗 전체 컨테이너 */
    .stChatFloatingInputContainer {
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        margin: 1rem auto !important;
        max-width: 800px !important;
        padding: 2rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    /* 스피너 스타일 */
    .stSpinner {
        border-top-color: #667eea !important;
    }
    
    /* 초기화 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.8rem 2rem !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* 애니메이션 */
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
    
    .fade-in {
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* 숨기기 */
    .stDeployButton { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    
    /* 메인 컨테이너 패딩 조정 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 헤더 ---
st.markdown("""
<div class="header-container fade-in">
    <h1 style="margin: 0; color: #333; font-size: 2.5rem;">
        🤖 회사 규정 안내 챗봇
    </h1>
    <p style="margin: 1rem 0 0 0; color: #666; font-size: 1.2rem;">
        궁금한 회사 규정에 대해 질문해주세요.
    </p>
</div>
""", unsafe_allow_html=True)

# --- 4. API 키 및 Supabase 클라이언트 설정 (보안 방식) ---
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    openai.api_key = OPENAI_API_KEY
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except KeyError:
    st.error("🚨 OpenAI 또는 Supabase의 API Key가 설정되지 않았습니다. Streamlit Secrets를 확인해주세요.")
    st.stop()

# --- 5. 챗봇 로직 ---
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

# --- 6. 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 회사 규정에 대해 무엇이든 물어보세요. 💼"}]

# --- 7. 대화 초기화 버튼 (대화가 있을 때만 표시) ---
if len(st.session_state.messages) > 1:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 대화 초기화", key="clear"):
            st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 회사 규정에 대해 무엇이든 물어보세요. 💼"}]
            st.rerun()

# --- 8. Streamlit UI 및 대화 로직 ---
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

# --- 9. 푸터 ---
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem; color: rgba(255, 255, 255, 0.8);">
    <p>💼 더 자세한 정보가 필요하시면 인사팀에 문의해주세요.</p>
</div>
""", unsafe_allow_html=True)

