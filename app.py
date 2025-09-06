import streamlit as st
import openai
from supabase import create_client, Client

# 페이지 설정
st.set_page_config(
    page_title="사내 규정 챗봇",
    page_icon="🤖",
    layout="centered"
)

# 1단계: 기본 스타일 추가
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
</style>
""", unsafe_allow_html=True)

# 커스텀 제목
st.markdown("""
<div class="main-title">
    <h1 style="color: #333; margin: 0;">🤖 회사 규정 안내 챗봇</h1>
    <p style="color: #666; margin: 1rem 0 0 0;">궁금한 회사 규정에 대해 질문해주세요.</p>
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

