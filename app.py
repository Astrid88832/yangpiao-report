import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 CSV", type=["csv"])

# --- 辅助函数：模糊查找行 ---
def find_row_by_keyword(df, keyword):
    # 查找包含关键词的行，不区分大小写，自动处理空格
    mask = df.iloc[:, 1].astype(str).str.contains(keyword, case=False, na=False)
    if mask.any():
        return mask.idxmax()
    return None

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    try:
        # --- 1. 日期逻辑 ---
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y年%m月%d日")
        weekday_map = {0:"周一", 1:"周二", 2:"周三", 3:"周四", 4:"周五", 5:"周六", 6:"周日"}
        weekday_str = weekday_map[yesterday.weekday()]

        # --- 2. 核心定位 ---
        row_10y = find_row_by_keyword(df, "10Y UST")
        row_dxy = find_row_by_keyword(df, "DXY")
        row_cnh = find_row_by_keyword(df, "USD/CNH")
        row_yield_table = find_row_by_keyword(df, "Implied yield table")
        row_repo = find_row_by_keyword(df, "Repo")

        # --- 3. 市场数据分析 ---
        ten_year_yield = float(df.iat[row_10y, 2])
        ten_year_bps = float(df.iat[row_10y, 3])
        ny_usd_close = float(df.iat[row_dxy, 2])
        asia_usd_close = float(df.iat[row_dxy, 3])
        ysd_usd_close = float(df.iat[row_dxy, 4])
        
        # --- 4. 离岸回购与流动性逻辑 ---
        # 获取 Repo 数据 (假设前4行是活跃期限)
        repo_df = df.iloc[row_repo+1 : row_repo+5]
        repo_diffs = repo_df[3].astype(float) # 第4列变动
        repo_trend = "上行" if repo_diffs.mean() > 0 else "下行"
        repo_status = "转松" if float(df.iat[row_repo+1, 2]) > float(df.iat[row_repo+1, 4]) else "收紧"
        
        # 提取 Implied yield table 用于展示
        yield_table_df = df.iloc[row_yield_table:row_yield_table+10, 1:4]
        yield_table_df.columns = ["期限", "利率", "变动"]

        # --- 5. 生成完整报告 ---
        report = f"""
### 离岸央票市场简报 {date_str}

**第一段：市场概览**
{weekday_str}晚间无重要经济数据公布。美债收益率曲线在纽约时段整体{"上行" if ten_year_bps > 0 else "下行"}，10年期美债收益率较上一交易日{"上行" if ten_year_bps > 0 else "下行"}{abs(ten_year_bps)} bps，收于{ten_year_yield}%。

美元指数在纽约时段{"震荡上行" if (ny_usd_close - ysd_usd_close) > 0.05 else "震荡下行"}，最终收于{ny_usd_close}附近。

今日亚洲时间，美元指数{"延续了上行" if (asia_usd_close - ny_usd_close) > 0.02 else "转跌"}，最终收于{asia_usd_close}附近；离岸人民币重回6.80关键位以内，最终收于{float(df.iat[row_cnh, 2])}附近。

**第二段：离岸人民币货币市场与流动性观测**
今日离岸人民币资金利率整体{"收紧" if all(df.iloc[row_yield_table+2:row_yield_table+10, 3].astype(float) > 0) else "变化不大"}。

**第三部分：香港离岸人民币回购市场**
人民币回购市场方面，今日开盘离岸人民币回购利率各期限与上一交易日开盘时相比{repo_trend}于 {abs(round(repo_diffs.mean(), 1))} bps以内。今日日内离岸人民币资金整体小幅{repo_status}，收盘时各期限与开盘水平相比上行 {abs(round(repo_diffs.mean(), 1))} bps以内。今日我行有 [请填入] 亿离岸人民币回购成交。以下是比较活跃期限之我行开价及波幅：

### Implied Yield Table
{yield_table_df.to_markdown(index=False)}
"""
        st.subheader("✅ 生成报告内容：")
        st.markdown(report)
        st.download_button("下载报告", report, file_name=f"央票简报_{yesterday.strftime('%Y%m%d')}.md")

    except Exception as e:
        st.error(f"坐标定位出错，请检查 CSV 内容是否包含必需标签。详细错误: {e}")
        st.write("提示：请确保 CSV 中包含 '10Y UST', 'DXY', 'USD/CNH', 'Implied yield table', 'Repo' 等关键词。")