import streamlit as st
import pandas as pd

st.set_page_config(page_title="央票简报自动化产出", page_icon="📝")
st.title("📝 央票简报直接产出引擎")

uploaded_file = st.file_uploader("请上传 CSV 数据文件", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='gbk')
    
    # 1. 抓取您的坐标数据 (使用 iat 定位，确保数据完全符合)
    # 假设 Excel 中 D4, C4, C6, D6, C8 分别对应您想要的数据
    ten_year_bps = df.iat[3, 3]    # D4
    ten_year_yield = df.iat[3, 2]  # C4
    ny_usd_close = df.iat[5, 2]    # C6
    asia_usd_close = df.iat[5, 3]  # D6
    cnh_asia_close = df.iat[7, 2]  # C8

    # 2. 编写“报告生成模板” (这里就是您想要的直接生成的结果)
    # 我们根据 Word 文稿的第一段逻辑，直接用 Python 字符串填入数据
    report = f"""
### 离岸央票市场简报 2026.05.18

周五晚间无重要经济数据公布，中东局势继续紧张引发通胀担忧再起，叠加日债欧债抛售潮带动美债共振走弱，美债收益率曲线迅速上行。

其中10年期美债收益率较上一交易日{ten_year_bps} bps，收于{ten_year_yield}%。

美元指数在纽约时段震荡走高，最终收于{ny_usd_close}附近。

今日亚洲时间，美元指数震荡上行，最终收于{asia_usd_close}附近；离岸人民币重回6.80关键位以内，最终收于{cnh_asia_close}附近。
"""

    # 3. 在页面直接展示报告
    st.subheader("✅ 已自动生成报告内容：")
    st.markdown(report)
    
    # 下载功能
    st.download_button("下载 Markdown 报告", report, file_name="report.md")

else:
    st.info("请上传数据，网页将为您自动产出报告。")