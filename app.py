import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
from typing import Dict, List

# ================= 页面配置与UI美化 =================
st.set_page_config(page_title="AI-Tax 智慧财税中台", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* 商务浅色背景 */
    .stApp { background-color: #F4F7F9; }
    /* 深色侧边栏 */
    [data-testid="stSidebar"] { background-color: #1E293B; }
    [data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    /* 指标卡片 */
    div[data-testid="metric-container"] {
        background: white; border-radius: 10px; padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 4px solid #3B82F6;
    }
    /* 隐藏默认元素 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    /* 标题 */
    h1 { color: #1E293B; font-weight: 800; font-size: 32px; }
    h3 { color: #334155; font-weight: 700; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ================= 核心硬核算法层 (保留你的原版逻辑) =================
@dataclass
class EnterpriseProfile:
    name: str
    industry: str
    taxpayer_type: str
    annual_revenue: float
    total_assets: float
    employee_count: int
    registered_region: str
    is_high_tech: bool
    rd_expense_ratio: float

class TaxStrategy:
    def calc(self, profile, data): raise NotImplementedError

class VATStrategy(TaxStrategy):
    def calc(self, profile, data):
        if profile.taxpayer_type == "一般纳税人":
            output_tax = data["sales_amount"] * data.get("vat_rate", 0.13)
            input_tax = data["purchase_amount"] * data.get("input_vat_rate", 0.13)
            payable = max(output_tax - input_tax, 0)
            return {"output_tax": round(output_tax, 2), "input_tax": round(input_tax, 2), "payable": round(payable, 2), "rate": "13%（一般计税）"}
        else:
            payable = data["sales_amount"] * 0.03
            return {"output_tax": round(data["sales_amount"] * 0.03, 2), "input_tax": 0, "payable": round(payable, 2), "rate": "3%（简易计税）"}

class CITStrategy(TaxStrategy):
    def calc(self, profile, data):
        taxable_income = data.get("taxable_income", 0)
        if profile.is_high_tech:
            rate, label = 0.15, "高新技术企业15%"
        elif profile.annual_revenue <= 3_000_000 and profile.employee_count <= 300:
            rate, label = 0.05, "小型微利企业实际5%"
        else:
            rate, label = 0.25, "法定税率25%"
        return {"taxable_income": taxable_income, "rate": label, "payable": round(taxable_income * rate, 2)}

class SurchargeStrategy(TaxStrategy):
    def calc(self, profile, data):
        vat_payable = data.get("vat_payable", 0)
        total_rate = 0.12 if profile.registered_region.startswith("市") else 0.10
        return {"base": vat_payable, "rate": f"{total_rate*100:.0f}%", "payable": round(vat_payable * total_rate, 2)}

TAX_ENGINE = {"增值税": VATStrategy(), "企业所得税": CITStrategy(), "附加税费": SurchargeStrategy()}

POLICY_LIBRARY = [
    {"id":"P001","name":"高新技术企业减按15%征收企业所得税","tax":"企业所得税","conditions":{"is_high_tech":True},"benefit":"税率由25%降至15%","retention":"高新证书、研发辅助账"},
    {"id":"P002","name":"研发费用加计扣除（100%）","tax":"企业所得税","conditions":{"rd_expense_ratio":0.03},"benefit":"研发费用在税前加倍扣除","retention":"立项决议、辅助账、工时表"},
    {"id":"P003","name":"小型微利企业所得税优惠","tax":"企业所得税","conditions":{"annual_revenue":3_000_000,"employee_count":300},"benefit":"实际税负5%","retention":"从业人数、资产总额证明"},
    {"id":"P004","name":"增值税小规模纳税人减免","tax":"增值税","conditions":{"taxpayer_type":"小规模纳税人"},"benefit":"月销售额10万以下免征","retention":"申报表、台账"},
]

def match_policies(profile):
    matched, unmet = [], []
    for p in POLICY_LIBRARY:
        conds = p["conditions"]
        ok = all(getattr(profile, k) == v if not isinstance(v, (int,float)) else getattr(profile, k) >= v for k, v in conds.items())
        entry = {**p, "status": "可享受" if ok else "暂不满足"}
        if ok: matched.append(entry)
        else: unmet.append(entry)
    enjoyed = [p for p in matched if p["id"]=="P001" and profile.is_high_tech]
    return {"已享受": enjoyed, "可享受": [p for p in matched if p not in enjoyed], "暂不满足": unmet}

def analyze_risks(profile, calc_results):
    risks = []
    vat, cit = calc_results.get("增值税", {}), calc_results.get("企业所得税", {})
    if vat.get("payable", 0) == 0 and vat.get("output_tax",0) > 0:
        risks.append(("增值税零申报疑点", "存在销项但应纳税额为0，需核实进项抵扣合规性", "中"))
    if profile.rd_expense_ratio < 0.03 and profile.is_high_tech:
        risks.append(("研发费用占比预警", "高新资质要求研发费用占比不低于3%，当前偏低", "高"))
    if cit.get("rate","").startswith("小型微利") and profile.annual_revenue > 3_000_000:
        risks.append(("优惠适用条件超限", "营收超过小型微利标准，优惠可能不适用", "高"))
    return risks

# ================= 侧边栏：企业画像与数据输入 =================
with st.sidebar:
    st.markdown("## 🏢 企业画像录入")
    name = st.text_input("企业名称", "ysh 科技有限公司")
    industry = st.selectbox("所属行业", ["信息技术服务业", "制造业", "批发零售业", "建筑业"])
    taxpayer = st.radio("纳税身份", ["一般纳税人", "小规模纳税人"])
    revenue = st.number_input("年营业收入（元）", value=8000000.0)
    assets = st.number_input("资产总额（元）", value=5000000.0)
    employees = st.number_input("从业人数", value=85)
    region = st.text_input("注册地", "陕西省西安市")
    is_ht = st.checkbox("是否高新技术企业", value=True)
    rd_ratio = st.slider("研发费用占营收比", 0.0, 0.2, 0.06)
    
    st.markdown("---")
    st.markdown("## 💰 本期财务数据")
    sales = st.number_input("销售额（元）", value=2000000.0)
    purchase = st.number_input("采购额（元）", value=1200000.0)
    taxable_inc = st.number_input("应纳税所得额（元）", value=1500000.0)
    
    btn_run = st.button("⚡ 一键计税与政策匹配", type="primary", use_container_width=True)

# ================= 主界面逻辑 =================
st.title("AI-Tax 智慧财税中台")
st.markdown("多税种一键申报 · 自动计税 · 政策智能匹配 · 涉税风险分析")

if btn_run or True: # 默认直接运行展示
    profile = EnterpriseProfile(name, industry, taxpayer, revenue, assets, employees, region, is_ht, rd_ratio)
    data = {"sales_amount": sales, "purchase_amount": purchase, "taxable_income": taxable_inc, "vat_rate": 0.13, "input_vat_rate": 0.13}
    
    # 运行核心算法
    calc = {}
    for t_name, strategy in TAX_ENGINE.items():
        if t_name == "附加税费":
            data["vat_payable"] = calc.get("增值税", {}).get("payable", 0)
        calc[t_name] = strategy.calc(profile, data)
        
    policies = match_policies(profile)
    risks = analyze_risks(profile, calc)

    # --- 顶部指标卡片 ---
    st.markdown("### 📊 自动计税结果总览")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("应缴增值税", f"¥ {calc['增值税']['payable']:,.2f}", calc['增值税']['rate'])
    col2.metric("应缴企业所得税", f"¥ {calc['企业所得税']['payable']:,.2f}", calc['企业所得税']['rate'])
    col3.metric("应缴附加税费", f"¥ {calc['附加税费']['payable']:,.2f}", f"费率 {calc['附加税费']['rate']}")
    
    total_tax = calc['增值税']['payable'] + calc['企业所得税']['payable'] + calc['附加税费']['payable']
    col4.metric("企业总税负", f"¥ {total_tax:,.2f}")

    # --- 核心功能区 Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(["📄 申报表生成", "🎯 政策适配分析", "🛡️ 涉税风险扫描", "📈 数据可视化"])
    
    with tab1:
        st.subheader("增值税申报表（一般计税）")
        df_vat = pd.DataFrame({
            "项目": ["销售额", "销项税额", "进项税额", "应纳税额"],
            "金额（元）": [f"{sales:,.2f}", f"{calc['增值税'].get('output_tax',0):,.2f}", f"{calc['增值税'].get('input_tax',0):,.2f}", f"{calc['增值税']['payable']:,.2f}"]
        })
        st.dataframe(df_vat, hide_index=True, use_container_width=True)
        
        st.subheader("企业所得税季度预缴表（A类）")
        df_cit = pd.DataFrame({
            "项目": ["应纳税所得额", "适用税率", "应纳所得税额"],
            "内容": [f"{calc['企业所得税']['taxable_income']:,.2f}", calc['企业所得税']['rate'], f"{calc['企业所得税']['payable']:,.2f}"]
        })
        st.dataframe(df_cit, hide_index=True, use_container_width=True)

    with tab2:
        st.subheader("🎯 税收优惠政策智能匹配")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.success("✅ **已享受政策**")
            for p in policies["已享受"]:
                st.info(f"**{p['name']}**\n\n{p['benefit']}")
        with c2:
            st.info("💡 **可享受政策**")
            for p in policies["可享受"]:
                with st.expander(f"{p['name']}", expanded=True):
                    st.write(f"优惠: {p['benefit']}")
                    st.caption(f"留存备查: {p['retention']}")
        with c3:
            st.warning("⚠️ **暂不满足政策**")
            for p in policies["暂不满足"]:
                st.write(f"❌ {p['name']}")

    with tab3:
        st.subheader("🛡️ 智能涉税风险扫描")
        if not risks:
            st.success("✅ 未发现显著风险信号，企业财税健康度良好。")
        else:
            for r in risks:
                level = "🚨" if r[2] == "高" else "⚠️"
                st.error(f"{level} **[{r[2]}风险] {r[0]}** \n\n 详情：{r[1]}")

    with tab4:
        st.subheader("📈 企业税负结构分析")
        fig = px.pie(
            values=[calc['增值税']['payable'], calc['企业所得税']['payable'], calc['附加税费']['payable']],
            names=['增值税', '企业所得税', '附加税费'],
            hole=0.4,
            color_discrete_sequence=['#3B82F6', '#10B981', '#F59E0B']
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.info("⏰ **合规提醒**：政策库更新于 2026-10-20；增值税申报期限为次月15日前；高新技术企业证书到期前90天需启动重新认定。")
