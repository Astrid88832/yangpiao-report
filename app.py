import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="央票自动化工具", page_icon="🏦")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("上传 CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    try:
        # --- 1. 日期与周几自动换算 ---
        # 获取当前系统时间，或者您可以手动指定日期
        today = datetime.now() 
        date_str = today.strftime("%Y年%m月%d日")
        weekday_map = {0:"周一", 1:"周二", 2:"周三", 3:"周四", 4:"周五", 5:"周六", 6:"周日"}
        weekday_str = weekday_map[today.weekday()]
        
        # 假设前一天是工作日，用于描述“昨晚”
        prev_day_str = "前一交易日" 

        # --- 2. 精准定位数据 (基于您提供的 CSV 结构) ---
        # 定位 10Y UST 行
        ten_year_row = df[df[1] == "10Y UST"].iloc[0]
        ten_year_yield = ten_year_row[2] # Close lvl
        ten_year_bps = ten_year_row[3]   # 10Y UST change
        
        # 定位 DXY 行
        dxy_row = df[df[1] == "DXY"].iloc[0]
        ny_usd_close = dxy_row[2]   # Close US
        asia_usd_close = dxy_row[3] # Close Asia
        
        # 定位 USD/CNH 行
        cnh_row = df[df[1] == "USD/CNH"].iloc[0]
        cnh_asia_close = cnh_row[2] # Close Asia

        # --- 3. 动态生成的报告 ---
        report = f"""
### 离岸央票市场简报 {date_str}

**第一段：市场概览**
{weekday_str}晚间无重要经济数据公布，中东局势继续紧张引发通胀担忧再起，叠加日债欧债抛售潮带动美债共振走弱，美债收益率曲线迅速上行。

其中10年期美债收益率较上一交易日{ten_year_bps} bps，收于{ten_year_yield}%。

美元指数在纽约时段震荡走高，最终收于{ny_usd_close}附近。

今日亚洲时间，美元指数震荡上行，最终收于{asia_usd_close}附近；离岸人民币重回6.80关键位以内，最终收于{cnh_asia_close}附近。
"""
        st.markdown(report)
        st.download_button("下载报告", report, file_name=f"央票简报_{today.strftime('%Y%m%d')}.md")
        
    except Exception as e:
        st.error(f"数据定位失败，请确保 CSV 中包含 '10Y UST', 'DXY', 'USD/CNH' 等关键词。报错: {e}")