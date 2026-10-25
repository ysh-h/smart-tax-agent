import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# ================= 页面配置 & 高级CSS =================
st.set_page_config(page_title="智慧财税管理智能体 - 企业版", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background: #F4F7F9; font-family: 'PingFang SC', sans-serif; }
    [data-testid="stSidebar"] { background: #0F172A; box-shadow: 2px 0 10px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] * { color: #94A3B8 !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 15px; padding: 12px; border-radius: 8px; }
    [data-testid="stSidebar"] .stRadio label:hover { background-color: #1E293B; color: #38BDF8 !important; }
    div[data-testid="metric-container"] { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #3B82F6; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1E293B; font-weight: 800; font-size: 28px; }
    h1 { color: #0F172A; font-weight: 800; font-size: 32px; }
    h3 { color: #1E293B; font-weight: 600; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= 全局状态 =================
if 'd' not in st.session_state:
    st.session_state.d = {
        "name": "星耀科技（中国）有限公司", "industry": "软件与信息技术服务业",
        "revenue": 2400000.0, "cost": 1000000.0, "expense": 400000.0, "input_vat": 30000.0,
        "employees": 85, "assets": 4000000.0, "is_high_tech": True, "rd_ratio": 0.06
    }
if 'status' not in st.session_state: st.session_state.status = "未申报"
if 'adj_vat' not in st.session_state: st.session_state.adj_vat = 0.0

d = st.session_state.d

# 核心测算逻辑
vat_out = d["revenue"] * 0.06
vat_payable = max(vat_out - d["input_vat"] + st.session_state.adj_vat, 0)
surcharge = vat_payable * 0.12
profit = d["revenue"] - d["cost"] - d["expense"]
taxable_income = max(0, profit)
is_micro = taxable_income <= 3000000 and d["employees"] <= 300 and d["assets"] <= 50000000
cit_rate = 0.05 if is_micro else (0.15 if d["is_high_tech"] else 0.25)
cit_payable = taxable_income * cit_rate
total_tax = vat_payable + surcharge + cit_payable

# ================= 侧边栏 =================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#38BDF8;'>⚡ 智慧财税中台</h2>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("业务导航", [
        "🏢 企业画像中心", 
        "📁 多源数据采集与清洗", 
        "🧮 自动计税与申报复核", 
        "🎯 政策图谱与适配计算", 
        "🛡️ 涉税风险机器学习看板", 
        "🕸️ 税收知识图谱拓扑", 
        "💬 NLP智能问答与合规提醒"
    ])
    st.markdown("---")
    st.info(f"申报期状态：**{st.session_state.status}**")

# ================= 1. 企业画像中心 =================
if menu == "🏢 企业画像中心":
    st.title("🏢 企业多维数字画像")
    st.markdown("结合企业工商信息、财税指标与研发投入，构建用于政策匹配的底层特征库。")
    
    with st.container(border=True):
        st.subheader("基础画像特征录入")
        c1, c2, c3 = st.columns(3)
        d["name"] = c1.text_input("企业名称", d["name"])
        d["industry"] = c2.selectbox("行业属性", ["软件与信息技术服务业", "先进制造业", "批发零售"])
        d["is_high_tech"] = c3.checkbox("高新技术企业资质", d["is_high_tech"])
        
        c4, c5, c6 = st.columns(3)
        d["revenue"] = c4.number_input("年营业收入(元)", value=d["revenue"], step=10000.0)
        d["employees"] = c5.number_input("从业人数(人)", value=d["employees"])
        d["assets"] = c6.number_input("资产总额(元)", value=d["assets"], step=100000.0)

    st.markdown("### 画像健康度与合规性雷达")
    fig = go.Figure(go.Scatterpolar(
        r=[90, 80, 85, 95, 70], theta=['盈利水平', '资产规模', '研发实力', '税务合规', '现金流'],
        fill='toself', line_color='#3B82F6'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

# ================= 2. 多源数据采集与清洗 =================
elif menu == "📁 多源数据采集与清洗":
    st.title("📁 业财数据采集与智能清洗")
    st.markdown("支持结构化财务数据与非结构化发票/合同数据接入，自动执行勾稽校验与去重。")
    
    tab1, tab2, tab3 = st.tabs(["📊 财务报表接入", "🧾 发票池与进项认证", "📄 OCR合同抽取"])
    
    with tab1:
        st.subheader("财务利润表指标接入")
        c1, c2, c3 = st.columns(3)
        d["cost"] = c1.number_input("本期营业成本(元)", value=d["cost"], step=10000.0)
        d["expense"] = c2.number_input("本期期间费用(元)", value=d["expense"], step=10000.0)
        d["rd_ratio"] = c3.slider("研发费用占营收比", 0.0, 0.2, d["rd_ratio"], 0.01)
        
    with tab2:
        st.subheader("增值税进销项发票台账")
        st.dataframe(pd.DataFrame({
            "发票类型": ["销项专票", "进项专票", "进项普票(不可抵)"],
            "金额(元)": [d["revenue"]*0.8, d["input_vat"]/0.06, 50000.0],
            "税额(元)": [d["revenue"]*0.8*0.06, d["input_vat"], 0.0],
            "勾稽状态": ["✅ 已比对一致", "✅ 已认证抵扣", "⚠️ 进项转出"]
        }), hide_index=True, use_container_width=True)
        d["input_vat"] = st.number_input("确认本期可抵扣进项税额(元)", value=d["input_vat"], step=1000.0)

    with tab3:
        st.subheader("NLP 非结构化合同抽取")
        st.info("上传采购合同扫描件，大模型自动抽取关键要素：")
        st.code('{\n  "合同类别": "技术开发合同",\n  "合同金额": 500000,\n  "适用印花税税目": "技术合同 (0.03%)",\n  "印花税测算": 150.00\n}', language="json")

# ================= 3. 自动计税与申报复核 =================
elif menu == "🧮 自动计税与申报复核":
    st.title("🧮 自动计税与人工复核")
    st.markdown("依据税法自动生成多税种申报底稿，支持进项税额转出等人工干预调整。")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("增值税", f"¥ {vat_payable:,.2f}", "6%现代服务")
    c2.metric("附加税费", f"¥ {surcharge:,.2f}", "增值税*12%")
    c3.metric("企业所得税", f"¥ {cit_payable:,.2f}", f"{'小微5%' if is_micro else '高新15%' if d['is_high_tech'] else '法定25%'}")
    c4.metric("综合税负", f"¥ {total_tax:,.2f}", "本期应缴总计")

    with st.container(border=True):
        st.subheader("1. 人工复核与税会差异调整")
        st.session_state.adj_vat = st.number_input("进项税额转出调增额 (元)", value=st.session_state.adj_vat, help="如发生非正常损失，需转出进项")
        
        st.subheader("2. 标准申报表底稿 (以增值税为例)")
        st.dataframe(pd.DataFrame({
            "行次": [1, 11, 12, 14, 20],
            "申报项目": ["按适用税率计税销售额", "销项税额", "进项税额", "进项税额转出", "应纳税额合计"],
            "金额(元)": [f"{d['revenue']:,.2f}", f"{vat_out:,.2f}", f"{d['input_vat']:,.2f}", f"{st.session_state.adj_vat:,.2f}", f"{vat_payable:,.2f}"]
        }), hide_index=True, use_container_width=True)
        
        if st.button("🚀 批量提交申报", type="primary"):
            st.session_state.status = "已申报"
            st.success("增值税、所得税申报表已成功推送至电子税务局！")

# ================= 4. 政策图谱与适配计算 =================
elif menu == "🎯 政策图谱与适配计算":
    st.title("🎯 政策匹配判定与减免测算")
    st.markdown("自动比对政策适用条件，输出已享受、可享受、暂不满足的详细判定报告。")
    
    with st.container(border=True):
        st.subheader("条件判定明细表 (核心业务逻辑)")
        cond_df = pd.DataFrame([
            {"政策名称": "小型微利企业所得税优惠", "判断条件": "应纳税所得额 ≤ 300万元", "企业当前值": f"{taxable_income:,.2f}", "规则结果": "✅ 满足" if taxable_income <= 3000000 else "❌ 不满足"},
            {"政策名称": "小型微利企业所得税优惠", "判断条件": "从业人数 ≤ 300人", "企业当前值": f"{d['employees']}人", "规则结果": "✅ 满足" if d['employees'] <= 300 else "❌ 不满足"},
            {"政策名称": "高新技术企业15%税率", "判断条件": "具备高新证书", "企业当前值": "具备" if d['is_high_tech'] else "无", "规则结果": "✅ 满足" if d['is_high_tech'] else "❌ 不满足"},
            {"政策名称": "研发费用100%加计扣除", "判断条件": "研发费占营收比 ≥ 3%", "企业当前值": f"{d['rd_ratio']*100:.1f}%", "规则结果": "✅ 满足" if d['rd_ratio'] >= 0.03 else "❌ 不满足"}
        ])
        st.dataframe(cond_df, hide_index=True, use_container_width=True)

    st.markdown("### 优惠金额测算与留存备查")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("✅ **已享受政策**")
        if is_micro: st.info(f"**小微企业优惠**\n减免税额约：{taxable_income*0.20:,.2f}元")
    with c2:
        st.info("💡 **可享受政策测算**")
        st.write(f"**研发费加计扣除**\n可调减应纳税所得额：{d['revenue'] * d['rd_ratio']:,.2f}元")
        st.caption("留存备查：立项决议、研发辅助账、工时分配表。")
    with c3:
        st.warning("⚠️ **暂不满足政策**")
        st.write("**软件即征即退**\n原因：未单独核算软件收入。")

# ================= 5. 涉税风险机器学习看板 =================
elif menu == "🛡️ 涉税风险机器学习看板":
    st.title("🛡️ 机器学习涉税风险预警")
    st.markdown("基于孤立森林（Isolation Forest）等异常检测算法，扫描财务指标偏离度。")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### 风险综合指数")
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = 78, title = {'text': "风险偏离度"},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#EF4444"}}
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.markdown("### 风险扫描明细与整改")
        st.error("🚨 **高风险：增值税税负率异常**\n**指标**：本期税负率 1.2%，行业均值 3.2%。\n**建议**：核查是否存在未开票收入隐匿，或进项发票不合规抵扣。")
        st.warning("⚠️ **中风险：研发费用归集不规范**\n**指标**：未建立辅助账。\n**建议**：规范研发工时与领料记录，防止加计扣除被稽查否定。")

# ================= 6. 税收知识图谱拓扑 =================
elif menu == "🕸️ 税收知识图谱拓扑":
    st.title("🕸️ 税收知识图谱底座")
    st.markdown("基于图数据库构建的实体-关系网络，支撑政策溯源与推理。")
    
    st.graphviz_chart('''
    digraph G {
        rankdir=LR;
        node [shape=box, style=filled, color=lightblue];
        
        "星耀科技" -> "软件与信息服务" [label="属于"];
        "星耀科技" -> "高新技术企业" [label="资质"];
        "高新技术企业" -> "15%所得税率" [label="适用"];
        "软件与信息服务" -> "研发费加计扣除" [label="适用"];
        "研发费加计扣除" -> "企业所得税" [label="影响"];
        
        "星耀科技" -> "税负率偏低" [label="触发", color=red];
        "税负率偏低" -> "税务稽查预警" [label="导致", color=red];
    }
    ''')
    st.info("💡 知识图谱支撑逻辑：系统通过图谱遍历企业实体节点，自动发现其关联的适用政策（如高新资质关联15%税率），同时通过异常指标触发风险节点。")

# ================= 7. NLP智能问答与合规提醒 =================
elif menu == "💬 NLP智能问答与合规提醒":
    st.title("💬 财税智能问答与站内提醒")
    
    tab1, tab2 = st.tabs(["NLP 财税智能问答", "政策变动与期限提醒"])
    with tab1:
        if "msgs" not in st.session_state: st.session_state.msgs = [{"role": "assistant", "content": "您好！基于政策知识图谱，我可以为您解答最新税收优惠与合规要求。"}]
        for m in st.session_state.msgs: st.chat_message(m["role"]).write(m["content"])
        if p := st.chat_input("提问..."):
            st.session_state.msgs.append({"role": "user", "content": p})
            st.chat_message("user").write(p)
            st.chat_message("assistant").write("根据财税[2023]7号文，贵公司研发费用可享受100%加计扣除，请确保辅助账完整。")
            
    with tab2:
        st.info("📢 **政策更新提醒**：2026年10月起，研发费用加计扣除预缴申报可享受。")
        st.warning("⏰ **申报期限提醒**：10月增值税及所得税申报截止日为10月23日。")
        st.error("🚨 **风险整改提醒**：税负率偏低风险已生成，请于本周内提交说明材料。")
