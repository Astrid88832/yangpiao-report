import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="央票自动化工具", page_icon="🏦")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("上传 CSV", type=["csv"])

if uploaded_file:
    # 使用 header=None 读取，避免 pandas 将空行识别为列名
    df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    try:
        # --- 精准坐标定位 (已根据您提供的 CSV 结构调整) ---
        # 索引说明: 行号(0-based), 列号(0-based)
        # 第2行是 "First PARA", 第3行是标题, 第4行是数据
        
        ten_year_yield = df.iat[2, 2] # 10Y UST Close lvl
        ten_year_bps = df.iat[2, 3]   # 10Y UST change
        
        ny_usd_close = df.iat[5, 2]   # DXY Close US
        asia_usd_close = df.iat[5, 3] # DXY Close Asia
        cnh_asia_close = df.iat[8, 2] # USD/CNH Close Asia

        # --- 动态日期逻辑 ---
        today = datetime.now()
        date_str = today.strftime("%Y年%m月%d日")
        weekday_map = {0:"周一", 1:"周二", 2:"周三", 3:"周四", 4:"周五", 5:"周六", 6:"周日"}
        weekday_str = weekday_map[today.weekday()]

        # --- 报告模板生成 ---
        report = f"""
### 离岸央票市场简报 {date_str}

**第一段：市场概览**
{weekday_str}晚间无重要经济数据公布，中东局势继续紧张引发通胀担忧再起，叠加日债欧债抛售潮带动美债共振走弱，美债收益率曲线迅速上行。

其中10年期美债收益率较上一交易日{ten_year_bps} bps，收于{ten_year_yield}%。

美元指数在纽约时段震荡走高，最终收于{ny_usd_close}附近。

今日亚洲时间，美元指数震荡上行，最终收于{asia_usd_close}附近；离岸人民币重回6.80关键位以内，最终收于{cnh_asia_close}附近。
"""
        st.markdown(report)
        st.download_button("下载报告", report, file_name="央票简报.md")
        
    except Exception as e:
        st.error(f"数据读取失败，请确保文件格式与模板一致。错误详情: {e}")