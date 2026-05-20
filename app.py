import streamlit as st
import pandas as pd
from docx import Document
import google.generativeai as genai
from io import BytesIO

# 1. 设置 API (请替换成你在 Google AI Studio 获取的 Key)
genai.configure(api_key="在此处粘贴你的API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="央票报告生成器", layout="wide")
st.title("📊 离岸央票市场简报自动化生成系统")

uploaded_file = st.file_uploader("请上传每日的 'Yangpiao data.xlsx' (CSV格式)", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file,encoding='gbk')
    st.success("数据读取成功！")
    
    if st.button("🚀 生成今日简报"):
        # 提取关键数据用于 AI 分析
        # 对应你 Excel 第一段的数据：美债、美元指数、USD/CNH
        us_rate = df.iloc[3, 2] 
        usd_cnh = df.iloc[7, 2]
        
        analysis_prompt = f"请作为金融分析师，基于以下关键数据撰写一份《离岸央票市场简报》的“市场概况”段落。数据：10年美债收益率{us_rate}%, USD/CNH为{usd_cnh}。要求专业、简洁。"
        
        with st.spinner('AI 正在撰写报告...'):
            report_text = model.generate_content(analysis_prompt).text
        
        # 填充到 Word
        doc = Document()
        doc.add_heading('离岸央票市场简报', 0)
        doc.add_paragraph(report_text)
        
        buffer = BytesIO()
        doc.save(buffer)
        
        st.download_button("📥 下载 Word 报告", data=buffer.getvalue(), file_name="离岸央票市场简报.docx")