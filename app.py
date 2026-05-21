import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])
if uploaded_file:
    # 1. 鲁棒的读取逻辑
    encodings = ['utf-8-sig', 'gbk', 'gb18030']
    df = None
    for enc in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc, header=None)
            break
        except: continue

    if df is not None:
        try:
            # 2. 定位 Repo 表并生成报告
            repo_idx = df[df[0] == "Repo"].index[0]
            repo_df = df.iloc[repo_idx+2 : repo_idx+9].copy()
            repo_df.columns = ["期限", "开盘买", "开盘卖", "变动", "收盘买", "收盘卖"]
            
            # Markdown 表格生成
            table_md = "| 期限 | 开盘买价(%) | 开盘卖价(%) | 变动(bps) | 收盘买价(%) | 收盘卖价(%) |\n|---|---|---|---|---|---|\n"
            for _, row in repo_df.iterrows():
                table_md += f"| {row['期限']} | {row['开盘买']} | {row['开盘卖']} | {row['变动']} | {row['收盘买']} | {row['收盘卖']} |\n"

            # 报告拼接
            report = f"""
### 离岸央票市场简报 {datetime.now().strftime("%Y年%m月%d日")}

**第一段：市场概览**
(此处补充你的概览逻辑)

**第二段：货币市场流动性**
(此处补充你的流动性逻辑)

**第三部分：香港离岸人民币回购市场**
人民币回购市场方面... (保持你之前的文案)

{table_md}
"""
            st.markdown(report)
            st.download_button("下载报告", report, file_name="央票简报.md")
        except Exception as e:
            st.error(f"处理数据失败: {e}")
    else:
        st.error("无法识别文件编码。")