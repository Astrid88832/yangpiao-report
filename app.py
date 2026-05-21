import streamlit as st
import pandas as pd

st.set_page_config(page_title="央票自动化工具", page_icon="🏦")
st.title("🏦 央票自动化工具")
st.write("请上传您的数据文件，系统将自动根据表头定位数据并生成报告。")

uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])

if uploaded_file:
    # 使用 header=0 让 pandas 识别表头
    df = pd.read_csv(uploaded_file, encoding='gbk')
    
    # --- 精细数据定位逻辑 ---
    # 我们定位 "10Y UST" 行，并获取对应列的值
    try:
        # 定位包含 "10Y UST" 的那一行
        ten_year_row = df[df.iloc[:, 0] == "10Y UST"].iloc[0]
        
        # 抓取对应表头的值
        ten_year_yield = ten_year_row["Close lvl"]   # 定位 Close lvl
        ten_year_bps = ten_year_row["10Y UST change"] # 定位 10Y UST change
        
        # 定位 DXY (美元指数) 坐标
        dxy_row = df[df.iloc[:, 0] == "DXY"].iloc[0]
        ny_usd_close = dxy_row["Close US"]
        asia_usd_close = dxy_row["Close Asia"]
        
        # 定位 USD/CNH 坐标
        cnh_row = df[df.iloc[:, 0] == "USD/CNH"].iloc[0]
        cnh_asia_close = cnh_row["Close Asia"]

        # --- 报告模板生成 ---
        report = f"""
### 离岸央票市场简报 (自动化生成)

**第一段：市场概览**
周五晚间无重要经济数据公布，中东局势继续紧张引发通胀担忧再起，叠加日债欧债抛售潮带动美债共振走弱，美债收益率曲线迅速上行。

其中10年期美债收益率较上一交易日{ten_year_bps} bps，收于{ten_year_yield}%。

美元指数在纽约时段震荡走高，最终收于{ny_usd_close}附近。

今日亚洲时间，美元指数震荡上行，最终收于{asia_usd_close}附近；离岸人民币重回6.80关键位以内，最终收于{cnh_asia_close}附近。
"""
        st.subheader("✅ 自动生成报告：")
        st.markdown(report)
        st.download_button("下载报告", report, file_name="央票简报.md")
        
    except Exception as e:
        st.error(f"数据读取失败，请检查 CSV 表头是否包含 '10Y UST', 'Close lvl', '10Y UST change' 等关键词。报错信息: {e}")