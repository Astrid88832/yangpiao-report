import streamlit as st
import pandas as pd

# 页面基础设置
st.set_page_config(page_title="央票简报自动化助手", page_icon="🏦", layout="wide")
st.title("🏦 央票简报数据自动化助手 (最终校准版)")
st.write("已按批注顺序：经济数据因果 → 美债表现 → 纽约汇率 → 亚洲汇率。")

# 文件上传
uploaded_file = st.file_uploader("请上传 CSV 数据文件", type=["csv"])

if uploaded_file is not None:
    try:
        # 指定 GBK 编码读取
        df = pd.read_csv(uploaded_file, encoding='gbk')
        st.success("✅ 数据已加载")

        # --- 坐标精准锁定 (基于您的 Excel 结构) ---
        # 10年期美债数据 (第4行, 索引3)
        ten_year_yield = df.iat[3, 2]  # C4
        ten_year_bps = df.iat[3, 3]    # D4
        
        # 美元指数与汇率数据 (第6行, 索引5; 第8行, 索引7)
        ny_usd_close = df.iat[5, 2]    # C6
        asia_usd_close = df.iat[5, 3]  # D6
        cnh_asia_close = df.iat[7, 2]  # C8

        # --- 生成严格符合批注顺序的 Prompt ---
        final_prompt = f"""
任务：撰写央票简报第一段，请严格遵循四句逻辑：

第一句：美国经济数据与影响分析
请根据前一日数据，描述公布值，并深入分析该数据如何导致了纽约时段美债的震荡走势。

第二句：美债表现
10年期美债收益率较上一交易日{ten_year_bps} bps，收于{ten_year_yield}%。

第三句：纽约时段美元指数
纽约时段美元指数[震荡上行/震荡下行/窄幅波动]，最终收于{ny_usd_close}。

第四句：亚洲时段汇率表现
今日亚洲时间，美元指数[震荡上行/震荡下行/窄幅波动]，最终收于{asia_usd_close}附近；离岸人民币走势[请根据行情描述]，最终收于{cnh_asia_close}附近。

撰写规则：
1. 必须完全按照上述四句顺序撰写。
2. 必须使用规定的趋势词（震荡上行/下行/窄幅波动）。
3. 严禁加入任何宏观背景之外的主观推断。
4. 语言风格：专业金融日报，严谨客观。
"""
        
        # UI展示
        st.subheader("💡 最终投喂指令：")
        st.text_area("请全选以下内容复制并粘贴到 QClaw 中：", value=final_prompt, height=550)
        
        st.warning("⚠️ 操作提示：如果生成的数值与您的预期行/列不符，请告诉我，我可以瞬间微调坐标数字。")

    except Exception as e:
        st.error(f"坐标读取出错: {e}")
        st.info("提示：请确保 Excel 文件的行数和列数与坐标锁定位置一致。")
else:
    st.info("请先上传 CSV 文件。")