import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="央票自动化工具", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv", type=["csv"])

if uploaded_file is not None:
    # 关键点：每次读取前重置指针
    uploaded_file.seek(0)
    
    try:
        # 1. 直接读取，不带 header
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig', header=None)
        
        # 2. 定位 Repo：因为它是文件的第一行
        # 根据你的 snippet，df.iloc[0, 0] 就是 'Repo'
        repo_idx = 0 
        
        # 3. 读取 Repo 数据 (从第3行开始读取 7 行)
        repo_df = df.iloc[repo_idx+2 : repo_idx+9].copy()
        repo_df.columns = ["期限", "开盘买", "开盘卖", "变动", "收盘买", "收盘卖"]
        
        # 4. 逻辑计算 (将数据转为数值)
        repo_df["变动"] = pd.to_numeric(repo_df["变动"], errors='coerce').fillna(0)
        avg_change = repo_df["变动"].mean()
        repo_trend = f"{'上行' if avg_change >= 0 else '下行'}于 {abs(round(avg_change, 1))} bps"
        
        # 5. 生成 Markdown 表格
        table_md = "| 期限 | 开盘买价(%) | 开盘卖价(%) | 变动(bps) | 收盘买价(%) | 收盘卖价(%) |\n"
        table_md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for _, row in repo_df.iterrows():
            table_md += f"| {row['期限']} | {row['开盘买']} | {row['开盘卖']} | {row['变动']} | {row['收盘买']} | {row['收盘卖']} |\n"
            
        # 6. 生成报告
        report = f"""
### 离岸央票市场简报 {datetime.now().strftime("%Y年%m月%d日")}

**第三部分：香港离岸人民币回购市场**
人民币回购市场方面，今日开盘离岸人民币回购利率各期限与上一交易日开盘时相比{repo_trend}。今日日内离岸人民币资金整体小幅波动，今日我行有 [请填入] 亿离岸人民币回购成交。以下是比较活跃期限之我行开价及波幅：

{table_md}
"""
        st.markdown(report)
        st.download_button("下载报告", report, file_name="央票简报.md")
        
    except Exception as e:
        st.error(f"处理数据出错: {e}")
        st.write("请检查文件是否为标准 CSV 格式。")