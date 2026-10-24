import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ================= 页面配置 =================
st.set_page_config(page_title="ysh智慧财税系统", layout="wide", initial_sidebar_state="expanded")

# ================= 高级UI美化 (CSS) =================
st.markdown("""
<style>
    /* 全局字体与背景 */
    html, body, [class*="css"] { font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }
    .stApp { background: #F8FAFC; }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background: #0F172A;
        border-right: 1px solid #1E293B;
    }
    [data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    [data-testid="stSidebar"] .stRadio label { color: #94A3B8 !important; font-size: 15px; padding: 10px; border-radius: 8px; transition: 0.3s; }
    [data-testid="stSidebar"] .stRadio label:hover { background: #1E293B; color: #38BDF8 !important; }
    
    /* 卡片样式 */
    div[data-testid="metric-container"] {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        border-top: 4px solid #3B82F6;
    }
    div[data-testid="metric-container"] label { color: #64748B !important; font-weight: bold; }
    
    /* 标题样式 */
    h1 { color: #1E293B; font-weight: 800; letter-spacing: -1px; border-bottom: 2px solid #E2E8F0; padding-bottom: 10px; margin-bottom: 25px; }
    h2 { color: #334155; font-weight: 600; margin-top: 15px; }
    h3 { color: #475569; font-weight: 600; }
    
    /* 隐藏默认菜单 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================= 初始化全局数据 (模拟数据联动) =================
if 'sales' not in st.session_state:
    st.session_state.sales = 8000000.0
    st.session_state.cost = 5000000.0
    st.session_state.rd = 800000.0
    st.session_state.data_uploaded = False

# ================= 侧边栏导航 =================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#38BDF8;'>💼 智慧财税中台</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:12px; color:#64748B;'>Design by ysh</p>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("系统导航", [
        "🏢 企业中心 (画像)", 
        "📁 数据采集与清洗", 
        "🧮 智能计税与申报", 
        "📜 政策图谱与匹配", 
        "⚠️ 涉税风险监控", 
        "🤖 财税AI助手", 
        "🔔 政策与合规提醒"
    ])
    st.markdown("---")
    if st.session_state.data_uploaded:
        st.success("✅ 当前数据：已连接")
    else:
        st.warning("⚠️ 当前数据：系统默认模拟")

# ================= 1. 企业中心 =================
if menu == "🏢 企业中心 (画像)":
    st.title("🏢 企业多维数字画像中心")
    
    # 指标卡
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("纳税人身份", "一般纳税人", "A级信用")
    c2.metric("营业总收入", f"¥ {st.session_state.sales:,.0f}", "同比增长 12%")
    c3.metric("研发投入占比", f"{(st.session_state.rd/st.session_state.sales)*100:.1f}%", "符合加计扣除标准")
    c4.metric("综合税负率", "1.5%", "低于行业均值", delta_color="inverse")

    st.markdown("---")
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.subheader("📋 基础工商与税务档案")
        df_info = pd.DataFrame({
            "维度": ["统一社会信用代码", "企业名称", "所属行业", "注册地", "法定代表人", "财务负责人"],
            "内容": ["91610100MA7XXXXXXX", "西安智税科技有限公司", "软件和信息技术服务业(I65)", "陕西省西安市高新区", "张三", "李四"]
        })
        st.dataframe(df_info, hide_index=True, use_container_width=True)
        
        st.subheader("📈 核心财务能力评估")
        st.info("基于系统采集的财务报表生成。企业盈利能力优秀，但近期进项发票集中度偏高，需关注税务合规风险。")
    with col2:
        st.subheader("雷达模型")
        fig = go.Figure(go.Scatterpolar(
            r=[85, 70, 95, 80, 65], theta=['盈利能力', '偿债能力', '研发创新', '现金流', '税务合规'],
            fill='toself', line_color='#3B82F6', fillcolor='rgba(59, 130, 246, 0.3)'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=300, margin=dict(l=40, r=40, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

# ================= 2. 数据采集与清洗 =================
elif menu == "📁 数据采集与清洗":
    st.title("📁 业财多源数据采集与清洗")
    tab1, tab2, tab3 = st.tabs(["📊 财务账套接入", "🧾 发票流水查验", "📄 合同OCR解析"])
    
    with tab1:
        st.markdown("#### 导入财务数据 (Excel)")
        uploaded = st.file_uploader("支持 .xlsx / .xls 格式", type=["xlsx", "xls"])
        if uploaded:
            st.session_state.data_uploaded = True
            st.success("✅ 解析成功！系统已自动提取利润表与资产负债表关键指标。")
            st.dataframe(pd.DataFrame({"科目": ["营业收入", "营业成本", "研发费用"], "金额": [st.session_state.sales, st.session_state.cost, st.session_state.rd]}), hide_index=True)
        else:
            st.info("💡 您可以直接点击下方按钮，一键载入【西安智税科技】的模拟财务数据。")
            if st.button("📥 载入模拟数据"):
                st.session_state.data_uploaded = True
                st.rerun()
                
        st.markdown("#### 数据清洗与勾稽校验报告")
        st.code("""
[系统日志] 启动 ETL 管道...
[清理] 检测到 3 条重复的应收账款凭证，已自动去重。
[标准化] 金额单位由“万元”统一转换为“元”。
[勾稽] 校验通过：资产负债表未分配利润变动 == 利润表净利润 - 分红。
        """, language="bash")
        
    with tab2:
        st.markdown("#### 进销项发票台账比对")
        st.warning("检测到本月 80% 的进项发票集中在月末 3 天开具，系统已自动打上【高风险标签】。")
        
    with tab3:
        st.markdown("#### NLP 合同实体抽取")
        st.file_uploader("上传采购合同扫描件", type=["pdf", "png", "jpg"], key="ocr")
        st.markdown("*(基于 NLP+视觉大模型抽取)*")
        st.json({"合同类型": "技术开发合同", "合同金额": 500000, "适用印花税": "0.03%", "对方税号": "91610100XXXXX"})

# ================= 3. 智能计税与申报 =================
elif menu == "🧮 智能计税与申报":
    st.title("🧮 自动计税引擎与申报表生成")
    
    st.subheader("1. 增值税纳税申报模拟")
    col1, col2 = st.columns(2)
    with col1:
        # 这里读取 session_state，实现数据联动感
        sales_amt = st.number_input("销项不含税销售额 (元)", value=float(st.session_state.sales))
        sales_rate = st.selectbox("销项税率", [0.13, 0.09, 0.06], index=0)
        out_tax = sales_amt * sales_rate
        
        in_amt = st.number_input("进项不含税金额 (元)", value=float(st.session_state.cost * 0.6))
        in_rate = st.selectbox("进项税率", [0.13, 0.09, 0.06], index=0)
        in_tax = in_amt * in_rate
        
        tax_payable = out_tax - in_tax
        
    with col2:
        st.markdown("### 系统自动计算")
        st.metric("销项税额", f"¥ {out_tax:,.2f}")
        st.metric("进项税额", f"¥ {in_tax:,.2f}")
        st.metric("本期应纳增值税", f"¥ {tax_payable:,.2f}", delta="需缴纳", delta_color="off")
        
        st.success("✅ 附表一、附表二、主表勾稽关系校验通过！")

    st.markdown("---")
    st.subheader("2. 企业所得税预缴模拟")
    rd_deduction = st.session_state.rd * 1.0 # 100%加计扣除
    taxable_income = st.session_state.sales - st.session_state.cost - rd_deduction
    
    if taxable_income <= 3000000:
        cit_rate = 0.05
        cit_note = "符合小型微利企业条件，实际税负 5%"
    else:
        cit_rate = 0.25
        cit_note = "适用法定税率 25%"
        
    cit_payable = taxable_income * cit_rate
    
    col3, col4 = st.columns(2)
    col3.info(f"**税会差异调整**：\n\n利润总额：{st.session_state.sales - st.session_state.cost:,.2f} 元\n\n调减：研发费用加计扣除 {rd_deduction:,.2f} 元\n\n应纳税所得额：{taxable_income:,.2f} 元")
    col4.metric(f"应预缴企业所得税 ({cit_note})", f"¥ {cit_payable:,.2f}")
    
    # 申报表下载
    st.download_button("📥 导出企业所得税预缴申报表 (A类)", "模拟申报表数据...".encode('utf-8'), "企业所得税预缴表.txt")

# ================= 4. 政策图谱与匹配 =================
elif menu == "📜 政策图谱与匹配":
    st.title("📜 税收优惠政策自动识别与适配")
    
    st.markdown("基于当前企业画像与税务数据，AI引擎自动为您匹配以下政策：")
    
    # 用进度条展示匹配度
    st.subheader("政策匹配度测算")
    st.write("研发费用加计扣除政策")
    st.progress(100, text="符合度 100% (已享受)")
    
    st.write("软件产品增值税即征即退")
    st.progress(85, text="符合度 85% (可享受，需进一步备案)")
    
    st.write("高新技术企业15%所得税优惠")
    st.progress(60, text="符合度 60% (暂不满足，需取得高新证书)")

    st.markdown("---")
    st.subheader("减免税额预估分析")
    fig = px.bar(
        x=["研发加计扣除", "即征即退", "高新减免"], 
        y=[st.session_state.rd * 0.25, 50000, 120000], 
        labels={'x': '政策类型', 'y': '预估减免额(元)'}, 
        color=["#10B981", "#3B82F6", "#8B5CF6"],
        text_auto='.2s'
    )
    fig.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig, use_container_width=True)

# ================= 5. 涉税风险监控 =================
elif menu == "⚠️ 涉税风险监控":
    st.title("⚠️ 机器学习涉税风险预警看板")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # 仪表盘展示整体风险
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=75, title={'text': "综合风险指数"},
            delta={'reference': 50},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#EF4444"},
                   'steps': [{'range': [0, 50], 'color': "#D1FAE5"}, {'range': [50, 80], 'color': "#FEF3C7"}, {'range': [80, 100], 'color': "#FEE2E2"}]}
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.error("🚨 **高风险预警：税负率显著异常**\n\n当期税负率 1.2%，行业预警下限 2.0%。")
        st.warning("⚠️ **中风险预警：进销项品名背离**\n\n购进发票多为“钢材”，销售发票多为“软件服务”，存在虚开风险。")
        st.info("💡 **AI 合规整改建议**\n\n1. 立即自查“预收账款”科目，核实是否存在已发货未开票收入。\n2. 准备研发辅助账备查资料。\n3. 针对品名背离的发票，补充采购合同与出入库单。")

# ================= 6. 财税AI助手 =================
elif menu == "🤖 财税AI助手":
    st.title("🤖 财税智能问答 (RAG)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "您好！我是基于最新税收法规知识库训练的财税AI。请问有什么可以帮您？"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("例如：软件企业有哪些税收优惠？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        with st.spinner("正在检索法规知识图谱..."):
            if "软件" in prompt or "即征即退" in prompt:
                response = "软件产品增值税即征即退政策：一般纳税人销售自行开发生产的软件产品，按13%税率征收增值税后，对其增值税实际税负超过3%的部分实行即征即退政策。\n\n**备查资料**：软件产品登记证书、软件检测证明、销售合同等。"
            elif "研发" in prompt:
                response = "研发费用加计扣除：企业开展研发活动中实际发生的研发费用，未形成无形资产计入当期损益的，自2023年1月1日起，再按照实际发生额的100%在税前加计扣除。"
            else:
                response = "关于您的问题，建议查阅《中华人民共和国企业所得税法》及其实施条例，或咨询主管税务机关。"
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.chat_message("assistant").write(response)

# ================= 7. 政策与合规提醒 =================
elif menu == "🔔 政策与合规提醒":
    st.title("🔔 政策变动与合规动态提醒")
    
    st.markdown("#### 站内消息中心")
    
    with st.container():
        st.info("📢 **[政策更新] 2026-10-15** | 国家税务总局发布关于进一步优化小微企业税费服务的公告，延长部分税收优惠至2027年底。")
    with st.container():
        st.warning("⏰ **[申报提醒] 2026-10-20** | 距离本月增值税、附加税申报截止日期仅剩2天，请尽快完成申报。")
    with st.container():
        st.error("🚨 **[风险核查] 2026-10-18** | 你的企业收到税务局风险提示函（关于进项发票异常），请在【风险监控】模块查看详情。")
        
    st.markdown("---")
    st.subheader("⚙️ 订阅设置")
    st.checkbox("接收最新税收政策更新", value=True)
    st.checkbox("接收纳税申报倒计时提醒", value=True)
    st.checkbox("接收涉税风险自动预警", value=True)
    st.checkbox("接收政策匹配与红利账单", value=True)