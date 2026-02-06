import streamlit as st
import google.generativeai as genai
import datetime

# 1. 화면 디자인 및 설정
st.set_page_config(page_title="2026년 삼재(三災) 확인 & 처방", page_icon="👹", layout="centered")

st.markdown("""
<style>
    /* 전체 배경 흰색 (라이트 모드 강제) */
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    /* 타이틀 및 헤더 검은색 */
    h1, h2, h3 {
        color: #000000 !important;
        font-family: 'Gowun Batang', serif;
        text-align: center;
    }
    p, label, div {
        color: #000000 !important;
        font-family: 'Gowun Batang', serif;
    }
    /* 입력창 스타일: 흰 배경, 검은 글씨, 테두리 */
    .stTextInput input, .stSelectbox, .stDateInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #cccccc !important;
    }
    /* 버튼 스타일 */
    div.stButton > button {
        background-color: #D32F2F; /* 경고 느낌의 붉은색 */
        color: white !important;
        border: none; 
        font-weight: bold; 
        padding: 10px; 
        border-radius: 8px;
    }
    .samjae-warning {
        background-color: #FFEBEE;
        border: 1px solid #FFCDD2;
        padding: 15px;
        border-radius: 5px;
        color: #B71C1C !important;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .safe-message {
        background-color: #E8F5E9;
        border: 1px solid #C8E6C9;
        padding: 15px;
        border-radius: 5px;
        color: #1B5E20 !important;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("👹 2026년(병오년) 삼재 확인")
st.markdown("<p style='text-align: center; color: #666;'>2026년 병오년(붉은 말의 해), 나는 삼재일까요?</p>", unsafe_allow_html=True)

# 2. API 키 가져오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = st.text_input("🔑 API 키 입력 (설정 파일이 없는 경우)", type="password")

st.divider()

# 3. 로직 함수
def get_zodiac(year):
    zodiacs = ["원숭이", "닭", "개", "돼지", "쥐", "소", "범", "토끼", "용", "뱀", "말", "양"]
    return zodiacs[year % 12]

def check_samjae(year):
    # 2026년 기준 삼재 판별
    # 돼지(3), 토끼(7), 양(11) 띠는 2026년에 '눌삼재' (삼재의 두 번째 해)
    # 삼재 기간: 2025(을사) ~ 2027(정미)
    zodiac_idx = year % 12
    if zodiac_idx in [3, 7, 11]:  # 돼지, 토끼, 양
        return {
            "is_samjae": True,
            "status": "눌삼재 (Middle Samjae)",
            "period": "2025년 ~ 2027년",
            "year_th": "2년차"
        }
    return {
        "is_samjae": False,
        "status": "해당 없음",
        "period": "-",
        "year_th": "-"
    }

# 4. 사용자 정보 입력
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("이름 (닉네임)", placeholder="홍길동")
    gender = st.radio("성별", ["남성", "여성"], horizontal=True)

with col2:
    birth_date = st.date_input("생년월일", min_value=datetime.date(1940, 1, 1), value=datetime.date(1990, 1, 1))
    # 생년월일에서 연도 추출
    birth_year = birth_date.year
    user_zodiac = get_zodiac(birth_year)

st.info(f"당신의 띠는 **'{user_zodiac}띠'** 입니다.")

# 띠에 따른 삼재 여부 미리 확인
samjae_info = check_samjae(birth_year)

if samjae_info["is_samjae"]:
    st.markdown(f"""
    <div class='samjae-warning'>
        ⚠️ <b>{name}</b>님, 2026년은 <b>{user_zodiac}띠</b>의 <b>{samjae_info['status']}</b>입니다.<br>
        (삼재 기간: <b>{samjae_info['period']}</b> 중 {samjae_info['year_th']})<br>
        각별한 주의가 필요합니다.
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"<div class='safe-message'>✅ <b>{name}</b>님, 2026년은 삼재가 아닙니다.<br>편안한 한 해가 될 것입니다.</div>", unsafe_allow_html=True)

detail_concern = st.text_area("삼재와 관련하여 걱정되거나 궁금한 점이 있다면 적어주세요", placeholder="예: 재물 손실이 걱정됩니다. 예방할 방법이 있을까요?")

solve_btn = st.button("👹 삼재 풀이 & 액땜 비법 확인하기", use_container_width=True)

# 5. 운세 풀이 로직
if solve_btn:
    if not name:
        st.warning("이름을 입력해주세요.")
    elif not api_key:
        st.error("API 키가 필요합니다.")
    else:
        with st.spinner("액운을 막고 복을 부르는 비법을 찾는 중... 🏮"):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-flash-latest')
                
                # 프롬프트 구성 (삼재 여부에 따라 다르게)
                if samjae_info["is_samjae"]:
                    prompt_context = f"""
                    내담자는 2026년 '눌삼재'에 해당하는 {user_zodiac}띠입니다.
                    - 삼재 기간: {samjae_info['period']}
                    - 현재 상태: {samjae_info['status']} ({samjae_info['year_th']})
                    
                    삼재(Three Calamities)는 9년마다 돌아오는 3가지 재난을 의미하며, 눌삼재는 그 중 두 번째 해로, 액운이 머무는 시기라 하여 주의가 필요합니다.
                    내담자에게 삼재 기간({samjae_info['period']})을 명확히 인지시키고, 경각심을 주되 슬기롭게 극복할 수 있는 조언을 해주세요.
                    """
                else:
                    prompt_context = f"""
                    내담자는 2026년 삼재에 해당하지 않습니다 ({user_zodiac}띠).
                    매우 다행스러운 일임을 알려주고, 더욱 발전할 수 있는 긍정적인 조언을 해주세요.
                    """

                prompt = f"""
                당신은 전통 명리학과 삼재 풀이의 대가입니다. 지금은 2026년(병오년, 붉은 말의 해)입니다.
                
                [내담자 정보]
                - 이름: {name}
                - 성별: {gender}
                - 생년월일: {birth_date.strftime('%Y년 %m월 %d일')} ({user_zodiac}띠)
                - 삼재 여부: {samjae_info['status']}
                - 삼재 기간: {samjae_info['period']}
                - 고민 사항: {detail_concern}
                
                {prompt_context}

                [요청사항]
                1. 2026년 병오년의 기운과 내담자의 조화를 설명해주세요.
                2. **[필수] 내담자의 삼재 기간({samjae_info['period']})과 현재 상태({samjae_info['status']})를 명확히 언급해주세요.**
                3. (삼재인 경우) 삼재를 무사히 넘기기 위한 **구체적인 행동 수칙 3가지**를 제안해주세요.
                   (삼재가 아닌 경우) 올해를 기회로 삼기 위한 **행운의 행동 3가지**를 제안해주세요.
                4. 고민 내용({detail_concern})에 대한 맞춤형 조언을 해주세요.
                5. 마지막으로 나쁜 기운을 막아주는 **행운의 아이템(부적 역할)**을 하나 추천해주세요.

                말투는 신비롭지만 진정성 있게, 마치 노스승이 제자에게 조언하듯 작성해주세요.
                답변 형식은 가독성 좋은 Markdown으로 작성하세요.
                """
                
                response = model.generate_content(prompt)
                
                st.markdown("---")
                st.markdown(f"### 📜 {name}님을 위한 처방문")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"천기를 읽는 중 오류가 발생했습니다: {e}")
