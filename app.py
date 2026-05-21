import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])
econ_news = st.text_area("请输入今晚的经济数据简述:", value="周五晚间无重要经济数据公布")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    except:
        df = pd.read_csv(uploaded_file, encoding='utf-8', header=None)
    
    try:
        # --- 1. 日期逻辑 ---
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y年%m月%d日")
        weekday_map = {0:"周一", 1:"周二", 2:"周三", 3:"周四", 4:"周五", 5:"周六", 6:"周日"}
        weekday_str = weekday_map[yesterday.weekday()]

        # --- 2. 搜索逻辑 (兼容可能存在的空格) ---
        def get_idx(keyword):
            mask = df[0].astype(str).str.contains(keyword, na=False)
            return df.index[mask][0]

        # --- 第一部分：市场概览 ---
        row_10y = get_idx("10Y UST")
        ten_year_yield = float(df.iat[row_10y, 2])
        ten_year_bps = float(df.iat[row_10y, 3])
        
        # --- 第二部分：货币市场 ---
        row_yield = get_idx("Implied yield table")
        # 资金利率基调：读取前8行变动值均值
        yield_changes = pd.to_numeric(df.iloc[row_yield+2:row_yield+10, 3], errors='coerce')
        if all(yield_changes > 0): liquidity_status = "收紧"
        elif all(yield_changes < 0): liquidity_status = "转松"
        else: liquidity_status = "变化不大"
        
        # --- 第三部分：Repo 市场 ---
        row_repo = get_idx("Repo")
        repo_df = df.iloc[row_repo+2 : row_repo+9].copy()
        repo_df.columns = ["期限", "开盘买", "开盘卖", "变动", "收盘买", "收盘卖"]
        
        avg_change = pd.to_numeric(repo_df["变动"], errors='coerce').mean()
        repo_trend_desc = f"{'上行' if avg_change >= 0 else '下行'}于 {abs(round(avg_change, 1))} bps"
        
        # 构建 Markdown 表格
        table_md = "| 期限 | 开盘买价 | 开盘卖价 | 变动(bps) | 收盘买价 | 收盘卖价 |\n|---|---|---|---|---|---|\n"
        for _, row in repo_df.iterrows():
            table_md += f"| {row['期限']} | {row['开盘买']} | {row['开盘卖']} | {row['变动']} | {row['收盘买']} | {row['收盘卖']} |\n"

        # --- 报告拼接 ---
        report = f"""
### 离岸央票市场简报 {date_str}

**第一段：市场概览**
{weekday_str}晚间{econ_news}。美债收益率曲线在纽约时段整体{"上行" if ten_year_bps > 0 else "下行"}，10年期美债收益率较上一交易日{"上行" if ten_year_bps > 0 else "下行"}{abs(ten_year_bps)} bps，收于{ten_year_yield}%。

**第二段：离岸人民币货币市场与流动性观测**
今日离岸人民币资金利率整体{liquidity_status}。

**第三部分：香港离岸人民币回购市场**
人民币回购市场方面，今日开盘离岸人民币回购利率各期限与上一交易日开盘时相比{repo_trend_desc}。今日日内离岸人民币资金整体小幅波动，收盘时各期限与开盘水平相比波动幅度均在 bps 以内。今日我行有 [请填入] 亿离岸人民币回购成交。以下是比较活跃期限之我行开价及波幅：

{table_md}
"""
        st.subheader("✅ 生成报告内容：")
        st.markdown(report)
        st.download_button("下载报告", report, file_name=f"央票简报_{yesterday.strftime('%Y%m%d')}.md")
        
    except Exception as e:
        st.error(f"坐标定位出错，请检查 CSV 格式。错误详情: {e}")