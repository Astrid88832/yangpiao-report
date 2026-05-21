import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])
econ_news = st.text_area("请输入今晚的经济数据简述:", value="周五晚间无重要经济数据公布")

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    try:
        # --- 基础数据定位 ---
        start_row_yield = df[df[1] == "Implied yield table"].index[0]
        row_repo = df[df[1] == "Repo"].index[0]

        # --- 第一/二段逻辑 (同前) ---
        # [此处省略第一/二段逻辑以保持简洁，实际使用时请保留完整变量]
        # 假设 liquidity_status, trend_word, etc. 已计算
        
        # --- 第三段：香港离岸人民币回购市场 ---
        # 1. 整体上行/下行 (较上一日开盘)
        repo_data = df.iloc[row_repo+2:row_repo+6, :] # 假设Repo表有4行活跃期限
        repo_diff_avg = repo_data[3].mean() # 假设第4列(索引3)是日内变动
        repo_trend = f"{'上行' if repo_diff_avg > 0 else '下行'}于 {abs(round(repo_diff_avg, 1))} bps"
        
        # 2. 收紧/转松判断 (收盘 vs 开盘)
        open_bid = float(df.iat[row_repo+2, 2]) # 假设第3列(索引2)是开盘买价
        close_bid = float(df.iat[row_repo+2, 4]) # 假设第5列(索引4)是收盘买价
        repo_status = "转松" if open_bid > close_bid else "收紧"
        
        # 3. 统计汇总
        repo_report = f"""
**第三部分：香港离岸人民币回购市场**
人民币回购市场方面，今日开盘离岸人民币回购利率各期限与上一交易日开盘时相比{repo_trend}。今日日内离岸人民币资金整体小幅{repo_status}，收盘时各期限与开盘水平相比上行 {abs(round(close_bid - open_bid, 1))} bps以内。今日我行有 [请填入] 亿离岸人民币回购成交。以下是比较活跃期限之我行开价及波幅：
"""

        # --- 表格生成 ---
        # 提取 Implied yield table
        yield_table = df.iloc[start_row_yield:start_row_yield+9, 1:4]
        
        # --- 5. 完整报告生成 ---
        report = f"""
### 离岸央票市场简报 {date_str}
... [此处插入之前的段落] ...

{repo_report}

**活跃期限报价表：**
{yield_table.to_markdown(index=False, header=False)}

**隐含收益率明细表：**
{yield_table.to_markdown(index=False, header=False)}
"""
        st.markdown(report)
        st.download_button("下载报告", report, file_name="央票简报.md")

    except Exception as e:
        st.error(f"处理数据出错: {e}")