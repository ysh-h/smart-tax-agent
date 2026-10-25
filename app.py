import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import uuid
from datetime import date
from dataclasses import dataclass
from typing import Dict, List

# ================= 页面配置与UI美化 =================
st.set_page_config(page_title="智慧财税管理智能体", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* 浅色商务风 */
    .stApp { background-color: #F4F7F9; }
    [data-testid="stSidebar"] { background-color: #1E293B; }
    [data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    [data-testid="stSidebar"] .stRadio label { padding: 10px; border-radius: 6px; transition: 0.2s; }
    [data-testid="stSidebar"] .stRadio label:hover { background-color: #334155; color: #60A5FA !important; }
    
    /* 数据卡片 */
    div[data-testid="metric-container"] {
        background: white; border-radius: 10px; padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-left: 5px solid #3B82F6;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1E293B; font-weight: 800; font-size: 26px; }
    
    /* 标题 */
    h1 { color: #1E293B; font-weight: 800; font-size: 32px; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px;}
    h3 { color: #334155; font-weight: 700; margin-top: 20px;}
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= 核心硬核算法层 (保留你的代码) =================
@dataclass
class EnterpriseProfile:
    name: str = "示例科技有限公司"
    industry: str = "信息技术服务业"
    taxpayer_type: str = "一般纳税人"
    annual_revenue: float = 8000000.0
    total_assets: float = 5000000.0
    employee_count: int = 85
    registered_region: str = "陕西省西安市"
    is_high_tech: bool = True
    rd_ratio: float = 0.06

class TaxStrategy:
    def calc(self, p, d): raise NotImplementedError

class VAT(TaxStrategy):
    def calc(self, p, d):
        if p.taxpayer_type == "一般纳税人":
            out = d["sales"] * 0.13
            inp = d["purchase"] * 0.13
            return {"output": round(out,2), "input": round(inp,2), "payable": round(max(out-inp,0),2), "label":"13%一般计税"}
        return {"payable": round(d["sales"]*0.03,2), "label":"3%简易计税"}

class CIT(TaxStrategy):
    def calc(self, p, d):
        ti = d["taxable_income"]
        if p.is_high_tech:
            rate, label = 0.15, "高新15%"
        elif p.annual_revenue <= 3000000 and p.employee_count <= 300:
            rate, label = 0.05, "小型微利实际5%"
        else:
            rate, label = 0.25, "法定25%"
        return {"ti": ti, "payable": round(ti*rate,2), "label": label}

class Surcharge(TaxStrategy):
    def calc(self, p, d):
        vat = d.get("vat_payable", 0)
        r = 0.12
        return {"base": vat, "payable": round(vat*r,2), "label": f"附加税费{r*100:.0f}%"}

ENGINE = {"增值税": VAT(), "企业所得税": CIT(), "附加税费": Surcharge()}

POLICIES = [
 {"id":"P001","name":"高新技术企业15%税率","tax":"企业所得税","cond":{"is_high_tech":True},"benefit":"税率25%→15%","retention":"高新证书、研发辅助账、知识产权"},
 {"id":"P002","name":"研发费用100%加计扣除","tax":"企业所得税","cond":{"rd_ratio_min":0.03},"benefit":"研发费用加倍扣除","retention":"立项决议、研发辅助账、工时分配表"},
 {"id":"P003","name":"小型微利企业所得税优惠","tax":"企业所得税","cond":{"revenue_max":3000000,"employee_max":300},"benefit":"实际税负5%","retention":"人数/资产/所得额证明"},
 {"id":"P004","name":"小规模纳税人增值税减免","tax":"增值税","cond":{"taxpayer_type":"小规模纳税人"},"benefit":"月销售额10万以下免征","retention":"申报表、销售额台账"},
]

def match(p: EnterpriseProfile):
    enjoyed, available, unmet = [], [], []
    for pol in POLICIES:
        ok = True
        for k, v in pol["cond"].items():
            if k == "rd_ratio_min" and p.rd_ratio < v: ok = False
            elif k == "revenue_max" and p.annual_revenue > v: ok = False
            elif k == "employee_max" and p.employee_count > v: ok = False
            elif k == "taxpayer_type" and p.taxpayer_type != v: ok = False
            elif k == "is_high_tech" and p.is_high_tech != v: ok = False
        if ok:
            (enjoyed if (pol["id"]=="P001" and p.is_high_tech) else available).append(pol)
        else:
            unmet.append(pol)
    return {"已享受":enjoyed, "可享受":available, "暂不满足":unmet}

def risk_scan(p, calc):
    risks = []
    vat = calc.get("增值税", {})
    if vat.get("payable",0)==0 and vat.get("output",0)>0:
        risks.append(("增值税零申报疑点","有销项但应纳税额为0，核查进项抵扣","中"))
    if p.is_high_tech and p.rd_ratio < 0.03:
        risks.append(("研发费用占比预警","高新要求研发占比≥3%，当前偏低","高"))
    return risks

# ================= 状态与数据初始化 =================
if 'filings' not in st.session_state:
    st.session_state.filings = []
if 'calc_results' not in st.session_state:
    st.session_state.calc_results = None
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "您好，我是财税AI助手。请问有什么可以帮您？"}]

# ================= 侧边栏导航 =================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#60A5FA;'>智慧财税智能体</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:12px;'>Design by ysh</p>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("功能导航", [
        "🏢 企业中心", 
        "📁 数据上传与计税", 
        "📄 申报状态查询", 
        "🎯 政策匹配中心", 
        "🛡️ 风险预警看板", 
        "🤖 智能问答", 
        "🔔 消息与提醒"
    ])

# ================= 页面渲染 =================
if menu == "🏢 企业中心":
    st.title("🏢 企业多维画像中心")
    st.markdown("通过结构化数据建立企业动态画像，驱动后续计税与政策匹配。")
    
    with st.container(border=True):
        st.subheader("基础信息录入")
        col1, col2, col3 = st.columns(3)
        name = col1.text_input("企业名称", "ysh 科技有限公司")
        industry = col2.selectbox("所属行业", ["信息技术服务业","制造业","批发零售业","建筑业"])
        ttype = col3.radio("纳税身份", ["一般纳税人", "小规模纳税人"])
        
        col4, col5, col6 = st.columns(3)
        revenue = col4.number_input("年营业收入（元）", value=8000000.0)
        assets = col5.number_input("资产总额（元）", value=5000000.0)
        emp = col6.number_input("从业人数", value=85)
        
        col7, col8, col9 = st.columns(3)
        region = col7.text_input("注册地", "陕西省西安市")
        htech = col8.checkbox("是否高新技术企业", value=True)
        rd = col9.slider("研发费用占营收比", 0.0, 0.2, 0.06)

    # 保存画像到 session
    st.session_state.profile = EnterpriseProfile(name, industry, ttype, revenue, assets, emp, region, htech, rd)

    # 雷达图展示
    st.markdown("### 企业健康度评估")
    fig = go.Figure(go.Scatterpolar(r=[85, 75, 90, 80, 70], theta=['盈利能力','偿债能力','研发创新','税务合规','营运效率'], fill='toself', line_color='#3B82F6'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

elif menu == "📁 数据上传与计税":
    st.title("📁 数据工作台与智能计税")
    st.markdown("模拟上传财务数据，一键执行多税种自动计算并生成底稿。")
    
    with st.container(border=True):
        st.subheader("本期财务数据录入")
        c1, c2, c3 = st.columns(3)
        sales = c1.number_input("本期销售额（元）", value=2000000.0)
        purchase = c2.number_input("本期采购额（元）", value=1200000.0)
        ti = c3.number_input("本期应纳税所得额（元）", value=1500000.0)

    if st.button("⚡ 一键计税并生成申报表", type="primary", use_container_width=True):
        p = st.session_state.get('profile', EnterpriseProfile())
        d = {"sales": sales, "purchase": purchase, "taxable_income": ti}
        calc = {}
        for tax, s in ENGINE.items():
            if tax == "附加税费": d["vat_payable"] = calc["增值税"]["payable"]
            calc[tax] = s.calc(p, d)
            
        st.session_state.calc_results = calc
        
        # 存入申报记录
        for tax, v in calc.items():
            st.session_state.filings.append({
                "id": str(uuid.uuid4())[:8], "tax": tax, "period": date.today().strftime("%Y-%m"),
                "amount": v["payable"], "status": "已生成待提交", "time": date.today().isoformat()
            })
        st.success("计税完成，已生成标准申报底稿！")

    if st.session_state.calc_results:
        st.markdown("### 自动计税结果")
        calc = st.session_state.calc_results
        r1, r2, r3 = st.columns(3)
        r1.metric("增值税", f"¥ {calc['增值税']['payable']:,.2f}", calc['增值税']['label'])
        r2.metric("企业所得税", f"¥ {calc['企业所得税']['payable']:,.2f}", calc['企业所得税']['label'])
        r3.metric("附加税费", f"¥ {calc['附加税费']['payable']:,.2f}", calc['附加税费']['label'])

        st.markdown("### 标准申报底稿")
        tab1, tab2 = st.tabs(["增值税申报表", "企业所得税预缴表"])
        with tab1:
            df_vat = pd.DataFrame({
                "项目": ["销售额", "销项税额", "进项税额", "本期应纳税额"],
                "金额（元）": [f"{sales:,.2f}", f"{calc['增值税'].get('output',0):,.2f}", f"{calc['增值税'].get('input',0):,.2f}", f"{calc['增值税']['payable']:,.2f}"]
            })
            st.dataframe(df_vat, hide_index=True, use_container_width=True)
        with tab2:
            df_cit = pd.DataFrame({
                "项目": ["应纳税所得额", "适用税率", "本期应纳所得税额"],
                "金额/说明": [f"{calc['企业所得税']['ti']:,.2f}", calc['企业所得税']['label'], f"{calc['企业所得税']['payable']:,.2f}"]
            })
            st.dataframe(df_cit, hide_index=True, use_container_width=True)

elif menu == "📄 申报状态查询":
    st.title("📄 申报记录与归档")
    st.markdown("查询系统生成的申报底稿状态，支持批量导出。")
    
    if not st.session_state.filings:
        st.info("暂无申报记录，请前往【数据上传与计税】生成底稿。")
    else:
        df = pd.DataFrame(st.session_state.filings)
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.download_button("📥 导出申报记录 CSV", df.to_csv(index=False).encode('utf-8-sig'), "申报记录.csv")

elif menu == "🎯 政策匹配中心":
    st.title("🎯 税收优惠政策智能适配")
    st.markdown("根据企业画像，自动比对政策条件，输出三级分类结果。")
    
    p = st.session_state.get('profile', EnterpriseProfile())
    pol = match(p)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.success("✅ **已享受政策**")
        for item in pol["已享受"]:
            st.info(f"**{item['name']}**\n\n效益：{item['benefit']}")
    with c2:
        st.info("💡 **可享受政策**")
        for item in pol["可享受"]:
            with st.expander(f"{item['name']}", expanded=True):
                st.write(f"效益：{item['benefit']}")
                st.caption(f"留存备查：{item['retention']}")
    with c3:
        st.warning("⚠️ **暂不满足政策**")
        for item in pol["暂不满足"]:
            st.write(f"❌ {item['name']}")

elif menu == "🛡️ 风险预警看板":
    st.title("🛡️ 涉税风险扫描")
    st.markdown("基于机器算法规则，实时扫描企业财务指标异常。")
    
    p = st.session_state.get('profile', EnterpriseProfile())
    calc = st.session_state.calc_results or {"增值税": {"payable": 0, "output": 0}}
    risks = risk_scan(p, calc)
    
    if not risks:
        st.success("✅ 未发现显著风险信号，企业财税健康度良好。")
    else:
        for r in risks:
            level = "🚨" if r[2] == "高" else "⚠️"
            st.error(f"{level} **[{r[2]}风险] {r[0]}** \n\n 详情：{r[1]}")

elif menu == "🤖 智能问答":
    st.title("🤖 财税智能问答助手")
    st.markdown("基于自然语言处理，解答您的财税政策疑问。")
    
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
        
    if prompt := st.chat_input("例如：高新技术企业有什么优惠？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        q = prompt.lower()
        if "高新" in q or "15%" in q:
            ans = ("高新技术企业减按15%征收企业所得税。条件：拥有核心知识产权、研发费用占比达标、高新收入占比≥60%。留存备查：高新证书、研发辅助账。依据：《企业所得税法》第二十八条。")
        elif "研发" in q and "加计" in q:
            ans = ("研发费用未形成无形资产的按100%加计扣除，形成无形资产的按200%摊销。需建立研发辅助账，留存立项决议与工时分配表。")
        elif "小规模" in q:
            ans = "小规模纳税人适用3%征收率，月销售额10万元以下免征增值税。"
        else:
            ans = "请提供更具体的问题，例如“高新企业所得税税率”“研发费用加计扣除条件”。"
            
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.chat_message("assistant").write(ans)

elif menu == "🔔 消息与提醒":
    st.title("🔔 站内消息与合规提醒")
    st.markdown("及时获取申报期限与政策更新通知。")
    
    st.info("📢 **政策更新**：政策库最近更新于 2026-10-20（研发费用加计扣除比例延续）。")
    st.warning("⏰ **申报提醒**：增值税申报期限为次月15日前；企业所得税季度预缴期限为季度终了后15日内。")
    st.error("🚨 **资质提醒**：高新技术企业证书到期前90天需启动重新认定，请注意时间节点。")