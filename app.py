import streamlit as st
import openai
from supabase import create_client, Client

# 페이지 설정
st.set_page_config(
    page_title="사내 규정 챗봇",
    page_icon="🤖",
    layout="centered"
)

# 2단계: 채팅 메시지 스타일 개선
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-title {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    /* 채팅 메시지 스타일 */
    div[data-testid="chat-message-user"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border-radius: 20px 20px 5px 20px !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    div[data-testid="chat-message-assistant"] {
        background: linear-gradient(135deg, #f093fb, #f5576c) !important;
        border-radius: 20px 20px 20px 5px !important;
        margin: 1rem 0 !important;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3) !important;
    }
    
    /* 메시지 텍스트 색상 */
    div[data-testid="chat-message-user"] p,
    div[data-testid="chat-message-assistant"] p {
        color: white !important;
        font-weight: 500 !important;
    }
    
    /* 입력창 스타일 */
    div[data-testid="stChatInputContainer"] {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #667eea !important;
        border-radius: 25px !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# 커스텀 제목
st.markdown("""
<div class="main-title">
    <h1 style="color: #333; margin: 0; font-size: 2.2rem;">🤖 회사 규정 안내 챗봇</h1>
    <p style="color: #666; margin: 1rem 0 0 0; font-size: 1.1rem;">궁금한 회사 규정에 대해 질문해주세요.</p>
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

# 채팅 UI
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
