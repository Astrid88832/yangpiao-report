import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])
econ_news = st.text_area("请输入今晚的经济数据简述:", value="周五晚间无重要经济数据公布")

if uploaded_file:
    # 尝试多种编码读取
    try:
        df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    except:
        df = pd.read_csv(uploaded_file, encoding='utf-8', header=None)
    
    try:
        # --- 基础工具函数 ---
        def get_row_by_first_col(df, keyword):
            return df[df[0] == keyword].index[0]
        
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y年%m月%d日")
        
        # --- 1. 第一/二段数据定位 (逻辑保持) ---
        # (此处省略逻辑，确保您之前的段落代码已整合)
        
        # --- 3. 第三部分：香港离岸人民币回购市场 ---
        repo_idx = get_row_by_first_col(df, "Repo")
        # 读取 Repo 数据区域 (从 Repo 标题下两行开始，O/N 到 3M)
        # 列索引：1=开盘买价, 3=变动(bps), 4=收盘买价
        repo_data = df.iloc[repo_idx+2 : repo_idx+9].copy()
        repo_data.columns = ["期限", "开盘买", "开盘卖", "变动", "收盘买", "收盘卖"]
        
        # 变动趋势计算 (基于 Column 3: 变动)
        avg_change = pd.to_numeric(repo_data["变动"], errors='coerce').mean()
        repo_trend_desc = f"{'上行' if avg_change >= 0 else '下行'}于 {abs(round(avg_change, 1))} bps"
        
        # 收紧/转松计算 (基于收盘买价 vs 开盘买价)
        # 注意: O/N 可能是 NA，需剔除
        valid_repo = repo_data.dropna(subset=["收盘买", "开盘买"])
        open_bids = pd.to_numeric(valid_repo["开盘买"])
        close_bids = pd.to_numeric(valid_repo["收盘买"])
        
        # 如果开盘买价 > 收盘买价，则转松；否则收紧
        repo_status = "转松" if open_bids.mean() > close_bids.mean() else "收紧"
        repo_diff = (close_bids - open_bids).mean()
        
        # --- 4. 生成报告 ---
        repo_section = f"""
**第三部分：香港离岸人民币回购市场**
人民币回购市场方面，今日开盘离岸人民币回购利率各期限与上一交易日开盘时相比{repo_trend_desc}。今日日内离岸人民币资金整体小幅{repo_status}，收盘时各期限与开盘水平相比上行 {abs(round(repo_diff, 1))} bps以内。今日我行有 [请填入] 亿离岸人民币回购成交。以下是比较活跃期限之我行开价及波幅：

| 期限 | 开盘买价 | 收盘买价 | 变动(bps) |
| :--- | :--- | :--- | :--- |
{valid_repo[['期限', '开盘买', '收盘买', '变动']].to_markdown(index=False, header=False)}
"""
        
        # 汇总合并
        final_report = f"### 离岸央票市场简报 {date_str}\n\n[此处填入您的前两段内容]\n\n{repo_section}"
        
        st.subheader("✅ 生成报告内容：")
        st.markdown(final_report)
        st.download_button("下载报告", final_report, file_name=f"央票简报_{yesterday.strftime('%Y%m%d')}.md")
        
    except Exception as e:
        st.error(f"处理数据出错，请检查 CSV 格式是否包含 'Repo' 标签。错误详情: {e}")