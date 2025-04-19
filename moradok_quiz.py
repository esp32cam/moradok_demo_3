import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random
from groq import Groq
from datetime import datetime
import json
import hashlib
from typing import Dict

# การตั้งค่าหน้า
st.set_page_config(
    page_title="🧩 แบบทดสอบบุคลิกภาพทางธุรกิจแบบไดนามิก",
    page_icon="🧩",
    layout="wide"
)

# CSS ปรับแต่งการแสดงผลที่ทันสมัยและมีความเคลื่อนไหวมากขึ้น
st.markdown("""
    <style>
    /* ตกแต่งหน้าเว็บโดยรวม */
    body {
        background-color: #f5f7fa;
        font-family: 'Kanit', sans-serif;
    }
    
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    
    /* เพิ่มสไตล์โปรเกรสวงกลมแบบใหม่ที่มีแอนิเมชันและเงา */
    .progress-container {
        display: flex;
        justify-content: center;
        gap: 12px;
        margin: 25px 0;
        position: relative;
    }
    
    .progress-circle {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 3px 8px rgba(0,0,0,0.15);
    }
    
    .progress-circle.completed {
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
        color: white;
        transform: scale(0.95);
    }
    
    .progress-circle.current {
        background: linear-gradient(135deg, #2c3e50, #1a2530);
        color: white;
        transform: scale(1.15);
        box-shadow: 0 5px 15px rgba(0,0,0,0.25);
    }
    
    .progress-circle.upcoming {
        background: #e0e0e0;
        color: #666;
    }
    
    /* แอนิเมชันการเคลื่อนไหวเมื่อเปลี่ยนคำถาม */
    @keyframes slideIn {
        from { transform: translateX(50px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .quiz-card {
        animation: slideIn 0.6s ease-out;
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border-left: 5px solid #2c3e50;
    }
    
    .quiz-card h3 {
        color: #2c3e50;
        margin-bottom: 15px;
    }
    
    .quiz-card p {
        color: #34495e;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .result-card {
        animation: fadeIn 0.8s ease-out;
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border-left: 5px solid #4CAF50;
    }
    
    .result-card h2 {
        color: #2c3e50;
        margin-bottom: 10px;
    }
    
    .result-card h3 {
        color: #34495e;
        margin-bottom: 15px;
    }
    
    .result-card h4 {
        color: #2c3e50;
        margin-bottom: 10px;
    }
    
    .result-card p, .result-card li {
        color: #34495e;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .dimensional-highlight {
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        background: #f8f9fa;
        border-left: 4px solid #3498db;
        transition: all 0.3s ease;
    }
    
    .dimensional-highlight h4 {
        color: #2c3e50;
        margin-bottom: 8px;
    }
    
    .dimensional-highlight p, .dimensional-highlight li {
        color: #34495e;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .profile-highlight {
        animation: pulse 2s infinite;
        padding: 15px;
        background: linear-gradient(135deg, #f9f9f9, #f2f2f2);
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .profile-highlight h4 {
        color: #2c3e50;
        margin-bottom: 10px;
    }
    
    .profile-highlight li {
        color: #34495e;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 5px;
    }
    
    /* ปรับสไตล์ปุ่มตอบคำตอบ */
    .stButton button {
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        border-radius: 8px !important;
        padding: 12px 20px !important;
        font-weight: 500 !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.08) !important;
        border: none !important;
        margin-bottom: 12px !important;
        text-align: left !important;
        font-size: 1.05rem !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
    }
    
    /* หน้าผลลัพธ์และกราฟ */
    .dimensional-highlight:hover {
        background: #eef2f7;
        transform: translateX(5px);
    }
    
    /* อนิเมชันพิเศษสำหรับจุดเด่น */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.03); }
        100% { transform: scale(1); }
    }
    
    /* สไตล์สำหรับแท็บในผลลัพธ์ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 4px 4px 0 0;
        border: none;
        padding: 10px 20px;
        color: #2c3e50;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2c3e50 !important;
        color: white !important;
    }
    </style>
    
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# จัดการ API Key
if "api_key" not in st.session_state:
    st.session_state.api_key = None

# เพิ่มส่วนสำหรับการป้อน API Key
if st.session_state.api_key is None:
    st.sidebar.title("⚙️ การตั้งค่า")
    api_key = st.sidebar.text_input("ป้อน GROQ API Key (ไม่บังคับ)", type="password")
    if api_key:
        st.session_state.api_key = api_key
        st.sidebar.success("API Key ถูกบันทึกแล้ว!")
    else:
        st.sidebar.info("คุณสามารถข้ามการป้อน API Key ได้ แต่ฟีเจอร์บางอย่างอาจไม่ทำงาน")
else:
    api_key = st.session_state.api_key

# กำหนดค่าเริ่มต้นใน session state
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "quiz_completed" not in st.session_state:
    st.session_state.quiz_completed = False
if "results" not in st.session_state:
    st.session_state.results = {}
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "question_order" not in st.session_state:
    st.session_state.question_order = []
if "user_id" not in st.session_state:
    # สร้าง unique ID สำหรับผู้ใช้แต่ละคน
    current_time = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
    st.session_state.user_id = hashlib.md5(current_time.encode()).hexdigest()[:8]

# คลังคำถามแบบทดสอบ (เพิ่มจำนวนคำถามให้มากขึ้น)
questions_pool = [
    {
        "question": "คุณมักวัดความสำเร็จของการตลาดอย่างไร?",
        "options": [
            "ผม/ฉันมุ่งเน้นตัวเลขยอดขายและการเติบโตของรายได้",
            "ผม/ฉันติดตามเมตริกการมีส่วนร่วมของลูกค้า เช่น โซเชียลมีเดียและจำนวนผู้เข้าชมเว็บไซต์",
            "ผม/ฉันดูทั้งตัวเลขเชิงปริมาณและความคิดเห็นเชิงคุณภาพจากลูกค้า",
            "ผม/ฉันยังไม่มีวิธีการวัดประสิทธิภาพการตลาดอย่างเป็นระบบ"
        ],
        "dimension": "Marketing Performance",
        "weight": 1.0
    },
    {
        "question": "อะไรที่ทำให้คุณแตกต่างจากผู้อื่นในอุตสาหกรรม?",
        "options": [
            "ผม/ฉันมีแบรนด์ส่วนตัวที่เป็นเอกลักษณ์และจดจำได้ทันที",
            "ผม/ฉันนำเสนอโซลูชันใหม่ที่ไม่มีใครเคยมี",
            "ผม/ฉันมีความเชี่ยวชาญเฉพาะทางในช่องทางหนึ่ง",
            "ผม/ฉันกำลังพัฒนาตัวตนที่เป็นเอกลักษณ์ของตัวเอง"
        ],
        "dimension": "Identity Uniqueness",
        "weight": 1.0
    },
    {
        "question": "คุณจัดการการแข่งขันในตลาดอย่างไร?",
        "options": [
            "ผม/ฉันมุ่งเน้นที่จะทำให้เหนือกว่าคู่แข่งทั้งเรื่องราคาและคุณภาพ",
            "ผม/ฉันพยายามหาความต้องการที่ยังไม่ได้รับการตอบสนองและสร้างตลาดใหม่",
            "ผม/ฉันเน้นการสร้างความสัมพันธ์มากกว่าการแข่งขันโดยตรง",
            "ผม/ฉันกำลังศึกษาคู่แข่งเพื่อหาตำแหน่งที่เหมาะสม"
        ],
        "dimension": "Competitive Advantage",
        "weight": 1.0
    },
    {
        "question": "คุณอธิบายวิธีการสร้างเครือข่ายมืออาชีพของคุณอย่างไร?",
        "options": [
            "ผม/ฉันเข้าร่วมกิจกรรมอุตสาหกรรมและเชื่อมต่อกับบุคคลสำคัญอย่างมีแผน",
            "ผม/ฉันรักษาเครือข่ายขนาดเล็กแต่แข็งแกร่ง",
            "ผม/ฉันสบายใจที่จะติดต่อคนแปลกหน้าและสร้างความสัมพันธ์ใหม่",
            "ผม/ฉันพบว่าการสร้างเครือข่ายเป็นเรื่องท้าทายและมักโฟกัสกับงานมากกว่า"
        ],
        "dimension": "Networking Capability",
        "weight": 1.0
    },
    {
        "question": "คุณมักระบุโอกาสทางธุรกิจใหม่อย่างไร?",
        "options": [
            "ผม/ฉันทดลองวิธีการการตลาดและโมเดลธุรกิจใหม่ๆ เสมอ",
            "ผม/ฉันฟังความคิดเห็นลูกค้าและปรับข้อเสนอ",
            "ผม/ฉันทำวิจัยตลาดอย่างเป็นทางการเพื่อหาช่องว่าง",
            "ผม/ฉันมักตามเทรนด์ของอุตสาหกรรมมากกว่าจะสร้างเอง"
        ],
        "dimension": "Entrepreneurial Marketing",
        "weight": 1.0
    },
    {
        "question": "เมื่อทรัพยากรการตลาดจำกัด คุณให้ความสำคัญกับอะไร?",
        "options": [
            "ปรับเปลี่ยนอัตราการแปลงของช่องทางที่มีอยู่",
            "หาวิธีสร้างสรรค์และประหยัดค่าใช้จ่ายเพื่อเข้าถึงลูกค้าใหม่",
            "เสริมความสัมพันธ์กับลูกค้าปัจจุบันเพื่อการซื้อซ้ำ",
            "เก็บทรัพยากรไว้จนกว่าจะพร้อมแผนการตลาดเต็มรูปแบบ"
        ],
        "dimension": "Marketing Performance",
        "weight": 1.0
    },
    {
        "question": "คุณสื่อสารคุณค่า (value proposition) อย่างไร?",
        "options": [
            "ผ่านเรื่องราวส่วนตัวที่สอดคล้องและน่าเชื่อถือ",
            "เน้นผลลัพธ์ที่วัดได้ที่ผม/ฉันสร้างให้ลูกค้า",
            "แสดงความเชี่ยวชาญผ่านการสร้างเนื้อหาและผู้นำทางความคิด",
            "ผม/ฉันยังปรับปรุงข้อความที่จะสื่อสารอยู่"
        ],
        "dimension": "Identity Uniqueness",
        "weight": 1.0
    },
    {
        "question": "เมื่อมีคู่แข่งใหม่เข้ามาในตลาด คุณตอบสนองอย่างไร?",
        "options": [
            "ปรับกลยุทธ์เร็วเพื่อรักษาตำแหน่งแข่งขัน",
            "เน้นจุดแข็งที่คู่แข่งเลียนแบบยาก",
            "มองหาวิธีร่วมมือแทนที่จะมองเป็นคู่แข่ง",
            "รอดูผลงานก่อนค่อยตัดสินใจ"
        ],
        "dimension": "Competitive Advantage",
        "weight": 1.0
    },
    {
        "question": "การร่วมมือมีบทบาทต่อการเติบโตของคุณอย่างไร?",
        "options": [
            "สำคัญมาก - ผม/ฉันมองหาความร่วมมือเชิงกลยุทธ์เสมอ",
            "สำคัญ - ผม/ฉันแลกเปลี่ยนไอเดียและทรัพยากรกับเครือข่าย",
            "เป็นครั้งคราว - ผม/ฉันร่วมมือเมื่อมีโอกาสเฉพาะ",
            "น้อย - ผม/ฉันชอบทำงานคนเดียว"
        ],
        "dimension": "Networking Capability",
        "weight": 1.0
    },
    {
        "question": "คุณวางแผนการตลาดเมื่อต้องเข้าไปในตลาดใหม่อย่างไร?",
        "options": [
            "ทดสอบหลายวิธีอย่างรวดเร็วเพื่อดูว่าวิธีใดใช้ได้ผล",
            "วิจัยอย่างละเอียดก่อนแล้วค่อยดำเนินงาน",
            "ใช้เครือข่ายที่มีเพื่อสร้างความน่าเชื่อถือ",
            "เริ่มเล็กแล้วขยายเมื่อเรียนรู้ตลาด"
        ],
        "dimension": "Entrepreneurial Marketing",
        "weight": 1.0
    },
    # เพิ่มคำถามใหม่เกี่ยวกับมิติต่างๆ
    {
        "question": "เมื่อเผชิญกับความล้มเหลวในธุรกิจ คุณจะทำอย่างไร?",
        "options": [
            "วิเคราะห์ข้อมูลอย่างละเอียดเพื่อหาสาเหตุที่แท้จริง",
            "ปรับตัวรวดเร็วและทดลองแนวทางใหม่ทันที",
            "ปรึกษาเครือข่ายธุรกิจเพื่อขอคำแนะนำ",
            "กลับมาทบทวนแผนและวางกลยุทธ์ใหม่อย่างรอบคอบ"
        ],
        "dimension": "Entrepreneurial Marketing",
        "weight": 1.2  # เพิ่มน้ำหนักให้คำถามสำคัญ
    },
    {
        "question": "คุณมีวิธีการอย่างไรในการบริหารความเสี่ยงทางธุรกิจ?",
        "options": [
            "วางแผนอย่างละเอียดและคาดการณ์สถานการณ์ต่างๆ ล่วงหน้า",
            "กระจายความเสี่ยงผ่านการมีหลายช่องทางรายได้",
            "เริ่มเล็กๆ และขยายเมื่อได้ผลตอบรับที่ดี",
            "รับความเสี่ยงเพื่อโอกาสที่ได้ผลตอบแทนสูง"
        ],
        "dimension": "Competitive Advantage",
        "weight": 1.1
    },
    {
        "question": "คุณให้ความสำคัญกับเรื่องใดมากที่สุดในทีมงาน?",
        "options": [
            "ความสามารถและทักษะที่หลากหลาย",
            "ความกล้าคิดนอกกรอบและสร้างสรรค์",
            "ความเชื่อมั่นและไว้วางใจกัน",
            "ประสิทธิภาพและการทำงานที่เป็นระบบ"
        ],
        "dimension": "Identity Uniqueness",
        "weight": 1.1
    },
    {
        "question": "คุณติดตามความเคลื่อนไหวในอุตสาหกรรมของคุณอย่างไร?",
        "options": [
            "เข้าร่วมงานสัมมนาและเน็ตเวิร์กกับผู้เชี่ยวชาญในวงการ",
            "อ่านบทความและรายงานวิเคราะห์อุตสาหกรรมเป็นประจำ",
            "ติดตามคู่แข่งสำคัญและศึกษากลยุทธ์ของพวกเขา",
            "ฟังเสียงตอบรับจากลูกค้าเพื่อเข้าใจแนวโน้มตลาด"
        ],
        "dimension": "Marketing Performance",
        "weight": 1.2
    },
    {
        "question": "คุณมีวิธีการอย่างไรในการรักษาความสัมพันธ์กับลูกค้าในระยะยาว?",
        "options": [
            "สร้างระบบ loyalty program และให้สิทธิพิเศษ",
            "สื่อสารสม่ำเสมอผ่านช่องทางที่หลากหลาย",
            "มอบประสบการณ์ที่เหนือความคาดหมายในทุกจุดสัมผัส",
            "รับฟังและปรับปรุงบริการตามความต้องการที่เปลี่ยนไป"
        ],
        "dimension": "Networking Capability",
        "weight": 1.2
    },
    {
        "question": "คุณเลือกใช้เทคโนโลยีในธุรกิจอย่างไร?",
        "options": [
            "เป็นผู้นำในการใช้เทคโนโลยีใหม่เสมอ เพื่อความได้เปรียบ",
            "เลือกใช้เฉพาะเทคโนโลยีที่คุ้มค่าต่อการลงทุน",
            "รอให้เทคโนโลยีพิสูจน์ตัวเองในตลาดก่อนนำมาใช้",
            "มุ่งเน้นที่ความสามารถหลักมากกว่าการพึ่งพาเทคโนโลยี"
        ],
        "dimension": "Entrepreneurial Marketing",
        "weight": 1.1
    },
    {
        "question": "คุณจัดการปัญหาความขัดแย้งในทีมอย่างไร?",
        "options": [
            "จัดให้มีการพูดคุยแบบเปิดใจและหาทางออกร่วมกัน",
            "ใช้ข้อมูลและเหตุผลเพื่อหาข้อสรุปที่ดีที่สุด",
            "มองหาทางประนีประนอมที่ทุกฝ่ายยอมรับได้",
            "ตัดสินใจอย่างรวดเร็วเพื่อไม่ให้กระทบการทำงาน"
        ],
        "dimension": "Identity Uniqueness",
        "weight": 1.0
    },
    {
        "question": "คุณมองเรื่องการสร้างแบรนด์อย่างไร?",
        "options": [
            "เป็นการลงทุนระยะยาวที่สร้างมูลค่าให้ธุรกิจ",
            "เป็นเครื่องมือในการสร้างความแตกต่างจากคู่แข่ง",
            "เป็นสิ่งที่ต้องเติบโตอย่างเป็นธรรมชาติจากคุณภาพสินค้า",
            "เป็นส่วนหนึ่งของกลยุทธ์การตลาดที่ต้องคำนวณ ROI"
        ],
        "dimension": "Identity Uniqueness",
        "weight": 1.3
    },
    {
        "question": "เมื่อพบโอกาสทางธุรกิจใหม่ คุณมีขั้นตอนอย่างไร?",
        "options": [
            "วิเคราะห์ข้อมูลอย่างละเอียดก่อนตัดสินใจ",
            "ทดลองในขนาดเล็กเพื่อพิสูจน์แนวคิด",
            "ปรึกษาผู้เชี่ยวชาญหรือที่ปรึกษา",
            "ใช้สัญชาตญาณและตัดสินใจอย่างรวดเร็ว"
        ],
        "dimension": "Entrepreneurial Marketing",
        "weight": 1.2
    },
    {
        "question": "คุณมีมุมมองต่อการระดมทุนอย่างไร?",
        "options": [
            "เป็นโอกาสในการเร่งการเติบโตและขยายธุรกิจ",
            "เป็นความเสี่ยงที่ต้องพิจารณาอย่างรอบคอบ",
            "เป็นทางเลือกสุดท้ายหลังจากพยายามเติบโตด้วยตัวเอง",
            "เป็นโอกาสในการสร้างพันธมิตรและเครือข่าย"
        ],
        "dimension": "Competitive Advantage",
        "weight": 1.1
    }
]

# ชุดบุคลิกภาพทางธุรกิจที่ซับซ้อนมากขึ้น
business_personalities = {
    "Strategic Thinker": {
        "color": "#3498db",  # blue
        "thai_name": "นักคิดเชิงกลยุทธ์",
        "description": "คิดอย่างเป็นระบบ วางแผนระยะยาว และสามารถมองเห็นภาพรวมได้ดี",
        "strengths": [
            "การวางแผนระยะยาว",
            "การวิเคราะห์ตลาดเชิงลึก",
            "การบริหารความเสี่ยง",
            "การตัดสินใจบนฐานข้อมูล"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.8,
            "Competitive Advantage": 0.9,
            "Identity Uniqueness": 0.7,
            "Networking Capability": 0.6,
            "Entrepreneurial Marketing": 0.7
        }
    },
    "Visionary Creator": {
        "color": "#9b59b6",  # purple
        "thai_name": "ผู้สร้างวิสัยทัศน์",
        "description": "มองเห็นอนาคตที่คนอื่นยังมองไม่เห็น สร้างสรรค์และกล้าคิดต่าง",
        "strengths": [
            "ความคิดสร้างสรรค์",
            "การมองเห็นโอกาสใหม่",
            "การสร้างนวัตกรรม",
            "การสร้างแรงบันดาลใจ"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.7,
            "Competitive Advantage": 0.8,
            "Identity Uniqueness": 0.9,
            "Networking Capability": 0.6,
            "Entrepreneurial Marketing": 0.8
        }
    },
    "Relationship Builder": {
        "color": "#2ecc71",  # green
        "thai_name": "ผู้สร้างความสัมพันธ์",
        "description": "สร้างเครือข่ายที่แข็งแกร่งและความสัมพันธ์ที่ยั่งยืนกับลูกค้าและพันธมิตร",
        "strengths": [
            "การสร้างเครือข่าย",
            "การสื่อสารระหว่างบุคคล",
            "การสร้างความไว้วางใจ",
            "การเจรจาต่อรอง"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.6,
            "Competitive Advantage": 0.7,
            "Identity Uniqueness": 0.7,
            "Networking Capability": 0.9,
            "Entrepreneurial Marketing": 0.6
        }
    },
    "Data-Driven Marketer": {
        "color": "#e67e22",  # orange
        "thai_name": "นักการตลาดที่ขับเคลื่อนด้วยข้อมูล",
        "description": "ใช้ข้อมูลและเมตริกในการตัดสินใจทางการตลาดอย่างมีประสิทธิภาพ",
        "strengths": [
            "การวิเคราะห์ข้อมูล",
            "การวัดผลการตลาด",
            "การปรับปรุงอัตราการแปลง",
            "การทดสอบ A/B"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.9,
            "Competitive Advantage": 0.7,
            "Identity Uniqueness": 0.6,
            "Networking Capability": 0.5,
            "Entrepreneurial Marketing": 0.7
        }
    },
    "Agile Experimenter": {
        "color": "#e74c3c",  # red
        "thai_name": "นักทดลองที่คล่องตัว",
        "description": "ปรับตัวเร็ว ทดลองแนวทางใหม่ และเรียนรู้จากความล้มเหลวอย่างรวดเร็ว",
        "strengths": [
            "การปรับตัว",
            "การเรียนรู้อย่างรวดเร็ว",
            "การทดลองแนวทางใหม่",
            "การจัดการกับความไม่แน่นอน"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.7,
            "Competitive Advantage": 0.8,
            "Identity Uniqueness": 0.7,
            "Networking Capability": 0.6,
            "Entrepreneurial Marketing": 0.9
        }
    },
    "Brand Architect": {
        "color": "#1abc9c",  # teal
        "thai_name": "สถาปนิกแบรนด์",
        "description": "สร้างและพัฒนาตัวตนแบรนด์ที่แข็งแกร่งและเป็นเอกลักษณ์",
        "strengths": [
            "การสร้างแบรนด์",
            "การเล่าเรื่อง (Storytelling)",
            "การออกแบบประสบการณ์ลูกค้า",
            "การสร้างความภักดีต่อแบรนด์"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.8,
            "Competitive Advantage": 0.8,
            "Identity Uniqueness": 0.9,
            "Networking Capability": 0.7,
            "Entrepreneurial Marketing": 0.7
        }
    },
    "Community Catalyst": {
        "color": "#ff9ff3",  # pink
        "thai_name": "ผู้จุดประกายชุมชน",
        "description": "สร้างและดูแลชุมชนที่แข็งแกร่ง กระตุ้นการมีส่วนร่วมและการเติบโตร่วมกัน",
        "strengths": [
            "การสร้างชุมชน",
            "การจัดการความสัมพันธ์",
            "การสร้างการมีส่วนร่วม",
            "การสร้างความไว้วางใจในชุมชน"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.6,
            "Competitive Advantage": 0.7,
            "Identity Uniqueness": 0.8,
            "Networking Capability": 0.9,
            "Entrepreneurial Marketing": 0.7
        }
    },
    "Innovation Leader": {
        "color": "#5f27cd",  # indigo
        "thai_name": "ผู้นำด้านนวัตกรรม",
        "description": "นำการเปลี่ยนแปลงและสร้างสรรค์นวัตกรรมใหม่ๆ อย่างต่อเนื่อง",
        "strengths": [
            "การคิดนอกกรอบ",
            "การนำการเปลี่ยนแปลง",
            "การสร้างนวัตกรรม",
            "การมองเห็นโอกาสใหม่"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.7,
            "Competitive Advantage": 0.9,
            "Identity Uniqueness": 0.8,
            "Networking Capability": 0.6,
            "Entrepreneurial Marketing": 0.8
        }
    },
    "Growth Hacker": {
        "color": "#feca57",  # amber
        "thai_name": "นักเติบโตแบบไว",
        "description": "ใช้กลยุทธ์สร้างสรรค์เพื่อเร่งการเติบโตและขยายธุรกิจอย่างรวดเร็ว",
        "strengths": [
            "การทดลองอย่างรวดเร็ว",
            "การวิเคราะห์ข้อมูล",
            "การปรับปรุงประสิทธิภาพ",
            "การสร้างการเติบโตแบบไว"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.9,
            "Competitive Advantage": 0.8,
            "Identity Uniqueness": 0.7,
            "Networking Capability": 0.6,
            "Entrepreneurial Marketing": 0.8
        }
    },
    "Sustainability Champion": {
        "color": "#2ecc71",  # emerald
        "thai_name": "ผู้ขับเคลื่อนความยั่งยืน",
        "description": "มุ่งเน้นการสร้างธุรกิจที่ยั่งยืนทั้งด้านเศรษฐกิจ สังคม และสิ่งแวดล้อม",
        "strengths": [
            "การวางแผนระยะยาว",
            "การสร้างความยั่งยืน",
            "การจัดการความเสี่ยง",
            "การสร้างคุณค่าร่วม"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.7,
            "Competitive Advantage": 0.8,
            "Identity Uniqueness": 0.8,
            "Networking Capability": 0.7,
            "Entrepreneurial Marketing": 0.7
        }
    },
    "Digital Transformer": {
        "color": "#00cec9",  # cyan
        "thai_name": "ผู้เปลี่ยนแปลงสู่ดิจิทัล",
        "description": "นำเทคโนโลยีและดิจิทัลมาปรับปรุงและเปลี่ยนแปลงธุรกิจ",
        "strengths": [
            "การนำเทคโนโลยี",
            "การปรับตัวสู่ดิจิทัล",
            "การสร้างประสบการณ์ดิจิทัล",
            "การจัดการการเปลี่ยนแปลง"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.8,
            "Competitive Advantage": 0.8,
            "Identity Uniqueness": 0.7,
            "Networking Capability": 0.6,
            "Entrepreneurial Marketing": 0.8
        }
    },
    "Customer Experience Designer": {
        "color": "#ff6b6b",  # rose
        "thai_name": "นักออกแบบประสบการณ์ลูกค้า",
        "description": "สร้างประสบการณ์ที่ยอดเยี่ยมให้กับลูกค้าในทุกจุดสัมผัส",
        "strengths": [
            "การออกแบบประสบการณ์",
            "การเข้าใจลูกค้า",
            "การสร้างความพึงพอใจ",
            "การปรับปรุงอย่างต่อเนื่อง"
        ],
        "dimension_affinity": {
            "Marketing Performance": 0.8,
            "Competitive Advantage": 0.7,
            "Identity Uniqueness": 0.8,
            "Networking Capability": 0.7,
            "Entrepreneurial Marketing": 0.7
        }
    }
}

# เพิ่มคำถามเกี่ยวกับ Moradok
moradok_questions = [
    {
        "question": "Moradok คืออะไร?",
        "options": [
            "แพลตฟอร์มที่มุ่งเน้นการอนุรักษ์และพัฒนามรดกชุมชน",
            "แพลตฟอร์มการลงทุนในอสังหาริมทรัพย์",
            "แพลตฟอร์มการเรียนรู้ออนไลน์",
            "แพลตฟอร์มการขายสินค้าชุมชน"
        ],
        "correct": 0,
        "explanation": "Moradok เป็นแพลตฟอร์มที่มุ่งเน้นการอนุรักษ์และพัฒนามรดกชุมชน โดยมีเป้าหมายในการสร้างรายได้จากความภาคภูมิใจในคุณค่าของมรดกชุมชน และให้ทุกคนมีส่วนร่วมในการสร้างคุณค่าสาธารณะร่วมกัน"
    },
    {
        "question": "Moradok มีกี่เสาหลักในการมีส่วนร่วม?",
        "options": [
            "2 เสาหลัก",
            "3 เสาหลัก",
            "4 เสาหลัก",
            "5 เสาหลัก"
        ],
        "correct": 1,
        "explanation": "Moradok มี 3 เสาหลักในการมีส่วนร่วม ได้แก่ 1) Your Idea (แบ่งปันความคิด) 2) Your Action (แบ่งปันเวลา) และ 3) Your Fund (แบ่งปันทุน) ซึ่งแต่ละเสาหลักมีวิธีการมีส่วนร่วมที่แตกต่างกัน"
    },
    {
        "question": "เสาหลัก 'Your Idea' เกี่ยวข้องกับอะไร?",
        "options": [
            "การบริจาคเงิน",
            "การแบ่งปันความคิดเกี่ยวกับพื้นที่มรดก",
            "การเข้าร่วมกิจกรรม",
            "การลงทุนในโครงการ"
        ],
        "correct": 1,
        "explanation": "เสาหลัก 'Your Idea' เกี่ยวข้องกับการแบ่งปันความคิดเกี่ยวกับพื้นที่มรดก โดยผู้ใช้สามารถแสดงความคิดเห็นออนไลน์และมีส่วนร่วมในการพัฒนาพื้นที่มรดกผ่านการเสนอแนวคิดใหม่ๆ"
    },
    {
        "question": "Moradok Srangsan (มรดกสร้างสรรค์) คืออะไร?",
        "options": [
            "กลุ่มที่มีมรดกทางธรรมชาติและวัฒนธรรมพร้อมส่งต่อด้วยคุณค่าเพิ่ม",
            "ระบบการลงคะแนนในแพลตฟอร์ม",
            "ฟีเจอร์การเรียนรู้ออนไลน์",
            "ระบบการบริจาค"
        ],
        "correct": 0,
        "explanation": "Moradok Srangsan หรือ มรดกสร้างสรรค์ หมายถึงกลุ่มที่มีมรดกทางธรรมชาติและวัฒนธรรมที่พร้อมจะส่งต่อด้วยคุณค่าเพิ่มผ่านกระบวนการของเจ้าของที่ใช้นวัตกรรมและระบบนิเวศทางเศรษฐกิจ"
    },
    {
        "question": "Moradok Baengpan (มรดกแบ่งปัน) เกี่ยวข้องกับอะไร?",
        "options": [
            "การขยายวงของผู้สนับสนุนผ่านการเป็นอาสาสมัครและการบริจาค",
            "การขายสินค้าชุมชน",
            "การเรียนรู้ออนไลน์",
            "การลงทุนในอสังหาริมทรัพย์"
        ],
        "correct": 0,
        "explanation": "Moradok Baengpan หรือ มรดกแบ่งปัน เกี่ยวข้องกับการขยายวงของผู้สนับสนุนและผู้ขับเคลื่อนผ่านการเป็นอาสาสมัคร การบริจาค และการลงทุน เพื่อสร้างโอกาสและนวัตกรรมที่ยั่งยืน"
    }
]

# ฟังก์ชันสุ่มคำถาม
def get_random_questions():
    if "question_order" not in st.session_state or len(st.session_state.question_order) == 0:
        # สุ่มจำนวนคำถามระหว่าง 10-30 ข้อ
        num_questions = random.randint(10, 30)
        
        # เลือกคำถามแบบสุ่มโดยคำนึงถึงน้ำหนักของแต่ละมิติ
        dimensions = ["Marketing Performance", "Identity Uniqueness", "Competitive Advantage", 
                    "Networking Capability", "Entrepreneurial Marketing"]
        questions_by_dimension = {dim: [] for dim in dimensions}
        
        for q in questions_pool:
            questions_by_dimension[q["dimension"]].append(q)
        
        # เลือกคำถามจากแต่ละมิติอย่างสมดุล
        selected_questions = []
        questions_per_dimension = max(1, num_questions // len(dimensions))
        
        for dim in dimensions:
            dim_questions = questions_by_dimension[dim]
            if len(dim_questions) > questions_per_dimension:
                selected_questions.extend(random.sample(dim_questions, questions_per_dimension))
            else:
                selected_questions.extend(dim_questions)
        
        # เติมคำถามให้ครบจำนวนที่ต้องการ
        remaining = num_questions - len(selected_questions)
        if remaining > 0:
            extra_questions = [q for q in questions_pool if q not in selected_questions]
            if len(extra_questions) > remaining:
                selected_questions.extend(random.sample(extra_questions, remaining))
            else:
                selected_questions.extend(extra_questions)
        
        # สุ่มลำดับคำถามอีกครั้ง
        random.shuffle(selected_questions)
        st.session_state.question_order = selected_questions
    
    return st.session_state.question_order

# ฟังก์ชันคำนวณผลลัพธ์แบบทดสอบบุคลิกภาพ
def calculate_results():
    dimension_scores = {
        "Marketing Performance": 0,
        "Identity Uniqueness": 0,
        "Competitive Advantage": 0,
        "Networking Capability": 0,
        "Entrepreneurial Marketing": 0
    }
    dimension_counts = {dim: 0 for dim in dimension_scores.keys()}
    
    for i, answer in enumerate(st.session_state.answers):
        question = st.session_state.question_order[i]
        dimension = question["dimension"]
        weight = question["weight"]
        
        # คะแนนสำหรับแต่ละคำตอบ (0-3)
        answer_score = answer / (len(question["options"]) - 1)
        dimension_scores[dimension] += answer_score * weight
        dimension_counts[dimension] += weight
    
    # คำนวณคะแนนเฉลี่ยสำหรับแต่ละมิติ
    for dim in dimension_scores:
        if dimension_counts[dim] > 0:
            dimension_scores[dim] = dimension_scores[dim] / dimension_counts[dim]
    
    # หาบุคลิกภาพที่ตรงที่สุด
    personality_scores = {}
    for personality, data in business_personalities.items():
        score = 0
        for dim, affinity in data["dimension_affinity"].items():
            score += dimension_scores[dim] * affinity
        personality_scores[personality] = score / len(data["dimension_affinity"])
    
    # เรียงลำดับบุคลิกภาพตามคะแนน
    sorted_personalities = sorted(personality_scores.items(), key=lambda x: x[1], reverse=True)
    
    # บันทึกผลลัพธ์
    st.session_state.results = {
        "dimension_scores": dimension_scores,
        "personality_scores": personality_scores,
        "sorted_personalities": sorted_personalities,
        "primary_personality": sorted_personalities[0][0],
        "secondary_personality": sorted_personalities[1][0] if len(sorted_personalities) > 1 else None,
        "tertiary_personality": sorted_personalities[2][0] if len(sorted_personalities) > 2 else None
    }

def analyze_dimension_with_llm(dimension_name: str, score: float, personality: Dict) -> str:
    """Analyze a dimension using LLM for deeper insights"""
    try:
        if not st.session_state.get('api_key'):
            # Fallback analysis when no API key is available
            fallback_analysis = {
                "Marketing Performance": "คุณมีความสามารถในการวัดผลและติดตามประสิทธิภาพทางการตลาดในระดับปานกลาง ควรเน้นการพัฒนาระบบการวัดผลและการวิเคราะห์ข้อมูลให้ละเอียดขึ้น",
                "Identity Uniqueness": "คุณมีเอกลักษณ์และความแตกต่างในระดับที่ดี ควรพัฒนาต่อยอดจุดแข็งนี้ให้เป็นข้อได้เปรียบทางการแข่งขัน",
                "Competitive Advantage": "คุณมีศักยภาพในการสร้างความได้เปรียบทางการแข่งขันในระดับปานกลาง ควรศึกษาและพัฒนาจุดแข็งที่แตกต่างจากคู่แข่ง",
                "Networking Capability": "คุณมีศักยภาพในการสร้างเครือข่ายที่ยังสามารถพัฒนาได้อีก ควรเพิ่มการมีส่วนร่วมในกิจกรรมเครือข่ายและสร้างความสัมพันธ์ที่ยั่งยืน",
                "Entrepreneurial Marketing": "คุณมีความสามารถในการทำการตลาดแบบผู้ประกอบการในระดับปานกลาง ควรพัฒนาทักษะการมองเห็นโอกาสและการทดลองแนวทางใหม่ๆ"
            }
            return fallback_analysis.get(dimension_name, "")
            
        client = groq.Groq(api_key=st.session_state.api_key)
        
        prompt = f"""
        You are a business strategy expert analyzing a business personality assessment.
        Dimension: {dimension_name}
        Score: {score}
        Personality Type: {personality['thai_name']} ({personality['description']})
        
        Please provide:
        1. A brief analysis of what this score means in the context of this personality type
        2. 2-3 specific strengths this combination suggests
        3. 1-2 potential areas for growth
        4. A practical recommendation for leveraging this dimension
        
        Keep the response concise and actionable.
        """
        
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in LLM analysis: {str(e)}")
        return ""

def analyze_personality_with_llm(personality: Dict, scores: Dict[str, float]) -> str:
    """Analyze the overall personality type using LLM for deeper insights"""
    try:
        if not st.session_state.get('api_key'):
            # Fallback analysis when no API key is available
            return f"""
            บุคลิกภาพ {personality['thai_name']} ของคุณแสดงถึงความสามารถในการ {personality['description']}
            
            จุดแข็งหลักของคุณ:
            - {personality['strengths'][0]}
            - {personality['strengths'][1]}
            - {personality['strengths'][2]}
            
            ข้อเสนอแนะในการพัฒนา:
            1. พัฒนาทักษะการสร้างเครือข่ายและการสื่อสาร
            2. เพิ่มความเข้าใจในตลาดและลูกค้า
            3. พัฒนาความสามารถในการปรับตัวและการเรียนรู้
            """
            
        client = groq.Groq(api_key=st.session_state.api_key)
        
        prompt = f"""
        You are a business strategy expert analyzing a business personality assessment.
        Personality Type: {personality['thai_name']} ({personality['description']})
        Dimension Scores: {json.dumps(scores, indent=2)}
        
        Please provide:
        1. A comprehensive analysis of how this personality type's strengths align with their dimension scores
        2. 2-3 unique business opportunities this combination suggests
        3. Potential challenges and how to address them
        4. Specific recommendations for business growth and development
        
        Keep the response focused on practical business applications.
        """
        
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in LLM analysis: {str(e)}")
        return ""

def show_results(scores: Dict[str, float], personality: Dict):
    """Display quiz results with enhanced LLM analysis"""
    st.title("ผลการประเมินบุคลิกภาพทางธุรกิจ")
    
    # Display personality type
    st.markdown(f"""
    <div class="result-card" style="border-color: {personality['color']};">
        <h2>บุคลิกภาพทางธุรกิจของคุณคือ</h2>
        <h3 style="color: {personality['color']};">{personality['thai_name']}</h3>
        <p>{personality['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display strengths
    st.markdown("""
    <div class="result-card">
        <h3>จุดแข็งของคุณ</h3>
        <ul>
    """, unsafe_allow_html=True)
    for strength in personality['strengths']:
        st.markdown(f"<li>{strength}</li>", unsafe_allow_html=True)
    st.markdown("</ul></div>", unsafe_allow_html=True)
    
    # Display dimension scores with LLM analysis
    st.markdown("""
    <div class="result-card">
        <h3>ผลการประเมินในแต่ละมิติ</h3>
    """, unsafe_allow_html=True)
    
    for dimension, score in scores.items():
        st.markdown(f"""
        <div class="dimensional-highlight">
            <h4>{dimension}</h4>
            <div class="score-bar">
                <div class="score-fill" style="width: {score * 100}%; background-color: {personality['color']};"></div>
                <span class="score-text">{score:.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add LLM analysis for each dimension
        llm_analysis = analyze_dimension_with_llm(dimension, score, personality)
        if llm_analysis:
            st.markdown(f"""
            <div class="llm-insight">
                <h4>การวิเคราะห์เชิงลึก</h4>
                <p>{llm_analysis}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add overall personality analysis from LLM
    llm_personality_analysis = analyze_personality_with_llm(personality, scores)
    if llm_personality_analysis:
        st.markdown(f"""
        <div class="result-card">
            <h3>การวิเคราะห์บุคลิกภาพเชิงลึก</h3>
            <p>{llm_personality_analysis}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Add CSS for new elements
    st.markdown("""
    <style>
    .llm-insight {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #6c757d;
    }
    .llm-insight h4 {
        color: #495057;
        margin-top: 0;
    }
    .llm-insight p {
        color: #212529;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# ฟังก์ชันแสดงผลลัพธ์แบบทดสอบบุคลิกภาพ
def show_results():
    st.title("🔍 การเดินทางของคุณกับ Moradok")
    st.write("")
    
    results = st.session_state.results
    primary_personality = results["primary_personality"]
    primary_data = business_personalities[primary_personality]
    
    # แสดงผลบุคลิกภาพหลัก
    with st.container():
        st.markdown(f"""
        <div class="result-card">
            <h2 style="color: {primary_data['color']};">{primary_data['thai_name']}</h2>
            <h3>{primary_data['description']}</h3>
            <div class="profile-highlight">
                <h4>🔹 จุดแข็งหลักของคุณ:</h4>
                <ul>
                    {''.join([f'<li>{strength}</li>' for strength in primary_data['strengths']])}
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # แสดงบุคลิกภาพรอง
    if results["secondary_personality"]:
        secondary_data = business_personalities[results["secondary_personality"]]
        st.markdown(f"""
        <div class="result-card" style="margin-top: 20px;">
            <h3 style="color: {secondary_data['color']};">บุคลิกภาพรอง: {secondary_data['thai_name']}</h3>
            <p>{secondary_data['description']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # แสดงกราฟมิติต่างๆ
    st.subheader("📊 คะแนนมิติทางธุรกิจของคุณ")
    fig = go.Figure()
    
    dimensions = list(results["dimension_scores"].keys())
    scores = [results["dimension_scores"][dim] * 100 for dim in dimensions]
    
    fig.add_trace(go.Bar(
        x=dimensions,
        y=scores,
        marker_color=['#3498db', '#9b59b6', '#2ecc71', '#e74c3c', '#f39c12'],
        text=[f"{score:.0f}%" for score in scores],
        textposition='auto'
    ))
    
    fig.update_layout(
        yaxis=dict(range=[0, 100], title="คะแนน (%)"),
        xaxis=dict(title="มิติทางธุรกิจ"),
        height=400,
        margin=dict(l=50, r=50, b=100, t=50, pad=4)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # แสดงปุ่มเลือกทำแบบทดสอบต่อไป
    st.write("")
    st.write("คุณสามารถเลือกที่จะ:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧩 ทำแบบทดสอบ Moradok"):
            st.session_state.quiz_selection = "moradok"
            st.session_state.moradok_completed = False
            st.session_state.moradok_current_question = 0
            st.session_state.moradok_answers = []
            st.rerun()
    with col2:
        if st.button("🔄 ทำแบบทดสอบบุคลิกภาพใหม่"):
            st.session_state.quiz_completed = False
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.session_state.results = {}
            st.session_state.user_profile = {}
            st.session_state.question_order = []
            st.rerun()
    with col3:
        if st.button("🏠 กลับไปหน้าแรก"):
            st.session_state.quiz_selection = None
            st.session_state.quiz_completed = False
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.session_state.results = {}
            st.session_state.user_profile = {}
            st.session_state.question_order = []
            st.rerun()

# ฟังก์ชันแสดงแบบทดสอบ Moradok
def show_moradok_quiz():
    st.title("🧩 แบบทดสอบความรู้เกี่ยวกับ Moradok")
    st.write("แบบทดสอบนี้จะช่วยให้คุณเข้าใจแพลตฟอร์ม Moradok มากขึ้น")
    
    # Initialize all required session state variables
    if "moradok_answers" not in st.session_state:
        st.session_state.moradok_answers = []
    if "moradok_current_question" not in st.session_state:
        st.session_state.moradok_current_question = 0
    if "moradok_completed" not in st.session_state:
        st.session_state.moradok_completed = False
    if "show_explanation" not in st.session_state:
        st.session_state.show_explanation = False
    
    if st.session_state.moradok_current_question < len(moradok_questions):
        question = moradok_questions[st.session_state.moradok_current_question]
        
        st.markdown(f"""
        <div class="quiz-card">
            <h3>คำถามที่ {st.session_state.moradok_current_question + 1}/{len(moradok_questions)}</h3>
            <p>{question['question']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.show_explanation:
            st.markdown(f"""
            <div class="result-card" style="margin-top: 20px;">
                <h4>คำอธิบาย:</h4>
                <p>{question['explanation']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("ต่อไป", key="next_question"):
                st.session_state.show_explanation = False
                st.session_state.moradok_current_question += 1
                if st.session_state.moradok_current_question == len(moradok_questions):
                    st.session_state.moradok_completed = True
                st.rerun()
        else:
            for i, option in enumerate(question['options']):
                if st.button(option, key=f"moradok_option_{i}"):
                    st.session_state.moradok_answers.append(i)
                    st.session_state.show_explanation = True
                    st.rerun()
    else:
        show_moradok_results()

# ฟังก์ชันแสดงผลลัพธ์แบบทดสอบ Moradok
def show_moradok_results():
    st.title("🎉 ผลลัพธ์แบบทดสอบ Moradok")
    
    correct_answers = sum(1 for i, answer in enumerate(st.session_state.moradok_answers) 
                         if answer == moradok_questions[i]['correct'])
    score = (correct_answers / len(moradok_questions)) * 100
    
    st.markdown(f"""
    <div class="result-card">
        <h2>คะแนนของคุณ: {score:.0f}%</h2>
        <p>คุณตอบถูก {correct_answers} จาก {len(moradok_questions)} ข้อ</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.write("ขอบคุณที่ทำแบบทดสอบความรู้เกี่ยวกับ Moradok!")
    st.write("คุณสามารถเลือกที่จะ:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌐 ไปที่เว็บไซต์ Moradok"):
            st.markdown("[คลิกที่นี่เพื่อไปที่ Moradok.co](https://moradok.co)")
    with col2:
        if st.button("🧩 ทำแบบทดสอบบุคลิกภาพทางธุรกิจ"):
            st.session_state.quiz_selection = "personality"
            st.session_state.quiz_completed = False
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.session_state.results = {}
            st.session_state.user_profile = {}
            st.session_state.question_order = []
            st.rerun()

def analyze_question_response_with_llm(question: str, answer: str, dimension: str) -> str:
    """Analyze user's response to a specific question using LLM"""
    try:
        if not st.session_state.get('api_key'):
            return ""
            
        client = groq.Groq(api_key=st.session_state.api_key)
        
        prompt = f"""
        You are a business psychology expert analyzing a quiz response.
        Question: {question}
        User's Answer: {answer}
        Dimension: {dimension}
        
        Please provide:
        1. A brief analysis of what this answer reveals about the user's mindset
        2. 1-2 key personality traits this response suggests
        3. How this aligns with the dimension being assessed
        
        Keep the response concise and insightful.
        """
        
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in LLM analysis: {str(e)}")
        return ""

def match_moradok_solutions(personality: Dict, scores: Dict[str, float]) -> str:
    """Match user's personality and scores with Moradok solutions"""
    try:
        if not st.session_state.get('api_key'):
            # Fallback matching when no API key is available
            return f"""
            โซลูชัน Moradok ที่เหมาะกับคุณ:
            
            1. เสาหลัก Your Idea:
            - แบ่งปันความคิดเห็นเกี่ยวกับพื้นที่มรดก
            - มีส่วนร่วมในการพัฒนาพื้นที่ผ่านการเสนอแนวคิดใหม่ๆ
            
            2. เสาหลัก Your Action:
            - เข้าร่วมกิจกรรมอนุรักษ์และพัฒนามรดก
            - เป็นอาสาสมัครในโครงการต่างๆ
            
            3. เสาหลัก Your Fund:
            - สนับสนุนโครงการอนุรักษ์มรดก
            - มีส่วนร่วมในการระดมทุนเพื่อการพัฒนาพื้นที่
            
            ข้อเสนอแนะ:
            - ใช้ความสามารถในการ {personality['strengths'][0]} เพื่อมีส่วนร่วมในโครงการที่เหมาะสม
            - พัฒนาทักษะการสร้างเครือข่ายเพื่อขยายการมีส่วนร่วม
            """
            
        client = groq.Groq(api_key=st.session_state.api_key)
        
        prompt = f"""
        You are a Moradok platform expert matching user profiles with appropriate solutions.
        Personality Type: {personality['thai_name']} ({personality['description']})
        Dimension Scores: {json.dumps(scores, indent=2)}
        
        Based on the user's personality and scores, suggest:
        1. Which Moradok engagement pillar (Your Idea, Your Action, Your Fund) best matches their profile
        2. Specific Moradok solutions or features they might find valuable
        3. How they can contribute to heritage preservation based on their strengths
        4. Potential community roles they could take on
        
        Keep the response focused on practical Moradok applications.
        """
        
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in Moradok matching: {str(e)}")
        return ""

def show_quiz():
    st.title("🧩 แบบทดสอบบุคลิกภาพทางธุรกิจ")
    st.write("แบบทดสอบนี้จะช่วยให้คุณเข้าใจบุคลิกภาพทางธุรกิจของคุณผ่าน 5 มิติหลัก")
    
    questions = get_random_questions()
    total_questions = len(questions)
    
    # สร้าง progress circles
    progress_html = '<div class="progress-container">'
    for i in range(total_questions):
        status = "completed" if i < st.session_state.current_question else "current" if i == st.session_state.current_question else "upcoming"
        progress_html += f'<div class="progress-circle {status}">{i+1}</div>'
    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)
    
    if st.session_state.current_question < total_questions:
        question = questions[st.session_state.current_question]
        
        st.markdown(f"""
        <div class="quiz-card">
            <h3>คำถามที่ {st.session_state.current_question + 1}/{total_questions}</h3>
            <p>{question['question']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, option in enumerate(question['options']):
            if st.button(option, key=f"option_{i}"):
                st.session_state.answers.append(i)
                
                # Add LLM analysis for this response
                if st.session_state.get('api_key'):
                    analysis = analyze_question_response_with_llm(
                        question['question'],
                        option,
                        question['dimension']
                    )
                    if analysis:
                        st.markdown(f"""
                        <div class="llm-insight">
                            <h4>การวิเคราะห์คำตอบของคุณ</h4>
                            <p>{analysis}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.session_state.current_question += 1
                if st.session_state.current_question == total_questions:
                    st.session_state.quiz_completed = True
                    calculate_results()
                st.rerun()
    else:
        show_results()

def show_results(scores: Dict[str, float], personality: Dict):
    """Display quiz results with enhanced LLM analysis and Moradok matching"""
    st.title("ผลการประเมินบุคลิกภาพทางธุรกิจ")
    
    # Create two columns for personality info and radar chart
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Display personality type
        st.markdown(f"""
        <div class="result-card" style="border-color: {personality['color']};">
            <h2>บุคลิกภาพทางธุรกิจของคุณคือ</h2>
            <h3 style="color: {personality['color']};">{personality['thai_name']}</h3>
            <p>{personality['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display strengths
        st.markdown("""
        <div class="result-card">
            <h3>จุดแข็งของคุณ</h3>
            <ul>
        """, unsafe_allow_html=True)
        for strength in personality['strengths']:
            st.markdown(f"<li>{strength}</li>", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)
        
        # Add overall personality analysis from LLM
        llm_personality_analysis = analyze_personality_with_llm(personality, scores)
        if llm_personality_analysis:
            st.markdown(f"""
            <div class="result-card">
                <h3>การวิเคราะห์บุคลิกภาพเชิงลึก</h3>
                <p>{llm_personality_analysis}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Add Moradok solution matching
        moradok_matching = match_moradok_solutions(personality, scores)
        if moradok_matching:
            st.markdown(f"""
            <div class="result-card" style="border-color: #4CAF50;">
                <h3>🎯 โซลูชัน Moradok ที่เหมาะกับคุณ</h3>
                <p>{moradok_matching}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Create radar chart for dimension scores
        st.markdown("""
        <div class="result-card">
            <h3>ผลการประเมินในแต่ละมิติ</h3>
        """, unsafe_allow_html=True)
        
        # Prepare data for radar chart
        dimensions = list(scores.keys())
        scores_values = [scores[dim] * 100 for dim in dimensions]  # Convert to percentage
        
        # Create radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=scores_values,
            theta=dimensions,
            fill='toself',
            name='คะแนนของคุณ',
            line_color=personality['color']
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=12),
                    tickangle=0
                ),
                angularaxis=dict(
                    tickfont=dict(size=14)
                )
            ),
            showlegend=False,
            height=400,
            margin=dict(l=50, r=50, b=50, t=50, pad=4),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display detailed scores and LLM analysis for each dimension
        st.markdown("""
        <div class="result-card">
            <h3>การวิเคราะห์เชิงลึกในแต่ละมิติ</h3>
        """, unsafe_allow_html=True)
        
        for dimension, score in scores.items():
            st.markdown(f"""
            <div class="dimensional-highlight">
                <h4>{dimension}</h4>
                <div class="score-bar">
                    <div class="score-fill" style="width: {score * 100}%; background-color: {personality['color']};"></div>
                    <span class="score-text">{score:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add LLM analysis for each dimension
            llm_analysis = analyze_dimension_with_llm(dimension, score, personality)
            if llm_analysis:
                st.markdown(f"""
                <div class="llm-insight">
                    <h4>การวิเคราะห์เชิงลึก</h4>
                    <p>{llm_analysis}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Add navigation buttons
    st.markdown("""
    <div class="navigation-buttons">
        <div class="button-container">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("กลับไปหน้าหลัก", key="back_to_main"):
            st.session_state.quiz_selection = None
            st.session_state.personality_answers = {}
            st.session_state.personality_current_question = 0
            st.session_state.personality_completed = False
            st.rerun()
    
    with col2:
        if st.button("กลับไป Moradok Quiz", key="back_to_moradok"):
            st.session_state.quiz_selection = "moradok"
            st.session_state.moradok_answers = {}
            st.session_state.moradok_current_question = 0
            st.session_state.moradok_completed = False
            st.rerun()
    
    with col3:
        if st.button("ทำแบบทดสอบใหม่", key="retake_quiz"):
            st.session_state.personality_answers = {}
            st.session_state.personality_current_question = 0
            st.session_state.personality_completed = False
            st.rerun()
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add CSS for new elements
    st.markdown("""
    <style>
    .navigation-buttons {
        margin-top: 30px;
        text-align: center;
    }
    .button-container {
        display: flex;
        justify-content: center;
        gap: 15px;
        flex-wrap: wrap;
    }
    .nav-button {
        background-color: #4CAF50;
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 25px;
        cursor: pointer;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .nav-button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .nav-button:active {
        transform: translateY(0);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .llm-insight {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #6c757d;
    }
    .llm-insight h4 {
        color: #495057;
        margin-top: 0;
    }
    .llm-insight p {
        color: #212529;
        line-height: 1.6;
    }
    .score-bar {
        width: 100%;
        height: 20px;
        background-color: #f0f0f0;
        border-radius: 10px;
        margin: 10px 0;
        position: relative;
    }
    .score-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    .score-text {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        color: #fff;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# ฟังก์ชันแสดงหน้าเลือกแบบทดสอบ
def show_quiz_selection():
    st.title("🧩 ยินดีต้อนรับสู่แพลตฟอร์ม Moradok")
    st.write("เลือกแบบทดสอบที่คุณต้องการทำ:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="quiz-card" style="text-align: center; padding: 20px;">
            <h3>แบบทดสอบความรู้เกี่ยวกับ Moradok</h3>
            <p>เรียนรู้เกี่ยวกับแพลตฟอร์ม Moradok และวิธีการมีส่วนร่วมในการอนุรักษ์และพัฒนามรดกชุมชน</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("เริ่มทำแบบทดสอบ Moradok", key="moradok_quiz"):
            st.session_state.quiz_selection = "moradok"
            st.session_state.moradok_completed = False
            st.session_state.moradok_current_question = 0
            st.session_state.moradok_answers = []
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="quiz-card" style="text-align: center; padding: 20px;">
            <h3>แบบทดสอบบุคลิกภาพทางธุรกิจ</h3>
            <p>ค้นพบบุคลิกภาพทางธุรกิจของคุณผ่าน 5 มิติหลัก และรับคำแนะนำเฉพาะบุคคล</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("เริ่มทำแบบทดสอบบุคลิกภาพ", key="personality_quiz"):
            st.session_state.quiz_selection = "personality"
            st.session_state.quiz_completed = False
            st.session_state.current_question = 0
            st.session_state.answers = []
            st.session_state.results = {}
            st.session_state.user_profile = {}
            st.session_state.question_order = []
            st.rerun()

# ฟังก์ชันหลัก
def main():
    if "quiz_selection" not in st.session_state:
        st.session_state.quiz_selection = None
    
    if st.session_state.quiz_selection is None:
        show_quiz_selection()
    elif st.session_state.quiz_selection == "moradok":
        if not st.session_state.moradok_completed:
            show_moradok_quiz()
        else:
            show_moradok_results()
    elif st.session_state.quiz_selection == "personality":
        if not st.session_state.quiz_completed:
            show_quiz()
        else:
            # Get the results from session state
            results = st.session_state.results
            primary_personality = results["primary_personality"]
            personality_data = business_personalities[primary_personality]
            
            # Call show_results with the required arguments
            show_results(results["dimension_scores"], personality_data)

if __name__ == "__main__":
    main()
