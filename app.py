import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化工具", layout="wide")
st.title("🏦 央票自动化工具")

uploaded_file = st.file_uploader("请上传 Yangpiao data.csv 文件", type=["csv"])
econ_news = st.text_area("请输入今晚的经济数据简述:", value="周五晚间无重要经济数据公布")

if uploaded_file:
    # 编码自适应读取
    df = None
    for enc in ['utf-8-sig', 'gbk', 'gb18030']:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc, header=None)
            break
        except: continue
    
    if df is not None:
        try:
            # --- 1. 日期逻辑 ---
            yesterday = datetime.now() - timedelta(days=1)
            date_str = yesterday.strftime("%Y年%m月%d日")
            weekday_map = {0:"周一", 1:"周二", 2:"周三", 3:"周四", 4:"周五", 5:"周六", 6:"周日"}
            weekday_str = weekday_map[yesterday.weekday()]

            # --- 2. 带有定位功能的查找函数 ---
            def get_idx_with_check(keyword, section_name):
                mask = df[0].astype(str).str.contains(keyword, case=False, na=False)
                if not mask.any():
                    raise ValueError(f"【{section_name}】未找到关键词 '{keyword}'，请检查 CSV 对应行！")
                return df.index[mask][0]

            # --- 第一部分：市场概览 (定位检查) ---
            row_10y = get_idx_with_check("10Y UST", "市场概览-10Y")
            ten_year_yield = float(df.iat[row_10y, 2])
            ten_year_bps = float(df.iat[row_10y, 3])
            
            # --- 第二部分：货币市场 (定位检查) ---
            row_yield = get_idx_with_check("Implied yield table", "货币市场-Implied Yield")
            yield_changes = pd.to_numeric(df.iloc[row_yield+2:row_yield+10, 3], errors='coerce')
            liquidity_status = "收紧" if yield_changes.mean() > 0 else "变化不大"

            # --- 3. 报告拼接 ---
            trend_word = "上行" if ten_year_bps > 0 else "下行"
            
            report = f"""
### 离岸央票市场简报 {date_str}

**第一段：市场概览**
{weekday_str}晚间{econ_news}。美债收益率曲线在纽约时段整体{trend_word}，10年期美债收益率较上一交易日{trend_word}{abs(ten_year_bps)} bps，收于{ten_year_yield}%。

**第二段：离岸人民币货币市场与流动性观测**
今日离岸人民币资金利率整体{liquidity_status}。
"""
            st.markdown(report)
            st.success("✅ 第一、二部分定位正常，逻辑运行良好。")
            
        except Exception as e:
            st.error(f"❌ 运行报错: {e}")
            st.write("提示：如果报错，请检查 CSV 文件中是否确实包含了上述关键字。")
    else:
        st.error("无法识别文件编码。")