import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])

if uploaded_file:
    # 使用 gbk 编码读取
    df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    try:
        # --- 基础行定位 ---
        # 寻找 Repo 表起始行
        repo_idx = df[df[0] == "Repo"].index[0]
        
        # --- 1. Repo 市场分析 ---
        # 根据 snippet，Repo 数据从 repo_idx + 2 开始，共 7 行 (O/N 到 3M)
        repo_df = df.iloc[repo_idx+2 : repo_idx+9].copy()
        repo_df.columns = ["期限", "开盘买", "开盘卖", "变动", "收盘买", "收盘卖"]
        
        # 计算变动趋势
        avg_change = pd.to_numeric(repo_df["变动"], errors='coerce').mean()
        repo_trend_desc = f"{'上行' if avg_change >= 0 else '下行'}于 {abs(round(avg_change, 1))} bps"
        
        # 判断收紧/转松: 开盘买价 vs 收盘买价
        open_bids = pd.to_numeric(repo_df["开盘买"], errors='coerce')
        close_bids = pd.to_numeric(repo_df["收盘买"], errors='coerce')
        repo_status = "转松" if open_bids.mean() > close_bids.mean() else "收紧"
        repo_diff = (close_bids - open_bids).mean()
        
        # --- 2. 报告生成 ---
        yesterday = datetime.now() - timedelta(days=1)
        
        # 手动拼接 Markdown 表格 (无需 tabulate)
        table_md = "| 期限 | 开盘买价 | 收盘买价 | 变动(bps) |\n|---|---|---|---|\n"
        for _, row in repo_df.iterrows():
            table_md += f"| {row['期限']} | {row['开盘买']} | {row['收盘买']} | {row['变动']} |\n"

        report = f"""
### 离岸央票市场简报 {yesterday.strftime("%Y年%m月%d日")}

**第三部分：香港离岸人民币回购市场**
人民币回购市场方面，今日开盘离岸人民币回购利率各期限与上一交易日开盘时相比{repo_trend_desc}。今日日内离岸人民币资金整体小幅{repo_status}，收盘时各期限与开盘水平相比上行 {abs(round(repo_diff, 1))} bps以内。今日我行有 [请填入] 亿离岸人民币回购成交。以下是比较活跃期限之我行开价及波幅：

{table_md}
"""
        st.markdown(report)
        st.download_button("下载报告", report, file_name="央票简报.md")
        
    except Exception as e:
        st.error(f"处理数据出错，请检查 CSV 格式。错误详情: {e}")