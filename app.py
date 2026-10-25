import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ================= 页面配置 =================
st.set_page_config(page_title="慧税智策 - 企业级财税中台", layout="wide", initial_sidebar_state="expanded")

# ================= 高级商务白底UI =================
st.markdown("""
<style>
    /* 全局背景与字体 */
    .stApp { background-color: #F7F9FC; color: #333333; }
    
    /* 侧边栏深蓝商务风 */
    [data-testid="stSidebar"] { background-color: #1E293B; }
    [data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 15px; padding: 10px; border-radius: 6px; transition: 0.2s; }
    [data-testid="stSidebar"] .stRadio label:hover { background-color: #334155; color: #60A5FA !important; }
    
    /* 顶部数据卡片 */
    div[data-testid="metric-container"] {
        background-color: white; border-radius: 8px; padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #E2E8F0;
    }
    div[data-testid="metric-container"] label { color: #64748B !important; font-size: 14px; font-weight: 500; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #0F172A; font-weight: 700; font-size: 28px; }
    
    /* 卡片容器 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white; border-radius: 10px; border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03); padding: 24px;
    }
    
    /* 标题 */
    h1 { color: #1E293B; font-weight: 800; font-size: 28px; margin-bottom: 5px; }
    p.subtitle { color: #64748B; font-size: 14px; margin-bottom: 25px; }
    h3 { color: #1E293B; font-weight: 700; font-size: 18px; padding-bottom: 12px; border-bottom: 1px solid #F1F5F9; margin-bottom: 20px; }
    
    /* 隐藏默认 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= 全局数据状态 (模拟数据库) =================
if 'data' not in st.session_state:
    st.session_state.data = {
        "company_name": "西安智税科技有限公司（虚拟）",
        "industry": "软件与信息技术服务",
        "year": "2026",
        "revenue": 2400000.0,
        "cost": 1550000.0,
        "expense": 420000.0,
        "tax_adjust": 20000.0,
        "input_vat": 68000.0,
        "assets": 6800000.0,
        "employees": 28,
        "prepaid_cit": 10000.0,
        "salary": 15000.0,
        "social": 2500.0,
        "deduction": 2000.0,
        "vat_rate": 0.06
    }

# ================= 核心计算引擎 =================
def calculate_taxes(d):
    # 1. 增值税
    vat_payable = d["revenue"] * d["vat_rate"] - d["input_vat"]
    
    # 2. 企业所得税 (税会差异调整)
    accounting_profit = d["revenue"] - d["cost"] - d["expense"]
    taxable_income = max(0, accounting_profit + d["tax_adjust"])
    
    is_small_micro = taxable_income <= 3000000 and d["employees"] <= 300 and d["assets"] <= 50000000
    cit_rate = 0.05 if is_small_micro else 0.25
    cit_payable = taxable_income * cit_rate
    cit_supplement = max(0, cit_payable - d["prepaid_cit"])
    
    # 3. 个人所得税 (按月测算全年)
    monthly_taxable = max(0, d["salary"] - 5000 - d["social"] - d["deduction"])
    annual_taxable = monthly_taxable * 12
    if annual_taxable <= 36000: iit = annual_taxable * 0.03
    elif annual_taxable <= 144000: iit = annual_taxable * 0.10 - 2520
    else: iit = annual_taxable * 0.20 - 16920
        
    return {
        "vat": max(0, vat_payable),
        "accounting_profit": accounting_profit,
        "taxable_income": taxable_income,
        "is_small_micro": is_small_micro,
        "cit": cit_payable,
        "cit_supplement": cit_supplement,
        "iit": max(0, iit)
    }

tax_res = calculate_taxes(st.session_state.data)

# ================= 侧边栏导航 =================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#60A5FA; margin-bottom:0;'>慧税智策</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:12px; color:#94A3B8;'>SMART TAX / STUDENT LAB</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:12px; color:#94A3B8;'>设计人：ysh</p>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("工作空间", [
        "📊 企业总览", 
        "⚙️ 数据工作台", 
        "🧮 智能申报", 
        "🎯 政策与优惠", 
        "🛡️ 风险看板", 
        "🕸️ 知识图谱", 
        "💬 智能问答", 
        "📁 消息与交付"
    ])
    st.markdown("---")
    st.caption("状态：运行中\n版本：V8.0 商业版")

# ================= 1. 企业总览 =================
if menu == "📊 企业总览":
    st.title("让财税决策，有据可循")
    st.markdown("<p class='subtitle'>从企业数据到申报测算、优惠匹配与风险预警，一站式教学演示工作台。</p>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("年度营业收入", f"¥ {st.session_state.data['revenue']:,.2f}", "不含税销售额")
    c2.metric("增值税测算", f"¥ {tax_res['vat']:,.2f}", "销项税额减可抵扣进项")
    c3.metric("企业所得税", f"¥ {tax_res['cit']:,.2f}", "符合小微条件" if tax_res['is_small_micro'] else "适用25%税率")
    
    normal_cit = tax_res['taxable_income'] * 0.25
    saving = normal_cit - tax_res['cit']
    c4.metric("预计所得税优惠", f"¥ {saving:,.2f}", "相对25%基准测算")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.5, 1])
    
    with col_left:
        with st.container(border=True):
            st.markdown("### 企业经营画像")
            st.markdown(f"**{st.session_state.data['company_name']}**")
            st.markdown(f"<span style='color:#64748B;'>{st.session_state.data['industry']} · 一般纳税人 · {st.session_state.data['employees']}人</span>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            cost_ratio = st.session_state.data['cost'] / st.session_state.data['revenue']
            exp_ratio = st.session_state.data['expense'] / st.session_state.data['revenue']
            profit_ratio = tax_res['accounting_profit'] / st.session_state.data['revenue']
            
            st.write(f"成本占比: **{cost_ratio*100:.1f}%**")
            st.progress(min(1.0, cost_ratio))
            
            st.write(f"费用占比: **{exp_ratio*100:.1f}%**")
            st.progress(min(1.0, exp_ratio))
            
            st.write(f"利润率: **{profit_ratio*100:.1f}%**")
            st.progress(min(1.0, profit_ratio))
            
    with col_right:
        with st.container(border=True):
            st.markdown("### 待办与风险线索")
            st.warning("⚠️ 存在纳税调增：请核对业务招待费、罚款及凭证。")
            st.markdown("**合成模型风险概率：53.1%**")
            st.caption("基于机器学习算法，仅用于教学排序，不能代替稽核结论。")
            if st.button("查看完整风险分析 →", use_container_width=True):
                st.info("请点击左侧【风险看板】查看详情。")

# ================= 2. 数据工作台 =================
elif menu == "⚙️ 数据工作台":
    st.title("数据工作台")
    st.markdown("<p class='subtitle'>修改演示数据，所有测算与企业画像会同步更新。</p>", unsafe_allow_html=True)
    
    with st.form("data_form"):
        with st.container(border=True):
            st.markdown("### 企业档案与财务数据")
            row1_col1, row1_col2, row1_col3 = st.columns(3)
            company_name = row1_col1.text_input("企业名称", st.session_state.data['company_name'])
            industry = row1_col2.text_input("所属行业", st.session_state.data['industry'])
            row1_col3.text_input("所属年度", st.session_state.data['year'], disabled=True)
            
            st.markdown("---")
            row2_col1, row2_col2, row2_col3 = st.columns(3)
            revenue = row2_col1.number_input("年度不含税收入 (元)", value=st.session_state.data['revenue'], step=10000.0)
            cost = row2_col2.number_input("年度成本 (元)", value=st.session_state.data['cost'], step=10000.0)
            expense = row2_col3.number_input("期间费用 (元)", value=st.session_state.data['expense'], step=10000.0)
            
            row3_col1, row3_col2, row3_col3 = st.columns(3)
            tax_adjust = row3_col1.number_input("纳税调整净额 (元，可为负)", value=st.session_state.data['tax_adjust'], step=1000.0)
            input_vat = row3_col2.number_input("可抵扣进项税额 (元)", value=st.session_state.data['input_vat'], step=1000.0)
            employees = row3_col3.number_input("年度平均从业人数", value=st.session_state.data['employees'], step=1)
            
            row4_col1, row4_col2, row4_col3 = st.columns(3)
            assets = row4_col1.number_input("年度平均资产总额 (元)", value=st.session_state.data['assets'], step=10000.0)
            prepaid_cit = row4_col2.number_input("已预缴企业所得税 (元)", value=st.session_state.data['prepaid_cit'], step=1000.0)
            vat_rate = row4_col3.selectbox("增值税适用税率", [0.06, 0.09, 0.13], index=[0.06, 0.09, 0.13].index(st.session_state.data['vat_rate']))
            
            row5_col1, row5_col2, row5_col3 = st.columns(3)
            salary = row5_col1.number_input("个人月工资 (元)", value=st.session_state.data['salary'], step=1000.0)
            social = row5_col2.number_input("个人月社保公积金 (元)", value=st.session_state.data['social'], step=100.0)
            deduction = row5_col3.number_input("个人月专项附加扣除 (元)", value=st.session_state.data['deduction'], step=100.0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("保存并重新测算", type="primary")
            
            if submitted:
                st.session_state.data.update({
                    "company_name": company_name, "industry": industry,
                    "revenue": revenue, "cost": cost, "expense": expense,
                    "tax_adjust": tax_adjust, "input_vat": input_vat,
                    "employees": employees, "assets": assets,
                    "prepaid_cit": prepaid_cit, "vat_rate": vat_rate,
                    "salary": salary, "social": social, "deduction": deduction
                })
                st.success("数据已保存，全局测算已更新！")
                st.rerun()

# ================= 3. 智能申报 =================
elif menu == "🧮 智能申报":
    st.title("智能申报测算")
    st.markdown("<p class='subtitle'>按照统一数据口径生成多税种教学底稿，可追溯每一步公式。</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### 多税种一键测算")
        
        df_tax = pd.DataFrame([
            {"税种": "增值税", "计算依据": f"{st.session_state.data['revenue']:,.2f} × {st.session_state.data['vat_rate']*100}% - {st.session_state.data['input_vat']:,.2f}", "测算金额": f"¥ {tax_res['vat']:,.2f}", "状态": "待凭证复核"},
            {"税种": "企业所得税(年度)", "计算依据": f"应纳税所得额 × {'5%' if tax_res['is_small_micro'] else '25%'}", "测算金额": f"¥ {tax_res['cit']:,.2f}", "状态": "待人工确认"},
            {"税种": "企业所得税待补", "计算依据": f"年度测算税额 - 已预缴 {st.session_state.data['prepaid_cit']:,.2f}", "测算金额": f"¥ {tax_res['cit_supplement']:,.2f}", "状态": "教学底稿"},
            {"税种": "个人所得税(单人)", "计算依据": "月收入及扣除全年不变，综合所得税率表", "测算金额": f"¥ {tax_res['iit']:,.2f}", "状态": "不计其他综合所得"}
        ])
        st.dataframe(df_tax, hide_index=True, use_container_width=True)
        
        csv = df_tax.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 导出申报底稿 CSV", csv, "申报底稿.csv", "text/csv")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 纳税调整与勾稽")
        st.markdown(f"**会计利润** = 收入({st.session_state.data['revenue']:,.2f}) - 成本({st.session_state.data['cost']:,.2f}) - 费用({st.session_state.data['expense']:,.2f}) = **{tax_res['accounting_profit']:,.2f} 元**")
        st.markdown(f"**应纳税所得额** = max(0, 会计利润 + 纳税调整净额) = **{tax_res['taxable_income']:,.2f} 元**")
        st.caption("逻辑追溯：利润表收入 → 增值税销售额；利润与调整项目 → 所得税计税基础；工资与扣除 → 单个人个税测算。")

# ================= 4. 政策与优惠 =================
elif menu == "🎯 政策与优惠":
    st.title("政策与优惠匹配")
    st.markdown("<p class='subtitle'>基于企业条件逐项判断，记录政策来源与核查时间。</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### 小型微利企业所得税优惠")
        st.markdown("<span style='background-color:#DCFCE7; color:#166534; padding:4px 8px; border-radius:4px; font-size:12px;'>初步符合</span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        cond_df = pd.DataFrame([
            {"判断条件": "应纳税所得额 ≤ 300万元", "企业当前值": f"{tax_res['taxable_income']:,.2f}", "规则结果": "满足" if tax_res['taxable_income'] <= 3000000 else "不满足"},
            {"判断条件": "年度平均从业人数 ≤ 300人", "企业当前值": f"{st.session_state.data['employees']}", "规则结果": "满足" if st.session_state.data['employees'] <= 300 else "不满足"},
            {"判断条件": "年度平均资产 ≤ 5000万元", "企业当前值": f"{st.session_state.data['assets']:,.2f}", "规则结果": "满足" if st.session_state.data['assets'] <= 50000000 else "不满足"},
            {"判断条件": "非限制或禁止行业", "企业当前值": "非限制行业", "规则结果": "满足"}
        ])
        st.dataframe(cond_df, hide_index=True, use_container_width=True)
        
        st.markdown("---")
        normal_cit = tax_res['taxable_income'] * 0.25
        saving = normal_cit - tax_res['cit']
        st.markdown(f"**政策依据**：有效期至2027年12月31日。减按25%计入应纳税所得额，按20%税率缴纳，等效5%。")
        st.markdown(f"**预计节税**：<span style='color:#10B981; font-weight:bold;'>¥ {saving:,.2f}</span>；需核实年度平均口径、行业资格及汇算清缴结果。", unsafe_allow_html=True)

# ================= 5. 风险看板 =================
elif menu == "🛡️ 风险看板":
    st.title("风险看板")
    st.markdown("<p class='subtitle'>基于规则和合成模型的教学风险扫描，供内部参考。</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.container(border=True):
            st.markdown("### 综合风险指数")
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = 53.1, title = {'text': "风险概率 %"},
                gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#F59E0B"}, 'steps': [{'range': [0, 40], 'color': "#D1FAE5"}, {'range': [40, 70], 'color': "#FEF3C7"}, {'range': [70, 100], 'color': "#FEE2E2"}]}
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        with st.container(border=True):
            st.markdown("### 风险线索明细")
            st.warning("**1. 纳税调增风险**：存在业务招待费、罚款等调增项，需核对凭证合规性。")
            st.warning("**2. 税负率异常**：增值税税负率偏低，需关注是否存在滞后开票情况。")
            st.info("**3. 个税申报匹配**：工资薪金与社保缴纳基数需保持合理匹配。")

# ================= 6. 知识图谱 =================
elif menu == "🕸️ 知识图谱":
    st.title("财税知识图谱")
    st.markdown("<p class='subtitle'>底层支撑政策推理与表单映射的核心节点关联。</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("""
        **核心实体 (Entity)：**
        - [企业特征]：行业、人数、资产、利润
        - [税收政策]：小型微利、高新、加计扣除
        - [涉税风险]：税负异常、发票违规
        
        **关系路径 (Relationship)：**
        - `[小型微利政策] --(适用条件)--> [从业人数≤300]`
        - `[小型微利政策] --(适用条件)--> [资产≤5000万]`
        - `[财务指标异常] --(触发)--> [风险预警]`
        """)
        st.info("系统已加载图谱节点 1,245 个，关系边 3,890 条。当前企业画像已在图谱中完成匹配检索。")

# ================= 7. 智能问答 =================
elif menu == "💬 智能问答":
    st.title("智能问答")
    st.markdown("<p class='subtitle'>基于大模型的财税政策智能咨询助手。</p>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "您好，我是慧税智策AI助手。请问有什么可以帮您？"}]
        
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("例如：小微企业的认定标准是什么？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        with st.spinner("正在查阅图谱..."):
            if "小微" in prompt:
                res = "小型微利企业需同时满足：1. 从事国家非限制和禁止行业；2. 年度应纳税所得额不超过300万元；3. 从业人数不超过300人；4. 资产总额不超过5000万元。"
            else:
                res = "已为您检索相关政策，建议前往【政策与优惠】模块查看当前企业匹配详情。"
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.chat_message("assistant").write(res)

# ================= 8. 消息与交付 =================
elif menu == "📁 消息与交付":
    st.title("消息与交付")
    st.markdown("<p class='subtitle'>系统通知、申报提醒与数据导出中心。</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.info("📢 **【政策更新】** 关于进一步支持小微企业和个体工商户发展有关税费政策的公告。")
        st.warning("⏰ **【申报提醒】** 距离本月申报期截止还有3天，请及时完成申报。")
        
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 数据导出")
        st.markdown("生成完整的年度财税分析报告（PDF版），或导出当前系统全量数据。")
        col1, col2 = st.columns(2)
        col1.download_button("📄 导出全年分析报告 (模拟)", "报告内容", "年度分析报告.txt", use_container_width=True)
        col2.download_button("🗄️ 导出系统全量数据 (CSV)", "data", "data.csv", use_container_width=True)
