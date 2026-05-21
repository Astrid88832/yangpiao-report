import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦")
st.title("🏦 央票自动化工具")

# 1. 文件上传
uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])

# 2. 经济数据输入框
econ_news = st.text_area("请输入今晚的经济数据简述 (如：周五晚间美国公布了非农就业数据，表现平稳):", 
                         value="周五晚间无重要经济数据公布")

if uploaded_file:
    # 读入 CSV，忽略表头
    df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    try:
        # --- 1. 日期逻辑：自动回溯 1 天 ---
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y年%m月%d日")
        weekday_map = {0:"周一", 1:"周二", 2:"周三", 3:"周四", 4:"周五", 5:"周六", 6:"周日"}
        weekday_str = weekday_map[yesterday.weekday()]

        # --- 2. 精准坐标定位 (基于您的 CSV 物理位置) ---
        # 10Y UST (第3行, 索引2=Close, 索引3=Change, 索引4=Ysd)
        row_10y = df[df[1] == "10Y UST"].index[0]
        ten_year_yield = df.iat[row_10y, 2] 
        ten_year_bps = df.iat[row_10y, 3]   
        
        # DXY (第6行, 索引2=Close US, 索引3=Close Asia)
        row_dxy = df[df[1] == "DXY"].index[0]
        ny_usd_close = df.iat[row_dxy, 2]   
        asia_usd_close = df.iat[row_dxy, 3] 
        # 假设 Ysd lvl 在 DXY 行的第 5 列 (索引 4)
        ysd_usd_close = df.iat[row_dxy, 4] 
        
        # USD/CNH (第9行, 索引2=Close Asia)
        row_cnh = df[df[1] == "USD/CNH"].index[0]
        cnh_asia_close = df.iat[row_cnh, 2] 

        # --- 3. 走势逻辑自动计算 ---
        # 美债走势判断
        trend_word = "上行" if float(ten_year_bps) > 0 else "下行"
        
        # 美元指数纽约时段判断
        ny_diff = ny_usd_close - ysd_usd_close
        if ny_diff > 0.05: ny_trend = "震荡上行"
        elif ny_diff < -0.05: ny_trend = "震荡下行"
        else: ny_trend = "窄幅波动"
        
        # 美元指数亚洲时段判断
        asia_diff = asia_usd_close - ny_usd_close
        if asia_diff > 0.02: asia_trend = "延续了上行"
        elif asia_diff < -0.02: asia_trend = "转跌"
        else: asia_trend = "变化不大"

        # --- 4. 报告生成 ---
        report = f"""
### 离岸央票市场简报 {date_str}

**第一段：市场概览**
{weekday_str}晚间{econ_news}，中东局势继续紧张引发通胀担忧再起，叠加日债欧债抛售潮带动美债共振走弱，美债收益率曲线在纽约时段整体{trend_word}。

其中10年期美债收益率较上一交易日{ten_year_bps} bps，收于{ten_year_yield}%。

美元指数在纽约时段{ny_trend}，最终收于{ny_usd_close}附近。

今日亚洲时间，美元指数{asia_trend}，最终收于{asia_usd_close}附近；离岸人民币重回6.80关键位以内，最终收于{cnh_asia_close}附近。
"""
        st.subheader("✅ 生成报告内容：")
        st.markdown(report)
        st.download_button("下载报告", report, file_name=f"央票简报_{yesterday.strftime('%Y%m%d')}.md")
        
    except Exception as e:
        st.error(f"坐标读取出错，请检查 CSV 格式。错误详情: {e}")