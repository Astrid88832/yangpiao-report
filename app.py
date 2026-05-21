import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦")
st.title("🏦 央票自动化工具")

# 1. 文件上传
uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])

# 2. 经济数据输入框 (手动输入以保证灵活性)
econ_news = st.text_area("请输入今晚的经济数据简述 (如：周五晚间美国公布了非农就业数据，表现平稳):", 
                         value="周五晚间无重要经济数据公布")

if uploaded_file:
    # 使用 header=None 读取，避免 pandas 错误识别表头
    df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    try:
        # --- 1. 日期逻辑：自动回溯 1 天 (模拟昨晚数据) ---
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y年%m月%d日")
        weekday_map = {0:"周一", 1:"周二", 2:"周三", 3:"周四", 4:"周五", 5:"周六", 6:"周日"}
        weekday_str = weekday_map[yesterday.weekday()]

        # --- 2. 精准坐标定位 (基于 Yangpiao data.csv) ---
        # 定位方式：df[1] 是包含关键字 "10Y UST" 等的那一列
        
        # 10Y UST 数据 (第3行, 索引2为 Close lvl, 索引3为 Change)
        row_10y = df[df[1] == "10Y UST"].index[0]
        ten_year_yield = df.iat[row_10y, 2] 
        ten_year_bps = df.iat[row_10y, 3]   
        
        # DXY 数据 (第6行, 索引5)
        row_dxy = df[df[1] == "DXY"].index[0]
        ny_usd_close = df.iat[row_dxy, 2]   
        asia_usd_close = df.iat[row_dxy, 3] 
        
        # USD/CNH 数据 (第9行, 索引8)
        row_cnh = df[df[1] == "USD/CNH"].index[0]
        cnh_asia_close = df.iat[row_cnh, 2] 

        # --- 3. 报告生成 ---
        report = f"""
### 离岸央票市场简报 {date_str}

**第一段：市场概览**
{weekday_str}晚间{econ_news}，中东局势继续紧张引发通胀担忧再起，叠加日债欧债抛售潮带动美债共振走弱，美债收益率曲线迅速上行。

其中10年期美债收益率较上一交易日{ten_year_bps} bps，收于{ten_year_yield}%。

美元指数在纽约时段震荡走高，最终收于{ny_usd_close}附近。

今日亚洲时间，美元指数震荡上行，最终收于{asia_usd_close}附近；离岸人民币重回6.80关键位以内，最终收于{cnh_asia_close}附近。
"""
        st.subheader("✅ 生成报告内容：")
        st.markdown(report)
        st.download_button("下载报告", report, file_name=f"央票简报_{yesterday.strftime('%Y%m%d')}.md")
        
    except Exception as e:
        st.error(f"数据读取出错，请检查 CSV 格式是否包含 '10Y UST', 'DXY', 'USD/CNH' 等行。错误: {e}")