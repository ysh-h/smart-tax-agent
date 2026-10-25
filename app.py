import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ================= 页面配置 =================
st.set_page_config(page_title="AI-Tax 智能财税驾驶舱", layout="wide", initial_sidebar_state="expanded")

# ================= 高级科技感UI美化 =================
st.markdown("""
<style>
    /* 全局深色科技背景 */
    .stApp { background: #0B1120; color: #E2E8F0; }
    
    /* 侧边栏发光效果 */
    [data-testid="stSidebar"] { 
        background: #111827; 
        border-right: 1px solid #1E293B;
        box-shadow: 2px 0 10px rgba(6, 182, 212, 0.1);
    }
    [data-testid="stSidebar"] * { color: #94A3B8 !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 15px; padding: 10px; border-radius: 8px; transition: 0.3s; }
    [data-testid="stSidebar"] .stRadio label:hover { background: #1E293B; color: #06B6D4 !important; }
    
    /* 霓虹指标卡片 */
    div[data-testid="metric-container"] {
        background: linear-gradient(145deg, #111827, #0F172A); 
        border-radius: 12px; padding: 20px;
        border: 1px solid #1E293B;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4), inset 0 0 10px rgba(6, 182, 212, 0.05);
    }
    div[data-testid="metric-container"] label { color: #38BDF8 !important; font-size: 14px; font-weight: 600; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #F8FAFC; font-weight: 800; font-size: 26px; text-shadow: 0 0 10px rgba(255,255,255,0.2); }
    
    /* 卡片容器 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #111827; border-radius: 12px; border: 1px solid #1E293B;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2); padding: 20px;
    }
    
    /* 标题渐变文字 */
    h1 { 
        background: -webkit-linear-gradient(45deg, #38BDF8, #818CF8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 900; font-size: 36px; margin-bottom: 5px; 
    }
    p.subtitle { color: #64748B; font-size: 15px; margin-bottom: 30px; }
    h3 { color: #E2E8F0; font-weight: 700; font-size: 18px; padding-bottom: 10px; border-bottom: 1px solid #1E293B; margin-bottom: 20px; }
    
    /* 表格美化 */
    .stDataFrame { background: #1E293B; border-radius: 8px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= 数据初始化 =================
if 'tax_data' not in st.session_state:
    st.session_state.tax_data = {
        "company": "西安智税科技有限公司",
        "industry": "软件和信息技术服务业",
        "revenue": 1200000.0,
        "cost": 650000.0,
        "expense": 180000.0,
        "input_vat": 35000.0,
        "employees": 25,
        "assets": 4000000.0
    }

# ================= 核心计算引擎 =================
def calc_tax(d):
    # 1. 增值税 (假设税率6%)
    vat = d["revenue"] * 0.06 - d["input_vat"]
    vat = max(0, vat)
    
    # 2. 企业所得税 (带小微判断)
    profit = d["revenue"] - d["cost"] - d["expense"]
    is_micro = profit <= 3000000 and d["employees"] <= 300 and d["assets"] <= 50000000
    cit_rate = 0.05 if is_micro else 0.25
    cit = max(0, profit) * cit_rate
    
    return {"vat": vat, "profit": profit, "is_micro": is_micro, "cit": cit}

res = calc_tax(st.session_state.tax_data)

# ================= 侧边栏导航 =================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#38BDF8;'>⚡ AI-Tax 驾驶舱</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:12px; color:#64748B;'>Design by ysh</p>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("系统导航", [
        "🖥️ 数据控制台", 
        "⚙️ 财务底座设定", 
        "📊 智能税算与申报", 
        "🎯 政策红利雷达", 
        "🛡️ 风控与异常预警", 
        "🧠 财税知识问答"
    ])

# ================= 1. 数据控制台 =================
if menu == "🖥️ 数据控制台":
    st.title("AI-Tax 智能财税驾驶舱")
    st.markdown("<p class='subtitle'>基于大数据的实时财税态势感知与决策指挥中枢。</p>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("年度总营收", f"¥ {st.session_state.tax_data['revenue']:,.2f}")
    c2.metric("预估增值税", f"¥ {res['vat']:,.2f}")
    c3.metric("预估所得税", f"¥ {res['cit']:,.2f}")
    
    # 估算优惠
    normal_cit = res['profit'] * 0.25 if res['profit'] > 0 else 0
    saving = normal_cit - res['cit']
    c4.metric("政策红利释放", f"¥ {saving:,.2f}", "小微优惠叠加" if res['is_micro'] else "无")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        with st.container(border=True):
            st.markdown("### 企业健康度多维雷达")
            fig = go.Figure(go.Scatterpolar(
                r=[85, 70, 90, 80, 60], theta=['盈利能力', '营运效率', '研发投入', '税务合规', '现金流'],
                fill='toself', line_color='#06B6D4', fillcolor='rgba(6, 182, 212, 0.2)'
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=False, range=[0, 100]), bgcolor='#111827'),
                paper_bgcolor='rgba(0,0,0,0)', font_color='#E2E8F0', showlegend=False, height=350,
                margin=dict(l=40, r=40, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        with st.container(border=True):
            st.markdown("### 智能诊断摘要")
            st.info(f"**画像特征**：{st.session_state.tax_data['company']}，属于{st.session_state.tax_data['industry']}，从业人数{st.session_state.tax_data['employees']}人。")
            if res['is_micro']:
                st.success("✅ **利好**：该企业当前指标完全符合【小型微利企业】标准，适用5%实际税负！")
            else:
                st.warning("⚠️ **提示**：当前企业利润或资产超标，无法享受小微优惠，请关注其他政策。")
            
            st.markdown("---")
            st.markdown("**AI 预测**：未来季度资金流健康，但进项抵扣占比仅为 28%，建议合理规划采购周期以优化税负。")

# ================= 2. 财务底座设定 =================
elif menu == "⚙️ 财务底座设定":
    st.title("财务底座数据录入")
    st.markdown("<p class='subtitle'>在此修改底层财务账套数据，系统将瞬间联动全局测算与预警。</p>", unsafe_allow_html=True)
    
    with st.form("data_input"):
        with st.container(border=True):
            st.markdown("### 基础经营指标")
            col1, col2, col3 = st.columns(3)
            comp = col1.text_input("企业名称", st.session_state.tax_data['company'])
            rev = col2.number_input("年度营业收入 (元)", value=st.session_state.tax_data['revenue'], step=10000.0)
            cost = col3.number_input("年度营业成本 (元)", value=st.session_state.tax_data['cost'], step=10000.0)
            
            st.markdown("### 费用与抵扣")
            col4, col5, col6 = st.columns(3)
            exp = col4.number_input("期间费用 (元)", value=st.session_state.tax_data['expense'], step=10000.0)
            in_vat = col5.number_input("进项税额 (元)", value=st.session_state.tax_data['input_vat'], step=1000.0)
            emp = col6.number_input("平均从业人数", value=st.session_state.tax_data['employees'])
            
            st.markdown("### 资产状况")
            asset = st.number_input("资产总额 (元)", value=st.session_state.tax_data['assets'], step=100000.0)
            
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🚀 保存并重新全局运算", type="primary", use_container_width=True)
            
            if submitted:
                st.session_state.tax_data.update({
                    "company": comp, "revenue": rev, "cost": cost,
                    "expense": exp, "input_vat": in_vat, "employees": emp, "assets": asset
                })
                st.success("数据已写入数据库，全局页面同步更新！")
                st.rerun()

# ================= 3. 智能税算与申报 =================
elif menu == "📊 智能税算与申报":
    st.title("智能税算与申报中枢")
    st.markdown("<p class='subtitle'>透明化展示税会差异调整，生成标准申报底稿。</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### 核心税种测算")
        df = pd.DataFrame([
            {"税种": "增值税", "公式依据": f"营收({st.session_state.tax_data['revenue']}) * 6% - 进项({st.session_state.tax_data['input_vat']})", "测算金额(元)": f"{res['vat']:,.2f}", "状态": "待复核"},
            {"税种": "企业所得税", "公式依据": f"利润({res['profit']}) * {'5%(小微)' if res['is_micro'] else '25%'}", "测算金额(元)": f"{res['cit']:,.2f}", "状态": "已优化"}
        ])
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        st.markdown("### 税会差异调整底稿")
        st.markdown(f"1. 会计利润 = 收入 - 成本 - 费用 = **{res['profit']:,.2f}** 元")
        st.markdown(f"2. 纳税调整增加额 = **0.00** 元")
        st.markdown(f"3. 应纳税所得额 = **{res['profit']:,.2f}** 元")
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 导出申报数据底稿 (CSV)", csv, "tax_report.csv")

# ================= 4. 政策红利雷达 =================
elif menu == "🎯 政策红利雷达":
    st.title("政策红利智能雷达")
    st.markdown("<p class='subtitle'>利用规则引擎精准锁定企业可享受的税收红利。</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        with st.container(border=True):
            st.markdown("### 政策匹配漏斗")
            # 漏斗图展示筛选过程
            fig = go.Figure(go.Funnel(
                y = ["全量政策库", "行业初筛", "规模达标", "最终强匹配"],
                x = [120, 45, 15, 3],
                textinfo = "value+percent initial",
                marker = {"color": ["#1E3A8A", "#3B82F6", "#06B6D4", "#10B981"]}
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#E2E8F0', height=300, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        with st.container(border=True):
            st.markdown("### 匹配详情")
            if res['is_micro']:
                st.success("**✔️ 小型微利企业所得税优惠**\n\n条件：利润≤300万、人数≤300、资产≤5000万。\n\n**节税效益**：实际税负由25%降至5%。")
            else:
                st.error("**❌ 小型微利企业优惠未命中**\n\n原因：利润或资产超标。")
                
            st.info("**✔️ 研发费用加计扣除（100%）**\n\n提示：需建立辅助账，归集研发人员工时。")

# ================= 5. 风控与异常预警 =================
elif menu == "🛡️ 风控与异常预警":
    st.title("AI 涉税风控中心")
    st.markdown("<p class='subtitle'>结合机器学习算法，实时诊断企业经营指标健康度。</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 税负率监控")
            # 计算税负率
            burden = res['vat'] / st.session_state.tax_data['revenue'] * 100 if st.session_state.tax_data['revenue'] > 0 else 0
            
            fig = go.Figure(go.Indicator(
                mode = "gauge+number", value = burden,
                title = {'text': "增值税税负率 (%)", 'font': {'color': '#94A3B8'}},
                gauge = {'axis': {'range': [0, 10]}, 'bar': {'color': "#EF4444" if burden < 1 else "#10B981"}}
            ))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#E2E8F0', height=250, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            if burden < 1:
                st.error("🚨 警报：税负率异常偏低（低于1%），极易触发税务局大数据扫描！")
            else:
                st.success("✅ 当前税负率处于合理区间。")
                
    with col2:
        with st.container(border=True):
            st.markdown("### 常见风险指标")
            st.markdown("""
            - **进销项品名匹配度**：`[ 95% ]` (正常)
            - **存货周转率波动**：`[ 12% ]` (正常)
            - **预收账款挂账周期**：`[ 180天 ]` (偏高，有隐匿收入嫌疑)
            """)
            st.info("**💡 整改建议**：请核实预收账款科目，确认是否已发货但未及时开票确认收入。")

# ================= 6. 财税知识问答 =================
elif menu == "🧠 财税知识问答":
    st.title("财税 AI 专家")
    st.markdown("<p class='subtitle'>接入政策法规库，随时解答涉税疑惑。</p>", unsafe_allow_html=True)
    
    if "chat" not in st.session_state:
        st.session_state.chat = [{"role": "assistant", "content": "您好！我是AI-Tax专属顾问。关于增值税、企业所得税、税务合规等问题，请随时问我。"}]
        
    for msg in st.session_state.chat:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("输入您的财税问题..."):
        st.session_state.chat.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        with st.spinner("正在查阅法规库与知识图谱..."):
            if "研发" in prompt:
                ans = "根据财政部 税务总局公告2023年第7号，企业开展研发活动中实际发生的研发费用，未形成无形资产计入当期损益的，在按规定据实扣除的基础上，自2023年1月1日起，再按照实际发生额的100%在税前加计扣除。"
            elif "小微" in prompt:
                ans = "小型微利企业需同时满足：1. 从事国家非限制和禁止行业；2. 年度应纳税所得额不超过300万元；3. 从业人数不超过300人；4. 资产总额不超过5000万元。"
            else:
                ans = "这个问题涉及具体业务细节。建议您前往【政策红利雷达】模块查看系统为您自动匹配的政策清单，或咨询主管税务机关。"
            
            st.session_state.chat.append({"role": "assistant", "content": ans})
            st.chat_message("assistant").write(ans)
