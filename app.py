import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])
econ_news = st.text_area("请输入今晚的经济数据简述:", value="周五晚间无重要经济数据公布")

if uploaded_file:
    # 强制使用 utf-8-sig 编码读取以处理 BOM 字符
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig', header=None)
    
    try:
        # --- 1. 日期逻辑 ---
        yesterday = datetime.now() - timedelta(days=1)
        
        # --- 2. 稳健定位 Repo 表 (核心修复) ---
        # 查找第一列中包含 'Repo' 字符的行
        mask = df[0].astype(str).str.contains("Repo", na=False)
        if not mask.any():
            st.error("未找到 'Repo' 标签，请检查 CSV 内容。")
            st.stop()
        
        repo_idx = df.index[mask][0]
        
        # 读取 Repo 表: 从标签下两行开始 (根据 Snippet)
        # 期限, 开盘买, 开盘卖, 变动, 收盘买, 收盘卖
        repo_df = df.iloc[repo_idx+2 : repo_idx+9].copy()
        repo_df.columns = ["期限", "开盘买", "开盘卖", "变动", "收盘买", "收盘卖"]
        
        # --- 3. 计算逻辑 ---
        # 清洗变动数据 (转为 float)
        repo_df["变动"] = pd.to_numeric(repo_df["变动"], errors='coerce').fillna(0)
        avg_change = repo_df["变动"].mean()
        repo_trend_desc = f"{'上行' if avg_change >= 0 else '下行'}于 {abs(round(avg_change, 1))} bps"
        
        # --- 4. 生成报告 ---
        # 构建 Markdown 表格
        table_md = "| 期限 | 开盘买价(%) | 开盘卖价(%) | 变动(bps) | 收盘买价(%) | 收盘卖价(%) |\n"
        table_md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for _, row in repo_df.iterrows():
            table_md += f"| {row['期限']} | {row['开盘买']} | {row['开盘卖']} | {row['变动']} | {row['收盘买']} | {row['收盘卖']} |\n"
            
        report = f"""
### 离岸央票市场简报 {yesterday.strftime("%Y年%m月%d日")}

**第三部分：香港离岸人民币回购市场**
人民币回购市场方面，今日开盘离岸人民币回购利率各期限与上一交易日开盘时相比{repo_trend_desc}。今日日内离岸人民币资金整体小幅波动，收盘时各期限与开盘水平相比波动幅度均在 bps 以内。今日我行有 [请填入] 亿离岸人民币回购成交。以下是比较活跃期限之我行开价及波幅：

{table_md}
"""
        st.markdown(report)
        st.download_button("下载报告", report, file_name="央票简报.md")
        
    except Exception as e:
        st.error(f"处理出错: {e}")