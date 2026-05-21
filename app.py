import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦", layout="wide")
st.title("🏦 央票自动化工具")

# 1. 文件上传
uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])

# 2. 经济数据输入框
econ_news = st.text_area("请输入今晚的经济数据简述 (如：周五晚间无重要经济数据公布):", 
                         value="周五晚间无重要经济数据公布")

if uploaded_file:
    # 读入 CSV，header=None
    df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    try:
        # --- 1. 日期逻辑 ---
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y年%m月%d日")
        weekday_map = {0:"周一", 1:"周二", 2:"周三", 3:"周四", 4:"周五", 5:"周六", 6:"周日"}
        weekday_str = weekday_map[yesterday.weekday()]

        # --- 2. 第一段数据定位 ---
        row_10y = df[df[1] == "10Y UST"].index[0]
        ten_year_yield = float(df.iat[row_10y, 2])
        ten_year_bps = float(df.iat[row_10y, 3])
        
        row_dxy = df[df[1] == "DXY"].index[0]
        ny_usd_close = float(df.iat[row_dxy, 2])
        asia_usd_close = float(df.iat[row_dxy, 3])
        ysd_usd_close = float(df.iat[row_dxy, 4])
        
        row_cnh = df[df[1] == "USD/CNH"].index[0]
        cnh_asia_close = float(df.iat[row_cnh, 2])

        # --- 3. 第二段数据定位 (Implied yield table) ---
        start_row = df[df[1] == "Implied yield table"].index[0]
        # 假设数据从 start_row + 2 开始 (跳过标题和表头)
        # 假设变动值在第 3 列 (索引 2)
        # 获取所有期限的变动值，直到空行或下一段
        changes = []
        i = start_row + 2
        while i < len(df) and pd.notna(df.iat[i, 1]): # 假设第2列(索引1)是期限名
            try:
                val = float(df.iat[i, 2])
                changes.append(val)
                i += 1
            except:
                break
        
        # 资金利率基调逻辑
        if all(c > 0 for c in changes): liquidity_status = "收紧"
        elif all(c < 0 for c in changes): liquidity_status = "转松"
        else: liquidity_status = "变化不大"
        
        # CNHON 数据
        row_cnhon = df[df[1] == "CNHON"].index[0]
        cnhon_open = float(df.iat[row_cnhon, 2])
        cnhon_close = float(df.iat[row_cnhon, 3])
        cnhon_trend = "震荡上行" if cnhon_close > cnhon_open else "震荡下行"
        
        # O/N 利率数据
        row_on = df[df[1] == "O/N"].index[0]
        on_rate = float(df.iat[row_on, 2])
        on_change = float(df.iat[row_on, 3])
        on_trend_desc = "上行" if on_change > 0 else "下行"

        # --- 4. 计算走势 ---
        trend_word = "上行" if ten_year_bps > 0 else "下行"
        
        ny_diff = ny_usd_close - ysd_usd_close
        if ny_diff > 0.05: ny_trend = "震荡上行"
        elif ny_diff < -0.05: ny_trend = "震荡下行"
        else: ny_trend = "窄幅波动"
        
        asia_diff = asia_usd_close - ny_usd_close
        if asia_diff > 0.02: asia_trend = "延续了上行"
        elif asia_diff < -0.02: asia_trend = "转跌"
        else: asia_trend = "变化不大"

        # --- 5. 报告生成 ---
        report = f"""
### 离岸央票市场简报 {date_str}

**第一段：市场概览**
{weekday_str}晚间{econ_news}。美债收益率曲线在纽约时段整体{trend_word}，10年期美债收益率较上一交易日{trend_word}{abs(ten_year_bps)} bps，收于{ten_year_yield}%。

美元指数在纽约时段{ny_trend}，最终收于{ny_usd_close}附近。

今日亚洲时间，美元指数{asia_trend}，最终收于{asia_usd_close}附近；离岸人民币重回6.80关键位以内，最终收于{cnh_asia_close}附近。

**第二段：离岸人民币货币市场与流动性观测**
今日离岸人民币资金利率整体{liquidity_status}。具体来看，O/N期限早盘于{cnhon_open}%位置开盘，日内走势为{cnhon_trend}，尾盘收于{cnhon_close}%附近位置，隐含收益率{on_rate}%，较上一交易日{on_trend_desc}{abs(on_change)} bps。
"""
        st.subheader("✅ 生成报告内容：")
        st.markdown(report)
        st.download_button("下载报告", report, file_name=f"央票简报_{yesterday.strftime('%Y%m%d')}.md")
        
    except Exception as e:
        st.error(f"数据读取出错，请检查 CSV 格式。错误详情: {e}")