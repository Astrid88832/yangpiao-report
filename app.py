import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])
econ_news = st.text_area("请输入今晚的经济数据简述:", value="周五晚间无重要经济数据公布")

if uploaded_file:
    # 尝试使用 gbk 编码读取
    try:
        df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    except:
        df = pd.read_csv(uploaded_file, encoding='utf-8', header=None)
    
    try:
        # --- 1. 日期与通用变量 ---
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y年%m月%d日")
        weekday_map = {0:"周一", 1:"周二", 2:"周三", 3:"周四", 4:"周五", 5:"周六", 6:"周日"}
        weekday_str = weekday_map[yesterday.weekday()]

        # --- 2. 基础数据定位逻辑 ---
        def get_val(keyword, col_idx, row_offset=0):
            row_idx = df[df[0] == keyword].index[0]
            return float(df.iat[row_idx + row_offset, col_idx])

        # --- 3. 市场概览数据 ---
        # 假设 10Y UST 在第一列
        row_10y = df[df[0] == "10Y UST"].index[0]
        ten_year_yield = float(df.iat[row_10y, 2])
        ten_year_bps = float(df.iat[row_10y, 3])
        
        # --- 4. Repo 市场数据抓取与表格构建 ---
        repo_idx = df[df[0] == "Repo"].index[0]
        # 提取 Repo 数据: 期限, 开盘买, 开盘卖, 变动, 收盘买, 收盘卖
        repo_df = df.iloc[repo_idx+2 : repo_idx+9].copy()
        repo_df.columns = ["期限", "开盘买", "开盘卖", "变动", "收盘买", "收盘卖"]
        
        # 计算逻辑
        avg_change = pd.to_numeric(repo_df["变动"], errors='coerce').mean()
        repo_trend_desc = f"{'上行' if avg_change >= 0 else '下行'}于 {abs(round(avg_change, 1))} bps"
        
        # 生成 Markdown 表格字符串 (匹配截图样式)
        table_md = "| 期限 | 开盘买价(%) | 开盘卖价(%) | 变动(bps) | 收盘买价(%) | 收盘卖价(%) |\n"
        table_md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for _, row in repo_df.iterrows():
            table_md += f"| {row['期限']} | {row['开盘买']} | {row['开盘卖']} | {row['变动']} | {row['收盘买']} | {row['收盘卖']} |\n"
        
        # --- 5. 完整报告拼接 ---
        report = f"""
### 离岸央票市场简报 {date_str}

**第一段：市场概览**
{weekday_str}晚间{econ_news}。美债收益率曲线在纽约时段整体{"上行" if ten_year_bps > 0 else "下行"}，10年期美债收益率较上一交易日{"上行" if ten_year_bps > 0 else "下行"}{abs(ten_year_bps)} bps，收于{ten_year_yield}%。

**第三部分：香港离岸人民币回购市场**
人民币回购市场方面，今日开盘离岸人民币回购利率各期限与上一交易日开盘时相比{repo_trend_desc}。今日日内离岸人民币资金整体小幅波动，收盘时各期限与开盘水平相比波动幅度均在 bps 以内。今日我行有 [请填入] 亿离岸人民币回购成交。以下是比较活跃期限之我行开价及波幅：

{table_md}
"""
        st.subheader("✅ 生成报告内容：")
        st.markdown(report)
        st.download_button("下载报告", report, file_name=f"央票简报_{yesterday.strftime('%Y%m%d')}.md")
        
    except Exception as e:
        st.error(f"坐标定位出错，请检查 CSV 格式是否包含 'Repo' 等关键词。详细错误: {e}")