import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="央票自动化调试工具", layout="wide")
st.title("🏦 央票自动化工具 (调试模式)")

uploaded_file = st.file_uploader("请上传 CSV", type=["csv"])

if uploaded_file:
    # 1. 编码检测与读取
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8-sig', header=None)
    except:
        df = pd.read_csv(uploaded_file, encoding='gbk', header=None)
    
    st.write("--- 调试信息: 文件前 5 行 ---")
    st.write(df.head(5))

    try:
        # 2. 定位 Repo 行 (带哨兵检查)
        repo_mask = df[0].astype(str).str.contains("Repo", na=False)
        if not repo_mask.any():
            st.error("❌ 错误：在第一列中找不到 'Repo' 标签！")
            st.stop()
        
        repo_idx = df.index[repo_mask][0]
        st.write(f"✅ 成功定位 Repo 行: 第 {repo_idx} 行")

        # 3. 读取 Repo 数据区域
        # 根据 snippet，数据从 repo_idx+2 开始
        repo_df = df.iloc[repo_idx+2 : repo_idx+9].copy()
        
        # ⚠️ 关键检查：看看数据是否正确加载
        if repo_df.empty:
            st.error("❌ 错误：Repo 数据区为空，请检查行偏移量是否正确！")
            st.stop()
            
        repo_df.columns = ["期限", "开盘买", "开盘卖", "变动", "收盘买", "收盘卖"]
        st.write("--- 调试信息: 读取到的 Repo 表 ---")
        st.write(repo_df)

        # 4. 逻辑计算
        repo_df["变动"] = pd.to_numeric(repo_df["变动"], errors='coerce').fillna(0)
        avg_change = repo_df["变动"].mean()
        
        # ... (后续生成报告逻辑) ...
        st.success("🎉 数据处理逻辑运行正常！")

    except Exception as e:
        # 打印出完整的报错信息，方便排查
        st.error(f"❌ 程序逻辑崩溃，错误详情如下：")
        st.exception(e)