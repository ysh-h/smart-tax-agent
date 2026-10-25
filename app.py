import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
from dataclasses import dataclass
from typing import Dict, List

# ================= 页面配置 =================
st.set_page_config(page_title="智慧财税决策中台 - 企业版", layout="wide", initial_sidebar_state="expanded")

# ================= 高定商业 UI 引擎 =================
st.markdown("""
<style>
    /* 全局背景与字体 */
    .stApp { background: #F0F4F8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
    
    /* 顶级深色控制台侧边栏 */
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
        box-shadow: 4px 0 24px rgba(0,0,0,0.1);
        border-right: none;
    }
    [data-testid="stSidebar"] * { color: #94A3B8 !important; }
    [data-testid="stSidebar"] .stRadio label { 
        font-size: 15px; padding: 12px 16px; border-radius: 8px; margin-bottom: 4px; transition: all 0.2s; 
    }
    [data-testid="stSidebar"] .stRadio label:hover { background: rgba(56, 189, 248, 0.1); color: #38BDF8 !important; }
    
    /* 玻璃拟态指标卡片 */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px);
        border-radius: 16px; padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.01);
        border: 1px solid #E2E8F0;
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
    div[data-testid="metric-container"] label { color: #64748B !important; font-size: 14px; font-weight: 600; letter-spacing: 0.5px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #0F172A; font-weight: 800; font-size: 32px; margin-top: 8px; }
    
    /* 高级卡片容器 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white; border-radius: 16px; border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); padding: 24px;
    }
    
    /* 排版 */
    h1 { color: #0F172A; font-weight: 800; font-size: 36px; letter-spacing: -1px; margin-bottom: 8px; }
    p.subtitle { color: #64748B; font-size: 16px; margin-bottom: 32px; font-weight: 400; }
    h2 { color: #1E293B; font-weight: 700; font-size: 24px; margin-top: 32px; margin-bottom: 16px;}
    
    /* 表格样式 */
    .stDataFrame { background: white; border-radius: 12px; overflow: hidden; border: 1px solid #E2E8F0; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= 核心算法层 (策略模式 & 税会差异) =================
@dataclass
class CompanyData:
    name: str = "星耀科技（中国）有限公司"
    industry: str = "软件和信息技术服务业"
    revenue: float = 85000000.0      # 营收 8500万
    cost: float = 45000000.0         # 成本
    expense: float = 18000000.0      # 费用
    entertainment: float = 500000.0  # 业务招待费
    rd_expense: float = 6500000.0    # 研发费用
    input_vat: float = 2800000.0     # 进项税额
    employees: int = 240

def calc_taxes(d: CompanyData):
    # 1. 增值税
    vat_payable = max(d.revenue * 0.06 - d.input_vat, 0) # 软件业按6%计算
    surcharge = vat_payable * 0.12
    
    # 2. 税会差异调整
    # 业务招待费：按发生额60%扣除，但最高不得超过当年销售(营业)收入的5‰
    ent_deduction = min(d.entertainment * 0.6, d.revenue * 0.005)
    ent_adjust = d.entertainment - ent_deduction
    
    # 研发费用加计扣除：100%加计
    rd_deduction = d.rd_expense * 1.0
    
    # 会计利润
    accounting_profit = d.revenue - d.cost - d.expense
    # 应纳税所得额 = 利润 + 招待费调增 - 研发费调减
    taxable_income = max(0, accounting_profit + ent_adjust - rd_deduction)
    
    # 3. 企业所得税 (小型微利判定)
    is_micro = taxable_income <= 3000000 and d.employees <= 300
    cit_rate = 0.05 if is_micro else 0.25
    cit_payable = taxable_income * cit_rate
    
    return {
        "vat": vat_payable,
        "surcharge": surcharge,
        "profit": accounting_profit,
        "taxable_income": taxable_income,
        "cit": cit_payable,
        "is_micro": is_micro,
        "total_tax": vat_payable + surcharge + cit_payable,
        "ent_adjust": ent_adjust,
        "rd_deduction": rd_deduction
    }

# ================= 全局状态 =================
if 'company' not in st.session_state: st.session_state.company = CompanyData()
if 'tax_res' not in st.session_state: st.session_state.tax_res = calc_taxes(st.session_state.company)
if 'declare_status' not in st.session_state: st.session_state.declare_status = "待申报"

# ================= 侧边栏 =================
with st.sidebar:
    st.markdown("<div style='padding: 20px 0;'><h2 style='text-align:center; color:#F8FAFC; margin:0;'>⚡ 智慧财税中台</h2><p style='text-align:center; font-size:12px; color:#64748B;'>Enterprise Finance & Tax OS</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("业务模块导航", [
        "📊 智能决策驾驶舱", 
        "📂 业财数据控制台", 
        "🧮 多税种申报与测算", 
        "🛡️ 涉税风控体检", 
        "🎯 政策红利与画像", 
        "🤖 财税大模型助手"
    ])
    st.markdown("---")
    st.markdown(f"""
    <div style='background: #1E293B; padding: 15px; border-radius: 10px; border: 1px solid #334155;'>
        <p style='font-size: 12px; color: #94A3B8; margin: 0 0 8px 0;'>当前申报状态</p>
        <p style='font-size: 16px; color: #38BDF8; font-weight: bold; margin: 0;'>● {st.session_state.declare_status}</p>
    </div>
    """, unsafe_allow_html=True)

# 获取当前数据
d = st.session_state.company
res = st.session_state.tax_res

# ================= 1. 智能决策驾驶舱 =================
if menu == "📊 智能决策驾驶舱":
    st.title("企业财税智能决策驾驶舱")
    st.markdown("<p class='subtitle'>全局掌控企业经营状态、实时监控税负健康度与合规风险。</p>", unsafe_allow_html=True)
    
    # 顶部指标卡
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("年度营业总收入", f"¥ {d.revenue:,.0f}", "同比增长 24.5%")
    c2.metric("本期综合税负", f"¥ {res['total_tax']:,.0f}", f"综合税负率 {res['total_tax']/d.revenue*100:.2f}%", delta_color="inverse")
    c3.metric("预计利润总额", f"¥ {res['profit']:,.0f}", "利润率良好")
    c4.metric("政策红利释放", f"¥ {res['rd_deduction']*0.25 + (res['profit'] if res['is_micro'] else 0):,.0f}", "合规降本增效")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 图表区
    col_left, col_right = st.columns([2, 1])
    with col_left:
        with st.container(border=True):
            st.markdown("### 📈 企业营收与利润趋势分析")
            months = ['1月', '2月', '3月', '4月', '5月', '6月']
            revenue_trend = [1200, 1350, 1100, 1600, 1850, 1700]
            profit_trend = [240, 310, 200, 420, 510, 450]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(x=months, y=revenue_trend, name="营收 (万元)", marker_color='#3B82F6'))
            fig.add_trace(go.Scatter(x=months, y=profit_trend, name="利润 (万元)", yaxis='y2', line=dict(color='#10B981', width=3)))
            fig.update_layout(
                yaxis=dict(title='营收', showgrid=False),
                yaxis2=dict(title='利润', overlaying='y', side='right', showgrid=False),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=350, margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
            
    with col_right:
        with st.container(border=True):
            st.markdown("### 🛡️ 财税合规健康分")
            fig = go.Figure(go.Indicator(
                mode="gauge+number", value=92, 
                number={'suffix': " 分", 'font': {'color': '#10B981'}},
                gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#10B981"}, 'bgcolor': "#F1F5F9"}
            ))
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
            st.success("✅ 企业财税指标健康，未触发税务稽查红线。")

# ================= 2. 业财数据控制台 =================
elif menu == "📂 业财数据控制台":
    st.title("业财数据控制台")
    st.markdown("<p class='subtitle'>对接底层业务系统，实现账务数据、发票池、资金流水的一体化采集与治理。</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### 核心财务指标调整")
        c1, c2, c3 = st.columns(3)
        d.revenue = c1.number_input("营业收入 (元)", value=d.revenue, step=100000.0)
        d.cost = c2.number_input("营业成本 (元)", value=d.cost, step=100000.0)
        d.expense = c3.number_input("期间费用 (元)", value=d.expense, step=100000.0)
        
        c4, c5, c6 = st.columns(3)
        d.rd_expense = c4.number_input("研发费用总额 (元)", value=d.rd_expense, step=10000.0)
        d.entertainment = c5.number_input("业务招待费 (元)", value=d.entertainment, step=10000.0)
        d.input_vat = c6.number_input("本期进项税额 (元)", value=d.input_vat, step=10000.0)
        
        if st.button("🔄 保存数据并重算全盘财税指标", type="primary", use_container_width=True):
            st.session_state.company = d
            st.session_state.tax_res = calc_taxes(d)
            st.success("数据已更新，全局报表已重算！")
            st.rerun()

    st.markdown("### 进销项发票勾稽匹配池 (OCR智能提取)")
    invoice_data = pd.DataFrame({
        "发票类型": ["增值税专用发票", "增值税专用发票", "电子普通发票"],
        "发票代码": ["011002400111", "011002400112", "011002400113"],
        "销方/购方": ["华为技术有限公司", "星耀科技（中国）", "阿里云计算有限公司"],
        "金额(元)": [1200000.0, 3500000.0, 250000.0],
        "税额(元)": [156000.0, 455000.0, 15000.0],
        "校验状态": ["✅ 已认证抵扣", "✅ 已开具", "⚠️ 待查验"]
    })
    st.dataframe(invoice_data, hide_index=True, use_container_width=True)

# ================= 3. 多税种申报与测算 =================
elif menu == "🧮 多税种申报与测算":
    st.title("智能算税与多税种申报")
    st.markdown("<p class='subtitle'>严格遵循税法规定，自动执行税会差异调整，生成标准申报底稿。</p>", unsafe_allow_html=True)
    
    # 顶部卡片
    c1, c2, c3 = st.columns(3)
    c1.metric("本期应缴增值税", f"¥ {res['vat']:,.2f}", "按6%现代服务业计")
    c2.metric("本期应缴附加税", f"¥ {res['surcharge']:,.2f}", "按增值税12%计")
    c3.metric("本期应缴所得税", f"¥ {res['cit']:,.2f}", "小微优享5%" if res['is_micro'] else "高新/法定适用")

    with st.container(border=True):
        st.markdown("### 📑 企业所得税税会差异调整底稿（核心专业资产）")
        st.markdown(f"""
        1. **会计利润**：营收({d.revenue:,.2f}) - 成本({d.cost:,.2f}) - 费用({d.expense:,.2f}) = **{res['profit']:,.2f} 元**
        2. **纳税调增项**：业务招待费超限调增 = **{res['ent_adjust']:,.2f} 元** *(发生额的60%与营收5‰孰低)*
        3. **纳税调减项**：研发费用加计扣除 = **{res['rd_deduction']:,.2f} 元**
        4. **最终应纳税所得额** = 利润 + 调增 - 调减 = **{res['taxable_income']:,.2f} 元**
        """)
        
        st.markdown(f"**最终适用税率**：`{ '5% (小型微利企业)' if res['is_micro'] else '25% (法定)' }`")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🚀 一键执行纳税申报及扣款", type="primary", use_container_width=True):
            st.session_state.declare_status = "✅ 已申报 (本期)"
            st.success("申报成功！已向电子税务局推送数据。")
    with col2:
        st.download_button("📥 导出全套标准申报表 (ZIP)", data=b"dummy_zip_data", file_name="申报归档.zip", use_container_width=True)

# ================= 4. 涉税风控体检 =================
elif menu == "🛡️ 涉税风控体检":
    st.title("涉税风险智能扫描")
    st.markdown("<p class='subtitle'>通过机器学习与规则引擎，实时监控发票流、资金流与税负率，防患于未然。</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 2])
    with c1:
        with st.container(border=True):
            st.markdown("### 综合健康指数")
            st.metric("风控评分", "85 分", "存在1项中风险", delta_color="inverse")
            st.info("**建议**：本月进项发票集中度偏高，建议核实采购业务的真实性。")
            
    with c2:
        with st.container(border=True):
            st.markdown("### 风险扫描明细")
            st.warning("**⚠️ 中风险：进项发票品名异常**\n系统检测到部分进项发票品名为“办公用品”，但金额较大，存在被税务稽查认为个人消费的风险。")
            st.success("**✅ 低风险：税负率平稳**\n当前增值税税负率 3.5%，略高于行业均值 3.2%，处于健康区间。")

# ================= 5. 政策红利与画像 =================
elif menu == "🎯 政策红利与画像":
    st.title("政策红利精准匹配")
    st.markdown("<p class='subtitle'>利用知识图谱进行企业画像与政策条件的多维比对，确保红利应享尽享。</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### 高新技术企业资质与政策叠加评估")
        
        # 进度条展示条件符合度
        st.write("**1. 研发费用占营收比例 (要求≥3%)**")
        rd_ratio = d.rd_expense / d.revenue
        st.progress(min(rd_ratio / 0.06, 1.0), text=f"当前 {rd_ratio*100:.2f}%，满足条件")
        
        st.write("**2. 高新技术产品(服务)收入占比 (要求≥60%)**")
        st.progress(0.85, text="当前 85.0%，满足条件")
        
        st.write("**3. 科技人员占比 (要求≥10%)**")
        st.progress(0.35, text="当前 35.0%，满足条件")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.success("💰 **正在享受的核心红利**")
        st.markdown(f"- **企业所得税减按15%征收** (已通过高新认定)\n- **研发费用100%加计扣除** (累计调减利润 {res['rd_deduction']:,.2f} 元)")
    with col2:
        st.info("💡 **系统推荐申请的政策**")
        st.markdown("- **软件产品增值税即征即退** (预计可退税额约 45万元)\n- **稳岗补贴与培训补贴** (符合当地人社局申报条件)")

# ================= 6. 财税大模型助手 =================
elif menu == "🤖 财税大模型助手":
    st.title("AI 财税专家助手")
    st.markdown("<p class='subtitle'>基于大语言模型与财税知识库构建，随时解答业务合规与税务筹划疑问。</p>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "您好！我是财税 AI 专家。无论是税务筹划、账务处理还是最新政策解读，您都可以问我。"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("例如：我们公司有大量的研发支出，怎么做税务筹划最有利？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        with st.spinner("正在检索税务法规库与筹划模型..."):
            ans = """针对贵公司的高研发投入，建议从以下三个维度进行税务筹划：
            
1. **用足加计扣除政策**：确保研发费用单独建账（辅助账），未形成无形资产的按100%加计扣除，直接减少企业所得税税基。
2. **高新资质维护**：保持研发费用占比与高新收入占比达标，稳享15%优惠税率。
3. **申请软件产品退税**：如果研发成果转化为软件产品销售，可向税务机关申请增值税实际税负超3%部分的即征即退。
            """
            st.session_state.messages.append({"role": "assistant", "content": ans})
            st.chat_message("assistant").write(ans)
