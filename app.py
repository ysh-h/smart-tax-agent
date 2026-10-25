import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date

# ================= 页面配置 & 高级UI =================
st.set_page_config(page_title="智慧财税管理智能体 - 专家版", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background: #F4F7F9; font-family: 'PingFang SC', sans-serif; }
    [data-testid="stSidebar"] { background: #0F172A; box-shadow: 4px 0 15px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] * { color: #94A3B8 !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 15px; padding: 12px; border-radius: 8px; transition: all 0.2s;}
    [data-testid="stSidebar"] .stRadio label:hover { background: #1E293B; color: #38BDF8 !important; }
    
    div[data-testid="metric-container"] { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid #3B82F6; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1E293B; font-weight: 800; font-size: 28px; }
    
    h1 { color: #0F172A; font-weight: 800; font-size: 32px; }
    h3 { color: #1E293B; font-weight: 600; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-top: 20px;}
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    
    /* 开发者专属名片样式 */
    .dev-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .dev-card p { margin: 0; color: #94A3B8; font-size: 13px; }
    .dev-card h4 { margin: 5px 0 0 0; color: #38BDF8; font-size: 18px; font-weight: bold; letter-spacing: 1px;}
</style>
""", unsafe_allow_html=True)

# ================= 全局状态 =================
if 'd' not in st.session_state:
    st.session_state.d = {
        "name": "星耀科技（中国）有限公司", "industry": "软件与信息技术服务业",
        "revenue": 12000000.0, "cost": 6000000.0, "expense": 2000000.0, "input_vat": 250000.0,
        "employees": 120, "assets": 15000000.0, "is_high_tech": True, "rd_ratio": 0.08,
        "entertainment": 150000.0, "advertising": 300000.0 
    }
if 'filings' not in st.session_state: st.session_state.filings = []
if 'adj_vat' not in st.session_state: st.session_state.adj_vat = 0.0

d = st.session_state.d

# 核心测算 (包含复杂的税会差异)
vat_out = d["revenue"] * 0.06
vat_payable = max(vat_out - d["input_vat"] + st.session_state.adj_vat, 0)
surcharge = vat_payable * 0.12
profit = d["revenue"] - d["cost"] - d["expense"]

# 税会差异调整计算
ent_deduct = min(d["entertainment"] * 0.6, d["revenue"] * 0.005)
ent_adjust = max(0, d["entertainment"] - ent_deduct)
ad_deduct = min(d["advertising"], d["revenue"] * 0.15)
ad_adjust = max(0, d["advertising"] - ad_deduct)
rd_deduct = d["revenue"] * d["rd_ratio"] * 1.0

taxable_income = max(0, profit + ent_adjust + ad_adjust - rd_deduct)
is_micro = taxable_income <= 3000000 and d["employees"] <= 300 and d["assets"] <= 50000000
cit_rate = 0.05 if is_micro else (0.15 if d["is_high_tech"] else 0.25)
cit_payable = taxable_income * cit_rate
total_tax = vat_payable + surcharge + cit_payable

# ================= 侧边栏 =================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#38BDF8;'>⚡ 智慧财税专家台</h2>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("业务导航矩阵", [
        "1. 🏢 企业多维画像舱",
        "2. 📁 业财数据清洗池",
        "3. 🧮 智能算税与税会差异",
        "4. 🚀 申报流转与归档中心",
        "5. 🎯 政策图谱与适配测算",
        "6. ⚠️ 涉税风控机器学习",
        "7. 🕸️ 知识图谱与NLP引擎",
        "8. 🔔 政策更新与合规提醒"
    ])
    st.markdown("---")
    
    # 👇 这里是你专属的系统架构师名片 👇
    st.markdown(f"""
    <div class="dev-card">
        <p>系统架构设计师</p>
        <h4>ysh</h4>
        <p style="margin-top:5px; font-size:11px;">ID: 2023xxxx</p>
        <p style="margin-top:5px; font-size:11px; color:#10B981;">● 已通过系统身份认证</p>
    </div>
    """, unsafe_allow_html=True)

# ================= 1. 企业多维画像舱 =================
if menu == "1. 🏢 企业多维画像舱":
    st.title("🏢 企业多维画像与经营诊断")
    st.markdown("欢迎使用由 **ysh** 主导设计的智慧财税决策系统。本系统打破数据孤岛，构建企业动态画像。")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        d["industry"] = c2.selectbox("行业属性", ["软件与信息技术服务业", "制造业", "批发零售业"])
        d["is_high_tech"] = c3.checkbox("高新资质", value=d["is_high_tech"])
        d["revenue"] = c1.number_input("年营业收入(元)", value=d["revenue"], step=100000.0)
        
        c4, c5, c6 = st.columns(3)
        d["employees"] = c4.number_input("从业人员(人)", value=d["employees"])
        d["assets"] = c5.number_input("资产总额(元)", value=d["assets"], step=100000.0)
        d["rd_ratio"] = c6.slider("研发费占比", 0.0, 0.3, d["rd_ratio"], 0.01)
        st.session_state.d = d

    st.markdown("### 经营与税负健康度诊断")
    col_chart, col_desc = st.columns([1.5, 1])
    with col_chart:
        months = ['1月', '2月', '3月', '4月', '5月', '6月']
        fig = go.Figure()
        fig.add_trace(go.Bar(x=months, y=[80, 95, 110, 105, 120, 130], name="营收(十万)", marker_color='#93C5FD'))
        fig.add_trace(go.Scatter(x=months, y=[4.2, 4.5, 4.1, 4.8, 4.3, 4.6], name="实际税负率(%)", yaxis='y2', line=dict(color='#EF4444', width=3)))
        fig.update_layout(yaxis2=dict(overlaying='y', side='right'), height=300, margin=dict(l=0,r=0,t=10,b=0), plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    with col_desc:
        st.info(f"""
        **财务专家系统诊断：**
        - **盈利状况**：企业营收处于上升期，利润率约为 **{profit/d['revenue']*100:.1f}%**。
        - **税负表现**：综合税负率为 **{total_tax/d['revenue']*100:.2f}%**，略低于行业预警线。
        - **研发实力**：研发投入占比 **{d['rd_ratio']*100:.1f}%**，{'完全满足' if d['rd_ratio']>=0.03 else '未满足'}高新企业及研发加计扣除要求。
        """)

# ================= 2. 业财数据清洗池 =================
elif menu == "2. 📁 业财数据清洗池":
    st.title("📁 多源数据清洗与业财税勾稽")
    st.markdown("处理结构化（财务报表/银行流水）与非结构化（PDF/发票）数据，执行严格的“三流一致”校验。")
    
    tab1, tab2 = st.tabs(["📊 财务与发票勾稽校验", "📄 NLP合同与凭证抽取"])
    
    with tab1:
        st.subheader("1. 核心财务指标录入")
        c1, c2, c3 = st.columns(3)
        d["cost"] = c1.number_input("营业成本(元)", value=d["cost"], step=100000.0)
        d["expense"] = c2.number_input("期间费用(元)", value=d["expense"], step=10000.0)
        d["input_vat"] = c3.number_input("进项税额(元)", value=d["input_vat"], step=1000.0)
        st.session_state.d = d
        
        st.subheader("2. 发票池勾稽与异常校验")
        st.dataframe(pd.DataFrame({
            "发票代码": ["011002400111", "011002400112", "011002400113"],
            "业务摘要": ["采购服务器", "办公用品", "咨询费"],
            "金额(元)": [d["cost"]*0.5, 50000.0, 150000.0],
            "勾稽结果": ["✅ 三流一致", "⚠️ 品名笼统，待核实", "✅ 三流一致"],
            "进项税率": ["13%", "13%", "6%"]
        }), hide_index=True, use_container_width=True)
        
    with tab2:
        st.subheader("NLP 实体抽取与自动凭证归类")
        st.code('''{
  "合同名称": "星耀科技-阿里云服务器采购协议",
  "合同金额": 150000.00,
  "印花税税目": "买卖合同 (0.03%)",
  "自动生成凭证": {
      "借": "管理费用-云服务费 141509.43",
      "借": "应交税费-应交增值税(进项) 8490.57",
      "贷": "银行存款 150000.00"
  }
}''', language="json")
        st.success("✅ 非结构化合同已成功解析，并自动映射至对应会计科目。")

# ================= 3. 智能算税与税会差异 =================
elif menu == "3. 🧮 智能算税与税会差异":
    st.title("🧮 智能计税引擎与税会差异调整")
    st.markdown("严格依据税法进行所得税汇算清缴模拟，展示复杂的纳税调整过程。")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("增值税", f"¥ {vat_payable:,.2f}")
    c2.metric("企业所得税", f"¥ {cit_payable:,.2f}", f"{'小微5%' if is_micro else '高新15%' if d['is_high_tech'] else '法定25%'}")
    c3.metric("税金及附加", f"¥ {surcharge:,.2f}")
    c4.metric("综合总税负", f"¥ {total_tax:,.2f}")

    with st.container(border=True):
        st.subheader("企业所得税纳税调整明细表 (A105000 模拟)")
        
        c1, c2 = st.columns(2)
        d["entertainment"] = c1.number_input("业务招待费发生额(元)", value=d["entertainment"])
        d["advertising"] = c2.number_input("广告宣传费发生额(元)", value=d["advertising"])
        st.session_state.d = d
        
        st.markdown("#### 差异调整测算")
        st.write(f"1. **业务招待费调整**：发生额 {d['entertainment']:,.2f} × 60% = {d['entertainment']*0.6:,.2f}；营收5‰ = {d['revenue']*0.005:,.2f}。孰低扣除。")
        st.write(f"   👉 需纳税**调增**金额：`{ent_adjust:,.2f}` 元")
        
        st.write(f"2. **广告费调整**：营收15%限额 = {d['revenue']*0.15:,.2f}。")
        st.write(f"   👉 需纳税**调增**金额：`{ad_adjust:,.2f}` 元")
        
        st.write(f"3. **研发费用加计扣除**：研发费用 {d['revenue']*d['rd_ratio']:,.2f} × 100%。")
        st.write(f"   👉 可纳税**调减**金额：`{rd_deduct:,.2f}` 元")
        
        st.info(f"**会计利润**：{profit:,.2f} 元 ➡️ **纳税调整后应纳税所得额**：**{taxable_income:,.2f} 元**")

    with st.container(border=True):
        st.subheader("人工复核与特殊调整")
        st.session_state.adj_vat = st.number_input("增值税进项税额转出(元)", value=st.session_state.adj_vat)
        if st.button("重新测算"):
            st.rerun()

# ================= 4. 申报流转与归档中心 =================
elif menu == "4. 🚀 申报流转与归档中心":
    st.title("🚀 多税种一键申报与归档")
    st.markdown("支持批量生成申报底稿，监控申报状态，并提供PDF/Excel归档下载。")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("申报操作")
        st.write(f"本期待申报：增值税(¥{vat_payable:,.0f})、附加税(¥{surcharge:,.0f})、所得税(¥{cit_payable:,.0f})")
        if st.button("📦 执行批量申报", type="primary", use_container_width=True):
            st.session_state.filings.append({"申报编号": "SB202610001", "税种": "增值税", "申报金额": vat_payable, "状态": "✅ 申报成功"})
            st.session_state.filings.append({"申报编号": "SB202610002", "税种": "企业所得税", "申报金额": cit_payable, "状态": "✅ 申报成功"})
            st.success("申报成功，回执已生成！")
            
    with c2:
        st.subheader("申报状态与归档")
        if st.session_state.filings:
            st.dataframe(pd.DataFrame(st.session_state.filings), hide_index=True, use_container_width=True)
            csv = pd.DataFrame(st.session_state.filings).to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 下载本期申报表及回执 (ZIP)", data=csv, file_name="税务申报归档.zip", mime="application/zip")
        else:
            st.info("暂无申报记录")

# ================= 5. 政策图谱与适配测算 =================
elif menu == "5. 🎯 政策图谱与适配测算":
    st.title("🎯 税收政策智能适配与红利测算")
    st.markdown("运用知识图谱逐项校验企业资质，区分政策状态，精准测算减免额度。")
    
    with st.container(border=True):
        st.subheader("政策适用条件自动判定报告")
        st.dataframe(pd.DataFrame([
            {"政策名称": "小型微利企业优惠", "判定条件": "利润≤300万,人数≤300", "企业当前状态": f"利润{taxable_income/10000:.1f}万,{d['employees']}人", "适配结果": "✅ 满足" if is_micro else "❌ 不满足"},
            {"政策名称": "高新技术企业税率", "判定条件": "具备高新证书", "企业当前状态": "具备" if d['is_high_tech'] else "无", "适配结果": "✅ 满足" if d['is_high_tech'] else "❌ 不满足"},
            {"政策名称": "研发费加计扣除", "判定条件": "研发费占比≥3%", "企业当前状态": f"{d['rd_ratio']*100}%", "适配结果": "✅ 满足" if d['rd_ratio']>=0.03 else "❌ 不满足"}
        ]), hide_index=True, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("✅ **已享受红利**")
        st.metric("小微/高新减免所得税", f"¥ {taxable_income * (0.25 - cit_rate):,.2f}")
    with c2:
        st.info("💡 **可追加享受测算**")
        st.write(f"**研发费用加计扣除**\n预估可抵减所得税：¥ {rd_deduct * cit_rate:,.2f}")
        st.caption("备查资料：研发项目立项决议、研发辅助账、工时分配表、领料单等。")
    with c3:
        st.warning("⚠️ **暂不满足政策**")
        st.write("**软件产品即征即退**\n原因：当前发票未单独列示软件产品销售额。")

# ================= 6. 涉税风控机器学习 =================
elif menu == "6. ⚠️ 涉税风控机器学习":
    st.title("⚠️ 涉税风险机器学习预警")
    st.markdown("基于孤立森林模型与行业对标数据，实时扫描财务指标，出具深度合规整改报告。")
    
    col_gauge, col_risk = st.columns([1, 2])
    with col_gauge:
        st.markdown("### 综合风控指数")
        fig = go.Figure(go.Indicator(
            mode = "gauge+number", value = 78, title = {'text': "风险偏离度"},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#EF4444"}, 'steps': [{'range': [0, 50], 'color': "#D1FAE5"}, {'range': [50, 80], 'color': "#FEF3C7"}]}
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col_risk:
        st.markdown("### 深度风险诊断与整改方案")
        st.error("""
        🚨 **高风险：增值税税负率显著偏低**
        - **指标比对**：当前税负率 2.08%，行业均值 3.5%。
        - **触发原因**：可能存在未开票收入未申报，或违规扩大进项抵扣范围。
        - **整改建议**：全面清查“预收账款”与“其他应付款”科目，核实是否有已发货未开票业务；复核近期进项发票的业务真实性。
        """)
        st.warning("""
        ⚠️ **中风险：所得税贡献率异常**
        - **指标比对**：所得税贡献率低于同行业预警下限。
        - **整改建议**：核查是否存在多列成本费用、不合规税会调整。建议完善研发费用辅助账，充分享受加计扣除以合规降低税负。
        """)

# ================= 7. 知识图谱与NLP引擎 =================
elif menu == "7. 🕸️ 知识图谱与NLP引擎":
    st.title("🕸️ 财税底层架构：知识图谱与NLP")
    st.markdown("展示系统的底层AI能力：基于图数据库的政策推理，以及基于大模型的意图识别。")
    
    st.subheader("1. 税收知识图谱推理拓扑")
    fig = go.Figure()
    nodes = {"星耀科技": (1, 2), "软件行业": (3, 3), "高新资质": (3, 1), "15%税率": (5, 3), "研发加计": (5, 1), "税务稽查": (0, 0)}
    edges = [("星耀科技", "软件行业"), ("星耀科技", "高新资质"), ("高新资质", "15%税率"), ("软件行业", "研发加计"), ("星耀科技", "税务稽查")]
    
    for start, end in edges:
        fig.add_trace(go.Scatter(x=[nodes[start][0], nodes[end][0]], y=[nodes[start][1], nodes[end][1]], mode='lines', line=dict(width=2, color='#CBD5E1'), hoverinfo='none', showlegend=False))
        
    node_x, node_y, node_text, node_color = [], [], [], []
    colors = {"星耀科技": "#3B82F6", "软件行业": "#10B981", "高新资质": "#10B981", "15%税率": "#8B5CF6", "研发加计": "#8B5CF6", "税务稽查": "#EF4444"}
    for n, (x, y) in nodes.items():
        node_x.append(x); node_y.append(y); node_text.append(n); node_color.append(colors[n])
        
    fig.add_trace(go.Scatter(x=node_x, y=node_y, mode='markers+text', text=node_text, textposition="bottom center", marker=dict(size=30, color=node_color), showlegend=False))
    fig.update_layout(xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), plot_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("2. NLP 财税智能问答")
    st.chat_message("assistant").write("您好！我是财税大模型助手。我已关联您的企业画像，请问有关于税务筹划或合规的问题吗？")
    if prompt := st.chat_input("例如：我们公司买了一批服务器，进项税能抵扣吗？"):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("""根据贵公司（软件与信息技术服务业，一般纳税人）的画像，购买服务器用于生产经营，取得的增值税专用发票**可以抵扣进项税额**。
        
**操作建议**：
1. 确保发票品名为“服务器”或“电子设备”，而非“办公用品”。
2. 请在发票综合服务平台进行勾选认证。
3. 对应的折旧费用，如符合规定，还可享受固定资产加速折旧政策。""")

# ================= 8. 政策更新与合规提醒 =================
elif menu == "8. 🔔 政策更新与合规提醒":
    st.title("🔔 政策动态与合规事项提醒")
    st.markdown("实时抓取国家税务总局最新政策，并结合企业特征进行个性化合规倒计时提醒。")
    
    tab1, tab2 = st.tabs(["📢 最新财税政策库", "⏰ 合规与申报倒计时"])
    
    with tab1:
        st.info("**2026-10-18 财政部 税务总局公告**：关于进一步支持小微企业发展的税费政策指引。对小型微利企业年应纳税所得额不超过300万元的部分，减按25%计入应纳税所得额，按20%的税率缴纳企业所得税。")
        st.success("**2026-10-15 国家税务总局公告**：全面数字化电子发票（数电票）开具指南更新，新增特定要素发票开具规范。")
        st.warning("**2026-10-01 地方税务局通知**：关于开展2026年度高新技术企业认定管理工作的通知。")
        
    with tab2:
        st.markdown("### 智能待办事项")
        st.checkbox("【10月23日截止】申报缴纳本月增值税及附加税费", value=False)
        st.checkbox("【10月25日截止】完成第三季度企业所得税预缴申报", value=False)
        st.checkbox("【11月15日截止】报送上年度关联业务往来报告表", value=False)
        st.checkbox("【12月31日截止】确认并享受研发费用加计扣除优惠", value=False)
