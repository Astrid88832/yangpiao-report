import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="央票自动化工具", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv", type=["csv"])

if uploaded_file is not None:
    # 强制重置指针并使用 gbk 编码读取
    uploaded_file.seek(0)
    try:
        # 使用 gbk 编码读取，因为文件中包含中文
        df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
        
        # --- 数据处理 ---
        # 根据你提供的文件结构，Repo 就在第一行，数据从第3行开始
        repo_df = df.iloc[2:9].copy()
        repo_df.columns = ["期限", "开盘买", "开盘卖", "变动", "收盘买", "收盘卖"]
        
        # 逻辑计算
        repo_df["变动"] = pd.to_numeric(repo_df["变动"], errors='coerce').fillna(0)
        avg_change = repo_df["变动"].mean()
        repo_trend = f"{'上行' if avg_change >= 0 else '下行'}于 {abs(round(avg_change, 1))} bps"
        
        # 生成 Markdown 表格
        table_md = "| 期限 | 开盘买价(%) | 开盘卖价(%) | 变动(bps) | 收盘买价(%) | 收盘卖价(%) |\n"
        table_md += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
        for _, row in repo_df.iterrows():
            table_md += f"| {row['期限']} | {row['开盘买']} | {row['开盘卖']} | {row['变动']} | {row['收盘买']} | {row['收盘卖']} |\n"
            
        # 生成报告
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
        st.write("如果依然报错，请确认该 CSV 文件是否直接从 Excel 导出（Excel 默认使用 GBK 编码）。")