import streamlit as st
import pandas as pd
from docx import Document
import google.generativeai as genai
from io import BytesIO

import streamlit as st
import pandas as pd

# 页面基础设置
st.set_page_config(page_title="央票数据提炼助手", page_icon="📈")
st.title("📈 央票数据提炼与报告助手")
st.write("请上传您的 CSV 数据文件，我们将为您生成投喂给 QClaw 的指令。")

# 文件上传组件
uploaded_file = st.file_uploader("选择一个 CSV 文件", type=["csv"])

if uploaded_file is not None:
    # 1. 读取 Excel/CSV 数据
    try:
        df = pd.read_csv(uploaded_file, encoding='gbk')
        st.success("数据读取成功！")
        
        # 显示数据概览
        st.write("### 数据概览：")
        st.dataframe(df.head())
        
        # 2. 自动提炼核心内容（将数据转化为纯文本）
        # 这里使用 df.to_string() 确保所有数值都能被 AI 识别
        data_string = df.to_string(index=False)
        
        # 3. 生成投喂指令 (QClaw 专用提示词)
        prompt_for_qclaw = f"""
请扮演金融分析师，根据以下央票市场数据撰写一份专业简报：

【市场数据】
{data_string}

【撰写要求】
1. 分析市场趋势（如利率变动、流动性情况）。
2. 用专业的金融术语总结核心结论。
3. 如果数据中有异常波动，请特别指出。
4. 语言简洁，结构清晰，适合在内部工作群中发布。
"""
        
        # 4. UI 展示与复制功能
        st.subheader("💡 复制以下指令投喂给 QClaw：")
        st.text_area("直接复制下面的内容：", value=prompt_for_qclaw, height=400)
        
        st.info("提示：请全选上方文本框内容，点击右键复制，然后粘贴到 QClaw 对话窗口中即可生成报告。")

    except Exception as e:
        st.error(f"读取文件时出错：{e}")
        st.write("请检查 CSV 文件格式是否正确。")
else:
    st.warning("请上传数据文件以开始工作。")