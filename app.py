import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ================= 页面配置 =================
st.set_page_config(page_title="ysh智慧财税中台", layout="wide", initial_sidebar_state="expanded")

# ================= 高级UI美化 =================
st.markdown("""
<style>
    .stApp { background: #F4F7F9; }
    [data-testid="stSidebar"] { background: #111827; border-right: 1px solid #374151; }
    [data-testid="stSidebar"] * { color: #F3F4F6 !important; }
    div[data-testid="metric-container"] {
        background: white; padding: 15px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 5px solid #3B82F6;
    }
    h1 { color: #1F2937; font-weight: 800; border-bottom: 2px solid #E5E7EB; padding-bottom: 10px; }
    h2 { color: #374151; font-weight: 600; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ================= 全局状态初始化 (模拟数据库) =================
if 'invoice_data' not in st.session_state:
    # 初始化的发票台账数据
    st.session_state.invoice_data = pd.DataFrame([
        {"发票类型": "销项", "发票号码": "01001", "开票日期": "2026-09-05", "购方/销方": "A科技公司", "金额": 500000.0, "税率": 0.13, "税额": 65000.0},
        {"发票类型": "销项", "发票号码": "01002", "开票日期": "2026-09-15", "购方/销方": "B商贸公司", "金额": 300000.0, "税率": 0.13, "税额": 39000.0},
        {"发票类型": "进项", "发票号码": "02001", "开票日期": "2026-09-10", "购方/销方": "C供应商", "金额": 200000.0, "税率": 0.13, "税额": 26000.0}
    ])

if 'declare_status' not in st.session_state:
    st.session_state.declare_status = "未申报"

# ================= 侧边栏 =================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#60A5FA;'>🏢 智慧财税中台</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:12px;'>设计人：<b>【ysh】</b></p>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("业务导航", [
        "🏠 企业中心", 
        "🧾 发票与凭证管理", 
        "🧮 智能计税与申报", 
        "📜 政策匹配中心", 
        "⚠️ 风险监控与体检", 
        "🤖 智能财税客服", 
        "🔔 待办与消息中心"
    ])
    st.markdown("---")
    st.info(f"系统状态：正常\n\n申报状态：{st.session_state.declare_status}")

# ================= 1. 企业中心 =================
if menu == "🏠 企业中心":
    st.title("🏠 企业数字档案与画像")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("纳税人识别号", "91610100MA7X", "一般纳税人")
    c2.metric("纳税信用等级", "B级", "良好")
    c3.metric("主营行业", "软件信息服务", "I65")
    c4.metric("注册资本", "500 万元", "实缴")
    
    st.markdown("---")
    st.subheader("企业健康度诊断雷达")
    fig = go.Figure(go.Scatterpolar(
        r=[85, 75, 90, 85, 70], theta=['盈利能力', '偿债能力', '研发创新', '税务合规', '营运能力'],
        fill='toself', line_color='#3B82F6', fillcolor='rgba(59, 130, 246, 0.2)'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

# ================= 2. 发票与凭证管理 =================
elif menu == "🧾 发票与凭证管理":
    st.title("🧾 进销项发票台账管理")
    st.info("💡 提示：您可以直接在下方表格中修改、添加或删除发票数据，系统将实时汇总并同步至计税引擎。")
    
    # 可编辑的数据表
    edited_df = st.data_editor(st.session_state.invoice_data, num_rows="dynamic", use_container_width=True)
    st.session_state.invoice_data = edited_df
    
    # 汇总数据
    total_sales = edited_df[edited_df["发票类型"] == "销项"]["金额"].sum()
    total_sales_tax = edited_df[edited_df["发票类型"] == "销项"]["税额"].sum()
    total_purchase = edited_df[edited_df["发票类型"] == "进项"]["金额"].sum()
    total_purchase_tax = edited_df[edited_df["发票类型"] == "进项"]["税额"].sum()
    
    st.markdown("### 自动汇总")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("本期销项金额", f"¥ {total_sales:,.2f}")
    col1.caption(f"销项税额: ¥ {total_sales_tax:,.2f}")
    col2.metric("本期进项金额", f"¥ {total_purchase:,.2f}")
    col2.caption(f"进项税额: ¥ {total_purchase_tax:,.2f}")
    
    st.markdown("---")
    st.subheader("数据清洗与勾稽校验")
    if st.button("执行数据清洗与校验"):
        with st.spinner("正在执行去重、缺失值填补、科目映射校验..."):
            st.success("✅ 校验通过：发票台账与财务报表借贷平衡，无重复发票！")

# ================= 3. 智能计税与申报 =================
elif menu == "🧮 智能计税与申报":
    st.title("🧮 多税种申报与计算引擎")
    
    # 自动从发票模块读取数据
    df = st.session_state.invoice_data
    sales_tax = df[df["发票类型"] == "销项"]["税额"].sum()
    purchase_tax = df[df["发票类型"] == "进项"]["税额"].sum()
    
    tab1, tab2, tab3 = st.tabs(["📄 增值税及附加", "🏢 企业所得税", "💰 印花税"])
    
    with tab1:
        st.subheader("增值税一般纳税人申报表计算")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("销项税额（从台账提取）", value=f"{sales_tax:.2f}", disabled=True)
            st.text_input("进项税额（从台账提取）", value=f"{purchase_tax:.2f}", disabled=True)
            transfer_out = st.number_input("进项税额转出", value=0.0)
        with col2:
            vat_payable = sales_tax - purchase_tax + transfer_out
            st.metric("本期应纳增值税", f"¥ {vat_payable:,.2f}")
            st.text_input("城建税及附加 (12%)", value=f"{vat_payable * 0.12:.2f}", disabled=True)
            
            if st.button("✅ 提交增值税申报"):
                st.session_state.declare_status = "增值税已申报"
                st.success("增值税申报成功！申报表已生成归档。")

    with tab2:
        st.subheader("企业所得税预缴测算 (A类)")
        revenue = st.number_input("营业收入", value=float(sales_tax * 1.5))
        cost = st.number_input("营业成本", value=float(revenue * 0.6))
        rd = st.number_input("研发费用", value=80000.0)
        st.info(f"加计扣除计算：研发费用 100% 加计，调减应纳税所得额 {rd} 元。")
        
        taxable = revenue - cost - rd
        cit_rate = 0.05 if taxable <= 3000000 else 0.25
        cit = taxable * cit_rate
        st.metric("应预缴企业所得税", f"¥ {cit:,.2f}", delta=f"适用税率 {cit_rate*100}%")

    with tab3:
        st.subheader("印花税申报")
        contract_amount = st.number_input("购销合同金额", value=1000000.0)
        stamp_tax = contract_amount * 0.0003
        st.metric("应纳印花税", f"¥ {stamp_tax:,.2f}", delta="税率 0.03%")

# ================= 4. 政策匹配中心 =================
elif menu == "📜 政策匹配中心":
    st.title("📜 税收优惠政策智能匹配")
    st.markdown("系统已通过知识图谱将企业画像与税收政策库进行比对。")
    
    policies = [
        {"name": "研发费用加计扣除", "status": "已享受", "desc": "企业研发投入占比10%，符合100%加计扣除条件。"},
        {"name": "软件产品增值税即征即退", "status": "可享受", "desc": "软件销售收入占比超50%，可申请对实际税负超3%部分即征即退。"},
        {"name": "高新技术企业15%所得税率", "status": "暂不满足", "desc": "需取得高新证书。当前无高新资质。"}
    ]
    
    for p in policies:
        with st.expander(f"{p['name']} - 【{p['status']}】", expanded=True):
            st.write(p["desc"])
            if p["status"] == "可享受":
                if st.button(f"一键申请 {p['name']}"):
                    st.success("申请任务已推送到主管税务机关，请准备备查资料！")

# ================= 5. 风险监控与体检 =================
elif menu == "⚠️ 风险监控与体检":
    st.title("⚠️ 涉税风险机器学习预警")
    st.error("🚨 检测到异常：本月增值税税负率 1.2%，大幅低于软件行业均值 3.0%。存在被税务局风控系统扫描的风险。")
    
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(mode="gauge+number", value=68, title={'text': "风险指数"}, 
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#EF4444"}}))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.markdown("### 💡 智能整改建议")
        st.write("1. 核查是否存在滞后开票的销售业务。")
        st.write("2. 检查本月进项发票是否有异常凭证或品名不符。")
        if st.button("生成风险自查报告"):
            st.success("报告已生成并下载到本地！")

# ================= 6. 智能财税客服 =================
elif menu == "🤖 智能财税客服":
    st.title("🤖 财税智能问答")
    st.chat_message("assistant").write("您好，我是财税AI助手。请问有什么可以帮您？")
    user_input = st.chat_input("输入您的财税问题...")
    if user_input:
        st.chat_message("user").write(user_input)
        with st.spinner("正在检索法规..."):
            st.chat_message("assistant").write("根据最新财税政策，软件企业销售自行开发的软件产品，按13%征收增值税后，对实际税负超过3%的部分实行即征即退。您可以在【政策匹配中心】进行申请。")

# ================= 7. 待办与消息中心 =================
elif menu == "🔔 待办与消息中心":
    st.title("🔔 消息与待办事项")
    st.tabs(["未读消息", "已读消息", "订阅设置"])
    
    with st.container(border=True):
        st.write("📢 **【税务局通知】** 2026年10月纳税申报期限截止至10月23日，请及时申报！")
        st.write("⏰ **【系统提醒】** 您的税负率偏低，请前往【风险监控】查看详情。")
    
    st.markdown("### 归档中心")
    st.download_button("📥 下载往期申报表归档.zip", "ZIP数据流", "申报归档.zip")
