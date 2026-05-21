import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv", type=["csv"])

if uploaded_file:
    # 使用 utf-8-sig 编码（适合 Excel 导出的 CSV）
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig', header=None)
    
    try:
        # --- 1. 定位 Repo 表 ---
        # 根据读取结果，Repo 在第一列的第0行
        repo_idx = df[df[0] == "Repo"].index[0]
        
        # 读取 Repo 数据区域: 期限, 开盘买, 开盘卖, 变动, 收盘买, 收盘卖
        # 数据从 repo_idx + 2 开始
        repo_df = df.iloc[repo_idx+2 : repo_idx+9].copy()
        repo_df.columns = ["期限", "开盘买", "开盘卖", "变动", "收盘买", "收盘卖"]
        
        # --- 2. 逻辑计算 ---
        avg_change = pd.to_numeric(repo_df["变动"], errors='coerce').mean()
        repo_trend = f"{'上行' if avg_change >= 0 else '下行'}于 {abs(round(avg_change, 1))} bps"
        
        # 资金松紧判断: 开盘买价 vs 收盘买价
        open_bids = pd.to_numeric(repo_df["开盘买"], errors='coerce')
        close_bids = pd.to_numeric(repo_df["收盘买"], errors='coerce')
        repo_status = "转松" if open_bids.mean() > close_bids.mean() else "收紧"
        
        # --- 3. 生成表格 Markdown ---
        table_md = "| 期限 | 开盘买价(%) | 开盘卖价(%) | 变动(bps) | 收盘买价(%) | 收盘卖价(%) |\n"
        table_md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for _, row in repo_df.iterrows():
            table_md += f"| {row['期限']} | {row['开盘买']} | {row['开盘卖']} | {row['变动']} | {row['收盘买']} | {row['收盘卖']} |\n"

        # --- 4. 生成完整报告 ---
        yesterday = datetime.now() - timedelta(days=1)
        report = f"""
### 离岸央票市场简报 {yesterday.strftime("%Y年%m月%d日")}

**第三部分：香港离岸人民币回购市场**
人民币回购市场方面，今日开盘离岸人民币回购利率各期限与上一交易日开盘时相比{repo_trend}。今日日内离岸人民币资金整体小幅{repo_status}。今日我行有 [请填入] 亿离岸人民币回购成交。以下是比较活跃期限之我行开价及波幅：

{table_md}
"""
        st.markdown(report)
        st.download_button("下载报告", report, file_name="央票简报.md")
        
    except Exception as e:
        st.error(f"处理数据出错: {e}")