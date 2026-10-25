import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
from typing import Dict, List

# ================= 页面配置与高级CSS =================
st.set_page_config(page_title="企业级智慧财税中台", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* 整体背景 */
    .stApp { background-color: #F4F7F9; font-family: 'PingFang SC', sans-serif; }
    /* 深色侧边栏 */
    [data-testid="stSidebar"] { background: #0F172A; box-shadow: 2px 0 10px rgba(0,0,0,0.1); }
    [data-testid="stSidebar"] * { color: #94A3B8 !important; }
    [data-testid="stSidebar"] .stRadio label { font-size: 15px; padding: 12px; border-radius: 8px; transition: all 0.3s; }
    [data-testid="stSidebar"] .stRadio label:hover { background-color: #1E293B; color: #38BDF8 !important; }
    
    /* 白色数据卡片 */
    div[data-testid="metric-container"] {
        background: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-top: 4px solid #3B82F6;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1E293B; font-weight: 800; }
    
    /* 标题与容器 */
    h1 { color: #0F172A; font-weight: 800; font-size: 32px; letter-spacing: -1px; }
    h2 { color: #334155; font-weight: 700; }
    h3 { color: #1E293B; font-weight: 600; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    /* 隐藏默认 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= 硬核底层：策略模式算法层 =================
@dataclass
class EnterpriseProfile:
    name: str = "ysh 科技有限公司"
    industry: str = "信息技术服务业"
    taxpayer_type: str = "一般纳税人"
    annual_revenue: float = 8000000.0
    total_assets: float = 5000000.0
    employee_count: int = 85
    region: str = "陕西省西安市"
    is_high_tech: bool = True
    rd_ratio: float = 0.06

class TaxStrategy:
    def calc(self, p, d): raise NotImplementedError

class VAT(TaxStrategy):
    def calc(self, p, d):
        if p.taxpayer_type == "一般纳税人":
            out = d["sales"] * 0.13
            inp = d["purchase"] * 0.13
            return {"output": out, "input": inp, "payable": max(out-inp, 0), "label": "13%一般计税"}
        return {"output": d["sales"]*0.03, "input": 0, "payable": d["sales"]*0.03, "label": "3%简易计税"}

class CIT(TaxStrategy):
    def calc(self, p, d):
        ti = d["taxable_income"]
        if p.is_high_tech:
            rate, label = 0.15, "高新技术企业(15%)"
        elif p.annual_revenue <= 3000000 and p.employee_count <= 300:
            rate, label = 0.05, "小型微利企业(5%)"
        else:
            rate, label = 0.25, "法定税率(25%)"
        return {"ti": ti, "payable": ti*rate, "label": label}

class Surcharge(TaxStrategy):
    def calc(self, p, d):
        vat = d.get("vat_payable", 0)
        r = 0.12
        return {"base": vat, "payable": vat*r, "label": f"附加税费({r*100:.0f}%)"}

ENGINE = {"增值税": VAT(), "企业所得税": CIT(), "附加税费": Surcharge()}

# ================= 全局状态存储 =================
if 'profile' not in st.session_state: st.session_state.profile = EnterpriseProfile()
if 'calc_results' not in st.session_state: st.session_state.calc_results = None
if 'filings' not in st.session_state: st.session_state.filings = []
if 'chat_history' not in st.session_state: st.session_state.chat_history = [{"role": "assistant", "content": "您好！我是智慧财税中台AI助手，请问有什么可以帮您？"}]

# ================= 侧边栏导航 =================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#38BDF8; margin-bottom:0;'>⚡ 智慧财税中台</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:12px; color:#64748B;'>Enterprise Tax Brain</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1E293B;'>", unsafe_allow_html=True)
    
    menu = st.radio("主导航", [
        "🏢 企业画像中心", 
        "⚙️ 数据工作台与计税", 
        "📄 申报状态流转", 
        "🎯 政策图谱匹配", 
        "🛡️ 风险预警雷达", 
        "💬 智能财税顾问"
    ])
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.caption("当前登录：ysh (财务主管)")

# ================= 1. 企业画像中心 =================
if menu == "🏢 企业画像中心":
    st.title("企业多维数字画像")
    st.markdown("构建真实企业特征，为计税与政策匹配提供底层数据支撑。")
    
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        p = st.session_state.profile
        p.name = c1.text_input("企业名称", p.name)
        p.industry = c2.selectbox("所属行业", ["信息技术服务业", "制造业", "批发零售业"], index=0)
        p.taxpayer_type = c3.radio("纳税人身份", ["一般纳税人", "小规模纳税人"])
        
        c4, c5, c6 = st.columns(3)
        p.annual_revenue = c4.number_input("年营业收入 (元)", value=p.annual_revenue, step=10000.0)
        p.total_assets = c5.number_input("资产总额 (元)", value=p.total_assets, step=10000.0)
        p.employee_count = c6.number_input("从业人数 (人)", value=p.employee_count)
        
        c7, c8, c9 = st.columns(3)
        p.region = c7.text_input("注册地", p.region)
        p.is_high_tech = c8.checkbox("是否高新技术企业", value=p.is_high_tech)
        p.rd_ratio = c9.slider("研发费用占营收比", 0.0, 0.2, p.rd_ratio, step=0.01)
        
        if st.button("保存企业画像", type="primary", use_container_width=True):
            st.session_state.profile = p
            st.success("企业画像已更新，全局数据联动生效！")

    st.markdown("### 企业财税健康度评估")
    col_chart, col_text = st.columns([1.5, 1])
    with col_chart:
        fig = go.Figure(go.Scatterpolar(
            r=[85, 70, 90, 80, 60], theta=['盈利能力', '偿债能力', '研发创新', '税务合规', '现金流'],
            fill='toself', line_color='#3B82F6', fillcolor='rgba(59, 130, 246, 0.2)'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    with col_text:
        st.info(f"""
        **智能诊断结论：**
        
        该企业属于 **{p.industry}**，当前研发投入占比为 **{p.rd_ratio*100:.1f}%**。
        结合其 **{p.taxpayer_type}** 身份与高新技术资质，系统预测其本年度可享受显著的研发加计扣除与所得税减免红利。
        """)

# ================= 2. 数据工作台与计税 =================
elif menu == "⚙️ 数据工作台与计税":
    st.title("业务数据台与智能计税引擎")
    st.markdown("导入本期财务数据，系统将自动执行策略模式计税引擎，并生成标准申报底稿。")
    
    with st.container(border=True):
        st.subheader("本期财务数据")
        c1, c2, c3 = st.columns(3)
        sales = c1.number_input("本期销项销售额 (元)", value=2000000.0, step=10000.0)
        purchase = c2.number_input("本期进项采购额 (元)", value=1200000.0, step=10000.0)
        ti = c3.number_input("本期利润总额/应纳税所得额", value=1500000.0, step=10000.0)
    
    if st.button("⚡ 运行计税引擎与生成申报底稿", type="primary", use_container_width=True):
        p = st.session_state.profile
        d = {"sales": sales, "purchase": purchase, "taxable_income": ti}
        calc = {}
        for tax, strategy in ENGINE.items():
            if tax == "附加税费": d["vat_payable"] = calc["增值税"]["payable"]
            calc[tax] = strategy.calc(p, d)
        
        st.session_state.calc_results = calc
        # 模拟写入申报流水
        st.session_state.filings.append({
            "申报期": "2026-10", "税种": "增值税", "应纳税额": calc["增值税"]["payable"], "状态": "已生成待申报"
        })
        st.session_state.filings.append({
            "申报期": "2026-10", "税种": "企业所得税", "应纳税额": calc["企业所得税"]["payable"], "状态": "已生成待申报"
        })
        st.success("✅ 计税完成！全税种底稿已生成。")

    if st.session_state.calc_results:
        calc = st.session_state.calc_results
        st.markdown("### 本期核心税负卡片")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("应缴增值税", f"¥ {calc['增值税']['payable']:,.2f}", calc['增值税']['label'])
        r2.metric("应缴企业所得税", f"¥ {calc['企业所得税']['payable']:,.2f}", calc['企业所得税']['label'])
        r3.metric("应缴附加税费", f"¥ {calc['附加税费']['payable']:,.2f}", calc['附加税费']['label'])
        total = calc['增值税']['payable'] + calc['企业所得税']['payable'] + calc['附加税费']['payable']
        r4.metric("本期合计税负", f"¥ {total:,.2f}", "需申报缴纳", delta_color="inverse")

        st.markdown("### 标准申报底稿（符合税务规范）")
        tab1, tab2 = st.tabs(["📄 增值税主表", "📄 企业所得税A类预缴表"])
        with tab1:
            st.dataframe(pd.DataFrame({
                "行次": [1, 11, 12, 20],
                "项目": ["按适用税率计税销售额", "销项税额", "进项税额", "应纳税额合计"],
                "金额（元）": [f"{sales:,.2f}", f"{calc['增值税']['output']:,.2f}", f"{calc['增值税']['input']:,.2f}", f"{calc['增值税']['payable']:,.2f}"]
            }), hide_index=True, use_container_width=True)
        with tab2:
            st.dataframe(pd.DataFrame({
                "行次": [1, 3, 20],
                "项目": ["实际利润额/应纳税所得额", "适用税率", "应纳所得税额"],
                "金额/说明": [f"{calc['企业所得税']['ti']:,.2f}", calc['企业所得税']['label'], f"{calc['企业所得税']['payable']:,.2f}"]
            }), hide_index=True, use_container_width=True)

# ================= 3. 申报状态流转 =================
elif menu == "📄 申报状态流转":
    st.title("涉税申报状态与归档")
    st.markdown("一键确认申报，实现从底稿生成到完成申报的状态流转。")
    
    if not st.session_state.filings:
        st.info("暂无待申报记录，请先前往【数据工作台】生成底稿。")
    else:
        df = pd.DataFrame(st.session_state.filings)
        st.dataframe(df, hide_index=True, use_container_width=True)
        
        if st.button("🚀 一键批量确认申报 (模拟与税局接口对接)", type="primary"):
            for f in st.session_state.filings:
                f["状态"] = "✅ 已申报归档"
            st.success("申报成功！回执已生成，数据已归档。")
            st.rerun()

# ================= 4. 政策图谱匹配 =================
elif menu == "🎯 政策图谱匹配":
    st.title("税收红利政策图谱匹配")
    st.markdown("基于知识图谱判定条件，精准锁定企业可享受的税收优惠。")
    
    p = st.session_state.profile
    st.markdown("### 1. 小型微利企业资质判定模型")
    with st.container(border=True):
        cond_df = pd.DataFrame([
            {"判定指标": "年应纳税所得额", "限额": "≤ 300万元", "企业当前": f"{st.session_state.calc_results['企业所得税']['ti'] if st.session_state.calc_results else 0:,.2f}元", "判定结果": "符合" if (st.session_state.calc_results and st.session_state.calc_results['企业所得税']['ti'] <= 3000000) else "不符合"},
            {"判定指标": "从业人数", "限额": "≤ 300人", "企业当前": f"{p.employee_count}人", "判定结果": "符合" if p.employee_count <= 300 else "不符合"},
            {"判定指标": "资产总额", "限额": "≤ 5000万元", "企业当前": f"{p.total_assets/10000:,.2f}万元", "判定结果": "符合" if p.total_assets <= 50000000 else "不符合"},
            {"判定指标": "限制/禁止行业", "限额": "否", "企业当前": "否", "判定结果": "符合"}
        ])
        st.dataframe(cond_df, hide_index=True, use_container_width=True)
        
    st.markdown("### 2. 政策图谱适配结果")
    c1, c2 = st.columns(2)
    with c1:
        st.success("✅ **已享受/法定适用政策**")
        st.info("**高新技术企业所得税优惠**\n\n税率从25%降至15%，减免效果显著。\n备查资料：高新证书、研发费用台账。")
    with c2:
        st.warning("💡 **可主动申请政策**")
        st.markdown("""
        **研发费用100%加计扣除**
        - **适用条件**：研发费用占营收比≥3%（当前为 {:.1f}%）。
        - **节税测算**：预计可额外抵扣利润额约 **{:,.2f} 元**。
        - **留存备查**：研发立项书、工时分配表。
        """.format(p.rd_ratio*100, p.annual_revenue * p.rd_ratio))

# ================= 5. 风险预警雷达 =================
elif menu == "🛡️ 风险预警雷达":
    st.title("涉税风险智能雷达")
    st.markdown("基于行业均值与税法红线，对财务指标进行主动风险扫描。")
    
    p = st.session_state.profile
    risks = []
    if st.session_state.calc_results:
        vat = st.session_state.calc_results['增值税']['payable']
        burden = (vat / 2000000.0) * 100 # 假设销售额为200万
        if burden < 1.5:
            risks.append(("增值税税负率极低预警", f"当前税负率约 {burden:.2f}%，远低于信息服务业均值。极易引发税务局大数据风控扫描。建议核查是否存在未开票收入。", "高"))
        if p.is_high_tech and p.rd_ratio < 0.03:
            risks.append(("高新资质维持风险", "研发费用占比低于3%，可能面临高新资质被取消及追缴税款风险。", "高"))
            
    if not risks:
        st.success("✅ 当前未发现显著涉税风险。")
    else:
        for r in risks:
            st.error(f"🚨 **【{r[2]}风险】{r[0]}**\n\n**诊断详情**：{r[1]}")

# ================= 6. 智能财税顾问 =================
elif menu == "💬 智能财税顾问":
    st.title("财税 AI 智能顾问")
    st.markdown("基于大模型微调的财税知识库问答系统。")
    
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("例如：小微企业的判定标准是什么？"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        q = prompt.lower()
        if "小微" in q:
            ans = "小型微利企业需同时满足：1. 从事国家非限制和禁止行业；2. 年度应纳税所得额不超过300万元；3. 从业人数不超过300人；4. 资产总额不超过5000万元。"
        elif "研发" in q:
            ans = "企业开展研发活动中实际发生的研发费用，未形成无形资产计入当期损益的，自2023年1月1日起，再按照实际发生额的100%在税前加计扣除。"
        else:
            ans = "该问题涉及具体业务场景，建议前往【政策图谱匹配】模块查看企业当前资质，或咨询主管税务机关。"
            
        st.session_state.chat_history.append({"role": "assistant", "content": ans})
        st.chat_message("assistant").write(ans)
