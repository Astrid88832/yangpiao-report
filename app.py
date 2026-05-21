import streamlit as st
import pandas as pd

st.title("🏦 央票自动化工具")
uploaded_file = st.file_uploader("上传 CSV", type=["csv"])

if uploaded_file:
    # 不设 header，让代码自己去寻找数据所在的行
    df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    try:
        # --- 核心逻辑：精准定位 ---
        # 1. 查找包含 "10Y UST" 的行
        ten_year_row = df[df[1] == "10Y UST"].iloc[0]
        ten_year_yield = ten_year_row[2]  # 第3列
        ten_year_bps = ten_year_row[3]    # 第4列
        
        # 2. 查找包含 "DXY" 的行
        dxy_row = df[df[1] == "DXY"].iloc[0]
        ny_usd_close = dxy_row[2]   # 第3列 (Close US)
        asia_usd_close = dxy_row[3] # 第4列 (Close Asia)
        
        # 3. 查找包含 "USD/CNH" 的行
        cnh_row = df[df[1] == "USD/CNH"].iloc[0]
        cnh_asia_close = cnh_row[2] # 第3列 (Close Asia)

        # 生成报告
        report = f"""
### 离岸央票市场简报 (自动化生成)

**第一段：市场概览**
周五晚间无重要经济数据公布，中东局势继续紧张引发通胀担忧再起，叠加日债欧债抛售潮带动美债共振走弱，美债收益率曲线迅速上行。

其中10年期美债收益率较上一交易日{ten_year_bps} bps，收于{ten_year_yield}%。

美元指数在纽约时段震荡走高，最终收于{ny_usd_close}附近。

今日亚洲时间，美元指数震荡上行，最终收于{asia_usd_close}附近；离岸人民币重回6.80关键位以内，最终收于{cnh_asia_close}附近。
"""
        st.markdown(report)
        st.download_button("下载报告", report, file_name="央票简报.md")
        
    except Exception as e:
        st.error(f"数据读取失败：系统无法找到对应的关键字行。请检查 CSV 中是否存在 '10Y UST', 'DXY', 'USD/CNH'。详细错误: {e}")