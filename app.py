import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import graphviz
from datetime import date
import io

# ================= 页面配置 & 高级UI =================
st.set_page_config(page_title="智慧财税管理智能体 - 企业级", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background: #F8FAFC; font-family: 'PingFang SC', sans-serif; }
    [data-testid="stSidebar"] { background: #0F172A; box-shadow: 4px 0 15px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] * { color: #94A3B8 !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 15px; padding: 12px; border-radius: 8px; transition: all 0.2s;}
    [data-testid="stSidebar"] .stRadio label:hover { background: #1E293B; color: #38BDF8 !important; }
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
if 'filings' not in st.session_state:
    st.session_state.filings = [] # 记录申报状态: {id, tax, period, amount, status}
if 'adj_vat' not in st.session_state: st.session_state.adj_vat = 0.0

d = st.session_state.d

# 核心测算
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
    st.markdown("<h2 style='text-align:center; color:#38BDF8;'>⚡ 智慧财税平台</h2>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("核心功能模块", [
        "1. 🏢 企业中心 (画像)",
        "2. 📁 多源数据采集与清洗",
        "3. 🧮 自动计税与税会差异",
        "4. 🚀 多税种一键申报",
        "5. 🎯 政策适配与优惠测算",
        "6. ⚠️ 机器学习风险看板",
        "7. 🕸️ 税收知识图谱与NLP",
        "8. 🔔 消息提醒与归档"
    ])
    st.markdown("---")
    st.caption("系统状态：在线 | 数据已加密")

# ================= 1. 企业中心 =================
if menu == "1. 🏢 企业中心 (画像)":
    st.title("🏢 企业多维画像中心")
    st.markdown("读取企业经营指标（行业、纳税身份、规模、注册地等），为政策匹配和风险分析提供底层支撑。")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        d["name"] = c1.text_input("企业名称", d["name"])
        d["industry"] = c2.selectbox("所属行业", ["软件与信息技术服务业", "制造业", "批发零售业"])
        d["is_high_tech"] = c3.checkbox("是否高新技术企业", value=d["is_high_tech"])
        
        c4, c5, c6 = st.columns(3)
        d["revenue"] = c4.number_input("年营业收入(元)", value=d["revenue"], step=10000.0)
        d["employees"] = c5.number_input("从业人数(人)", value=d["employees"])
        d["assets"] = c6.number_input("资产总额(元)", value=d["assets"], step=100000.0)
        st.session_state.d = d

    st.markdown("### 企业画像雷达图")
    fig = go.Figure(go.Scatterpolar(
        r=[90, 80, 85, 95, 70], theta=['盈利水平', '资产规模', '研发实力', '税务合规', '现金流'],
        fill='toself', line_color='#3B82F6'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

# ================= 2. 数据采集与清洗 =================
elif menu == "2. 📁 多源数据采集与清洗":
    st.title("📁 多源数据接入与智能清洗")
    st.markdown("支持对接财务系统、发票系统、银行流水；支持PDF/图片合同采集；完成勾稽关联校验。")
    
    tab1, tab2, tab3 = st.tabs(["📊 财务与银行流水", "🧾 发票池勾稽", "📄 NLP合同抽取"])
    
    with tab1:
        c1, c2 = st.columns(2)
        d["cost"] = c1.number_input("本期营业成本(元)", value=d["cost"], step=10000.0)
        d["expense"] = c2.number_input("本期期间费用(元)", value=d["expense"], step=10000.0)
        st.info("✅ 数据清洗：已过滤异常值 0 条，金额口径统一转换为【元】。")
        
    with tab2:
        st.dataframe(pd.DataFrame({
            "来源": ["发票系统", "银行流水"],
            "业务摘要": ["销售软件产品", "收到客户A货款"],
            "金额(元)": [d["revenue"]*0.8, d["revenue"]*0.8],
            "勾稽校验结果": ["✅ 业务-发票-流水三流一致", "✅ 业务-发票-流水三流一致"]
        }), hide_index=True, use_container_width=True)
        d["input_vat"] = st.number_input("确认本期认证抵扣进项税额(元)", value=d["input_vat"])
        st.session_state.d = d
        
    with tab3:
        st.markdown("#### 非结构化文档智能识别")
        st.file_uploader("上传PDF或图片采购合同", type=["pdf", "png", "jpg"])
        st.success("NLP抽取完成！")
        st.code('{\n  "合同类型": "软件采购合同",\n  "合同金额": 500000,\n  "适用印花税": "技术合同 0.03%",\n  "自动归类凭证": "管理费用-软件服务费"\n}', language="json")

# ================= 3. 自动计税与税会差异 =================
elif menu == "3. 🧮 自动计税与税会差异":
    st.title("🧮 自动计税与税会差异调整")
    st.markdown("依据税法规则自动计算，展示勾稽关系，支持人工复核干预。")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("增值税", f"¥ {vat_payable:,.2f}", "6%一般计税")
    c2.metric("企业所得税", f"¥ {cit_payable:,.2f}", "小微5%" if is_micro else "高新15%")
    c3.metric("综合总税负", f"¥ {total_tax:,.2f}")

    with st.container(border=True):
        st.subheader("人工复核调整")
        st.session_state.adj_vat = st.number_input("进项税额转出调整(元)", value=st.session_state.adj_vat, help="如存货非正常损失需转出")
        st.button("重新测算")

    st.markdown("### 申报表底稿预览")
    st.dataframe(pd.DataFrame({
        "行次": [1, 11, 12, 14, 20],
        "项目": ["按适用税率计税销售额", "销项税额", "进项税额", "进项税额转出", "应纳税额合计"],
        "金额(元)": [f"{d['revenue']:,.2f}", f"{vat_out:,.2f}", f"{d['input_vat']:,.2f}", f"{st.session_state.adj_vat:,.2f}", f"{vat_payable:,.2f}"]
    }), hide_index=True, use_container_width=True)

# ================= 4. 多税种一键申报 =================
elif menu == "4. 🚀 多税种一键申报":
    st.title("🚀 多税种一键申报与归档")
    st.markdown("支持批量提交、查询申报状态，申报表支持下载归档。")
    
    with st.container(border=True):
        st.write("系统检测到本期需申报以下税种：")
        st.markdown(f"- 增值税及附加：¥ {vat_payable + surcharge:,.2f}")
        st.markdown(f"- 企业所得税：¥ {cit_payable:,.2f}")
        
        if st.button("📦 批量提交申报", type="primary"):
            st.session_state.filings.append({"id": f"SB-{len(st.session_state.filings)+1:03d}", "税种": "增值税及附加", "所属期": "2026-10", "金额": f"¥ {vat_payable + surcharge:,.2f}", "状态": "已申报"})
            st.session_state.filings.append({"id": f"SB-{len(st.session_state.filings)+1:03d}", "税种": "企业所得税", "所属期": "2026-10", "金额": f"¥ {cit_payable:,.2f}", "状态": "已申报"})
            st.success("批量申报成功！")

    st.markdown("### 申报状态查询与归档下载")
    if st.session_state.filings:
        st.dataframe(pd.DataFrame(st.session_state.filings), hide_index=True, use_container_width=True)
        # 模拟下载
        csv = pd.DataFrame(st.session_state.filings).to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 打包下载全套申报表 (ZIP)", data=csv, file_name="申报表归档_202610.zip", mime="application/zip")
    else:
        st.info("暂无申报记录。")

# ================= 5. 政策适配与优惠测算 =================
elif menu == "5. 🎯 政策适配与优惠测算":
    st.title("🎯 政策适配与优惠智能测算")
    st.markdown("自动识别企业可享受优惠，区分已享受、可享受、暂不满足，提示留存备查资料。")
    
    with st.container(border=True):
        st.subheader("条件判定明细表")
        st.dataframe(pd.DataFrame([
            {"政策": "小型微利优惠", "判断条件": "利润 ≤ 300万", "当前值": f"{taxable_income}", "结果": "✅ 满足"},
            {"政策": "小型微利优惠", "判断条件": "人数 ≤ 300人", "当前值": f"{d['employees']}", "结果": "✅ 满足"},
            {"政策": "高新15%税率", "判断条件": "具备高新资质", "当前值": "是", "结果": "✅ 满足"}
        ]), hide_index=True, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("✅ **已享受**\n\n小微企业普惠减免")
    with c2:
        st.info("💡 **可享受测算**\n\n研发费用100%加计扣除\n\n减免额: ¥ " + f"{d['revenue']*d['rd_ratio']*0.05:,.2f}")
        st.caption("留存备查：研发立项决议、辅助账。")
    with c3:
        st.warning("⚠️ **暂不满足**\n\n软件产品增值税即征即退\n\n原因：未单独核算软件产品收入。")

# ================= 6. 机器学习风险看板 =================
elif menu == "6. ⚠️ 机器学习风险看板":
    st.title("⚠️ 机器学习涉税风险与合规整改")
    st.markdown("识别异常财税指标，输出涉税风险报告并给出合规整改建议。")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        fig = go.Figure(go.Indicator(mode = "gauge+number", value = 82, title = {'text': "风险预警指数"}, gauge = {'bar': {'color': "#EF4444"}}))
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.error("🚨 **高风险：增值税税负率异常**\n- 当前值: 1.2% | 行业均值: 3.5%\n- **整改建议**：核查是否存在未开票收入或进项税违规抵扣。")
        st.warning("⚠️ **中风险：研发费用归集不规范**\n- **整改建议**：建立研发辅助账，区分研发与生产成本。")

# ================= 7. 税收知识图谱与NLP =================
elif menu == "7. 🕸️ 税收知识图谱与NLP":
    st.title("🕸️ 税收知识图谱与NLP智能底座")
    st.markdown("支撑政策推理、表单映射与涉税风险点溯源。")
    
    st.subheader("1. 税收知识图谱网络")
    # 使用 Graphviz 渲染专业知识图谱
    graph = graphviz.Digraph()
    graph.attr(rankdir='LR')
    graph.node('企业', '星耀科技', shape='box', style='filled', color='lightblue')
    graph.node('政策', '研发费用加计扣除', shape='ellipse', style='filled', color='lightgreen')
    graph.node('税种', '企业所得税', shape='box', style='filled', color='lightyellow')
    graph.node('风险', '高新资质不符', shape='diamond', style='filled', color='lightcoral')
    graph.node('表单', 'A类预缴表', shape='note', style='filled', color='lavender')
    
    graph.edge('企业', '政策', label='适用条件')
    graph.edge('政策', '税种', label='影响')
    graph.edge('税种', '表单', label='映射')
    graph.edge('企业', '风险', label='触发')
    st.graphviz_chart(graph)

    st.subheader("2. 财税智能问答 (NLP)")
    st.chat_message("assistant").write("您好！我是基于知识图谱的财税智能助手。")
    if prompt := st.chat_input("询问政策或风险..."):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("根据图谱推理，贵公司符合研发加计扣除条件，请务必保留研发工时分配表备查。")

# ================= 8. 消息提醒与归档 =================
elif menu == "8. 🔔 消息提醒与归档":
    st.title("🔔 政策变动与合规提醒")
    st.markdown("税收政策库动态更新，对政策变更、申报期限、涉税风险事项提供站内提醒。")
    
    with st.container(border=True):
        st.info("📢 **政策变更更新 (2026-10-20)**：财政部发布公告，研发费用加计扣除比例100%制度长期执行。")
        st.warning("⏰ **申报期限提醒**：距离本月增值税及企业所得税申报期截止还有 3 天。")
        st.error("🚨 **涉税风险提醒**：系统检测到进项税负异常，请前往【风险看板】查看整改报告。")
    
    st.markdown("### 订阅设置")
    st.checkbox("接收最新政策变更实时推送", value=True)
    st.checkbox("接收申报期限倒计时提醒", value=True)
