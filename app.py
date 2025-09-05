# app.py (디버깅용 임시 코드)
import streamlit as st

st.title("🕵️‍♂️ Secrets 설정 확인 페이지")
st.write("---")

# 1. OPENAI_API_KEY 확인
st.header("1. OpenAI API Key")
if "OPENAI_API_KEY" in st.secrets:
    st.success("✅ OPENAI_API_KEY를 찾았습니다.")
    # 보안을 위해 키의 일부만 표시합니다.
    key_value = st.secrets["OPENAI_API_KEY"]
    st.code(f"값 (일부): {key_value[:5]}...{key_value[-4:]}", language=None)
else:
    st.error("❌ OPENAI_API_KEY를 찾을 수 없습니다.")
    st.info("Streamlit Secrets 설정에서 이름이 정확히 'OPENAI_API_KEY'인지 확인해주세요.")

st.write("---")

# 2. SUPABASE_URL 확인
st.header("2. Supabase URL")
if "SUPABASE_URL" in st.secrets:
    st.success("✅ SUPABASE_URL을 찾았습니다.")
    st.code(f"값: {st.secrets['SUPABASE_URL']}", language=None)
else:
    st.error("❌ SUPABASE_URL을 찾을 수 없습니다.")
    st.info("Streamlit Secrets 설정에서 이름이 정확히 'SUPABASE_URL'인지 확인해주세요.")

st.write("---")

# 3. SUPABASE_KEY 확인
st.header("3. Supabase Key")
if "SUPABASE_KEY" in st.secrets:
    st.success("✅ SUPABASE_KEY를 찾았습니다.")
    # 보안을 위해 키의 일부만 표시합니다.
    key_value = st.secrets["SUPABASE_KEY"]
    st.code(f"값 (일부): {key_value[:5]}...{key_value[-4:]}", language=None)
else:
    st.error("❌ SUPABASE_KEY를 찾을 수 없습니다.")
    st.info("Streamlit Secrets 설정에서 이름이 정확히 'SUPABASE_KEY'인지 확인해주세요.")
