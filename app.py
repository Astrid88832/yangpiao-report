import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", page_icon="🏦", layout="wide")
st.title("🏦 央票自动化工具")

# 1. 文件上传
uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])

# 2. 经济数据输入框
econ_news = st.text_area("请输入今晚的经济数据简述:", value="周五晚间无重要经济数据公布")

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    try:
        # --- 1. 日期逻辑 ---
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y年%m月%d日")
        weekday_map = {0:"周一", 1:"周二", 2:"周三", 3:"周四", 4:"周五", 5:"周六", 6:"周日"}
        weekday_str = weekday_map[yesterday.weekday()]

        # --- 2. 辅助函数：精准安全定位 ---
        def get_rate_data_safe(term_name, start_from=0):
            # 在指定行之后搜索
            subset = df.iloc[start_from:]
            row_idx = subset[subset[1] == term_name].index[0]
            return float(df.iat[row_idx, 2]), float(df.iat[row_idx, 3])

        # --- 3. 第一段数据 ---
        row_10y = df[df[1] == "10Y UST"].index[0]
        ten_year_yield = float(df.iat[row_10y, 2])
        ten_year_bps = float(df.iat[row_10y, 3])
        
        row_dxy = df[df[1] == "DXY"].index[0]
        ny_usd_close = float(df.iat[row_dxy, 2])
        asia_usd_close = float(df.iat[row_dxy, 3])
        ysd_usd_close = float(df.iat[row_dxy, 4])
        
        row_cnh = df[df[1] == "USD/CNH"].index[0]
        cnh_asia_close = float(df.iat[row_cnh, 2])

        # --- 4. 第二段数据 (安全定位) ---
        start_row = df[df[1] == "Implied yield table"].index[0]
        
        # 获取基础数据
        cnhon_open, cnhon_close = get_rate_data_safe("CNHON")
        tn_open, tn_close = get_rate_data_safe("CNHTN")
        on_rate, on_change = get_rate_data_safe("O/N", start_row)
        tn_rate, tn_change = get_rate_data_safe("T/N", start_row)
        one_year_rate, one_year_change = get_rate_data_safe("1Y", start_row)

        # 整体流动性基调
        changes = [float(df.iat[i, 3]) for i in range(start_row + 2, start_row + 10) if pd.notna(df.iat[i, 3])]
        liquidity_status = "收紧" if all(c > 0 for c in changes) else ("转松" if all(c < 0 for c in changes) else "变化不大")
        
        # 其余期限概括
        other_changes = [float(df.iat[i, 3]) for i in range(start_row + 4, start_row + 10) if pd.notna(df.iat[i, 3])]
        others_trend = "窄幅波动于 5bps 以内" if all(abs(c) <= 5 for c in other_changes) else ("均上行" if all(c > 0 for c in other_changes) else "均下行")

        # --- 5. 逻辑生成报告 ---
        trend_word = "上行" if ten_year_bps > 0 else "下行"
        ny_trend = "震荡上行" if (ny_usd_close - ysd_usd_close) > 0.05 else ("震荡下行" if (ny_usd_close - ysd_usd_close) < -0.05 else "窄幅波动")
        asia_trend = "延续了上行" if (asia_usd_close - ny_usd_close) > 0.02 else ("转跌" if (asia_usd_close - ny_usd_close) < -0.02 else "变化不大")

        report = f"""
### 离岸央票市场简报 {date_str}

**第一段：市场概览**
{weekday_str}晚间{econ_news}。美债收益率曲线在纽约时段整体{trend_word}，10年期美债收益率较上一交易日{trend_word}{abs(ten_year_bps)} bps，收于{ten_year_yield}%。

美元指数在纽约时段{ny_trend}，最终收于{ny_usd_close}附近。

今日亚洲时间，美元指数{asia_trend}，最终收于{asia_usd_close}附近；离岸人民币重回6.80关键位以内，最终收于{cnh_asia_close}附近。

**第二段：离岸人民币货币市场与流动性观测**
今日离岸人民币资金利率整体{liquidity_status}。具体来看，O/N期限早盘于{cnhon_open}%位置开盘，日内走势为{"震荡上行" if cnhon_close > cnhon_open else "震荡下行"}，尾盘收于{cnhon_close}%附近位置，隐含收益率{on_rate}%，较上一交易日{"上行" if on_change > 0 else "下行"}{abs(on_change)} bps。

T/N掉期早盘于{tn_open}附近位置开盘，日内走势为{"震荡上行" if tn_close > tn_open else "震荡下行"}，尾盘收于{tn_close}附近位置，隐含收益率{tn_rate}%，较上一交易日{"上行" if tn_change > 0 else "下行"}{abs(tn_change)} bps。

其余期限均{others_trend}，其中一年期隐含掉期利率收于{one_year_rate}%附近位置，较上一交易日相比{"上行" if one_year_change > 0 else "下行"}{abs(one_year_change)} bps。
"""
        st.subheader("✅ 生成报告内容：")
        st.markdown(report)
        st.download_button("下载报告", report, file_name=f"央票简报_{yesterday.strftime('%Y%m%d')}.md")
        
    except Exception as e:
        st.error(f"坐标定位出错，请确保 CSV 中包含所有必要标签。错误详情: {e}")