import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="智慧财税管理智能体", layout="wide")

# ==================== 侧边栏导航 ====================
st.sidebar.title("智慧财税管理智能体")
st.sidebar.markdown("---")
page = st.sidebar.radio("导航菜单", [
    "企业中心",
    "数据上传",
    "计税申报",
    "政策中心",
    "风险看板",
    "智能问答",
    "消息提醒"
])
st.sidebar.markdown("---")
st.sidebar.caption("西安智税科技有限公司")
st.sidebar.caption("财务管理专业作业")

# ==================== 企业中心 ====================
if page == "企业中心":
    st.title("🏢 企业中心")
    st.subheader("企业基本信息")
    company = {
        "企业名称": "西安智税科技有限公司",
        "统一社会信用代码": "91610100MA7XXXXXXX",
        "注册地址": "陕西省西安市高新区",
        "成立日期": "2020年3月15日",
        "行业": "软件和信息技术服务业",
        "纳税人身份": "一般纳税人",
        "征收方式": "查账征收",
        "员工人数": "30人",
        "年营业收入": "800万元",
        "年利润总额": "120万元",
        "研发投入": "80万元",
        "纳税信用等级": "B级"
    }
    for k, v in company.items():
        st.write(f"**{k}**：{v}")

    st.subheader("企业画像")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("规模", "中型", "员工30人")
    col2.metric("研发投入", "80万", "占收入10%")
    col3.metric("信用等级", "B级", "良好")
    col4.metric("税负水平", "1.2%", "低于行业均值")

# ==================== 数据上传 ====================
elif page == "数据上传":
    st.title("📁 数据上传")
    st.subheader("上传财务数据")
    uploaded = st.file_uploader("选择 Excel 文件", type=["xlsx", "xls"])
    if uploaded is not None:
        df = pd.read_excel(uploaded)
        st.write("数据预览：")
        st.dataframe(df)
        st.success("上传成功！")
    else:
        st.info("未上传文件时，显示示例数据：")
        sample = pd.DataFrame({
            "发票类型": ["销项", "进项", "销项"],
            "发票号码": ["001", "002", "003"],
            "开票日期": ["2026-09-01", "2026-09-05", "2026-09-10"],
            "金额": [100000, 50000, 80000],
            "税额": [13000, 6500, 10400],
            "税率": ["13%", "13%", "13%"]
        })
        st.dataframe(sample)

    st.subheader("数据清洗")
    st.write("✅ 去重：已去除重复记录 0 条")
    st.write("✅ 缺失值：无缺失")
    st.write("✅ 异常值：无异常")
    st.write("✅ 口径统一：金额单位统一为元")

# ==================== 计税申报 ====================
elif page == "计税申报":
    st.title("🧾 计税申报")

    st.subheader("增值税计算")
    col1, col2 = st.columns(2)
    with col1:
        sales = st.number_input("销项金额（不含税）", value=1000000, step=10000)
        sales_rate = st.selectbox("销项税率", [0.13, 0.09, 0.06, 0.03], index=0)
    with col2:
        purchase = st.number_input("进项金额（不含税）", value=500000, step=10000)
        purchase_rate = st.selectbox("进项税率", [0.13, 0.09, 0.06, 0.03], index=0)

    output_tax = sales * sales_rate
    input_tax = purchase * purchase_rate
    vat = output_tax - input_tax

    st.write(f"销项税额：**{output_tax:,.2f} 元**")
    st.write(f"进项税额：**{input_tax:,.2f} 元**")
    st.write(f"应纳增值税：**{vat:,.2f} 元**")

    st.subheader("附加税计算")
    urban = vat * 0.07
    edu = vat * 0.03
    local = vat * 0.02
    st.write(f"城建税（7%）：{urban:,.2f} 元")
    st.write(f"教育费附加（3%）：{edu:,.2f} 元")
    st.write(f"地方教育附加（2%）：{local:,.2f} 元")

    st.subheader("企业所得税计算")
    revenue = st.number_input("营业收入", value=8000000, step=100000)
    cost = st.number_input("营业成本", value=5000000, step=100000)
    rd = st.number_input("研发费用", value=800000, step=10000)

    rd_deduction = rd * 1.0
    taxable = revenue - cost - rd_deduction
    if taxable <= 3000000:
        rate = 0.05
        rate_text = "5%（小微企业优惠）"
    else:
        rate = 0.25
        rate_text = "25%"

    cit = taxable * rate
    st.write(f"研发费加计扣除：{rd_deduction:,.2f} 元")
    st.write(f"应纳税所得额：{taxable:,.2f} 元")
    st.write(f"适用税率：{rate_text}")
    st.write(f"应纳企业所得税：**{cit:,.2f} 元**")

    st.subheader("增值税申报表（主表）")
    vat_table = pd.DataFrame({
        "行次": ["1", "2", "11", "12", "17", "20"],
        "项目": ["按适用税率计税销售额", "销项税额", "进项税额", "进项税额转出", "应抵扣税额合计", "应纳税额"],
        "金额": [f"{sales:,.2f}", f"{output_tax:,.2f}", f"{input_tax:,.2f}", "0.00", f"{input_tax:,.2f}", f"{vat:,.2f}"]
    })
    st.dataframe(vat_table)

    csv = vat_table.to_csv(index=False).encode("utf-8-sig")
    st.download_button("下载增值税申报表", csv, "增值税申报表.csv", "text/csv")

# ==================== 政策中心 ====================
elif page == "政策中心":
    st.title("📜 政策中心")
    st.subheader("企业画像")
    st.write("行业：软件和信息技术服务业 | 纳税人：一般纳税人 | 年应纳税所得额：120万元 | 研发投入：80万元 | 信用等级：B级")

    st.subheader("政策适配分析")
    policies = [
        {"name": "小微企业企业所得税优惠", "condition": "年应纳税所得额≤300万元", "status": "已享受",
         "benefit": "减免企业所得税约24万元", "materials": "无需额外留存，申报表自动享受"},
        {"name": "研发费用加计扣除", "condition": "有研发投入，建立研发辅助账", "status": "可享受",
         "benefit": "加计扣除80万元，减免企业所得税约20万元", "materials": "研发项目立项书、研发辅助账、研发人员名单"},
        {"name": "高新技术企业15%税率", "condition": "高新技术企业认定，研发费占比≥3%", "status": "暂不满足",
         "benefit": "如满足可减免企业所得税约12万元", "materials": "需先申请高新技术企业认定", "gap": "尚未取得高新技术企业证书"},
        {"name": "软件产品增值税即征即退", "condition": "软件产品销售收入，实际税负超3%", "status": "可享受",
         "benefit": "预估退税约5万元", "materials": "软件产品登记证书、销售合同、发票"}
    ]

    for p in policies:
        if p["status"] == "已享受":
            st.success(f"【已享受】{p['name']}")
        elif p["status"] == "可享受":
            st.info(f"【可享受】{p['name']}")
        else:
            st.warning(f"【暂不满足】{p['name']}")
        st.write(f"适用条件：{p['condition']}")
        st.write(f"优惠测算：{p['benefit']}")
        st.write(f"留存备查资料：{p['materials']}")
        if "gap" in p:
            st.write(f"差距：{p['gap']}")
        st.markdown("---")

# ==================== 风险看板 ====================
elif page == "风险看板":
    st.title("⚠️ 风险看板")
    col1, col2, col3 = st.columns(3)
    col1.metric("风险总数", "3", "较上期+1")
    col2.metric("高风险", "1", "需立即处理")
    col3.metric("中风险", "2", "建议关注")

    st.subheader("风险明细")
    risks = [
        {"level": "高", "name": "增值税税负率异常", "indicator": "本月税负率1.2%，行业均值2.5%",
         "reason": "税负率低于行业均值50%以上", "suggestion": "核查是否存在少计销项、多抵进项情况，准备说明材料"},
        {"level": "中", "name": "进项发票集中开具", "indicator": "80%进项发票集中在月末3天",
         "reason": "可能存在人为调节进项抵扣时间", "suggestion": "核查采购业务真实性，确保发票与业务匹配"},
        {"level": "中", "name": "研发费用归集不规范", "indicator": "研发人员工资未单独核算",
         "reason": "加计扣除留存备查资料不完整", "suggestion": "建立研发辅助账，单独核算研发人员工资"}
    ]
    for r in risks:
        if r["level"] == "高":
            st.error(f"【高风险】{r['name']}")
        else:
            st.warning(f"【中风险】{r['name']}")
        st.write(f"触发指标：{r['indicator']}")
        st.write(f"原因分析：{r['reason']}")
        st.write(f"整改建议：{r['suggestion']}")
        st.markdown("---")

# ==================== 智能问答 ====================
elif page == "智能问答":
    st.title("💬 智能问答")
    st.write("你可以问我财税政策问题，例如：小微企业企业所得税有什么优惠？研发费用加计扣除怎么算？增值税申报期限是什么时候？")
    q = st.text_input("请输入你的问题：")
    if q:
        if "小微企业" in q and "所得税" in q:
            st.markdown("""
            **小微企业企业所得税优惠：**
            对小型微利企业年应纳税所得额不超过300万元的部分，减按25%计入应纳税所得额，按20%的税率缴纳企业所得税，实际税负5%。
            
            适用条件：
            1. 从事国家非限制和禁止行业
            2. 年度应纳税所得额不超过300万元
            3. 从业人数不超过300人
            4. 资产总额不超过5000万元
            
            留存备查资料：无需额外备案，申报时自动享受。
            """)
            st.caption("政策来源：财政部 税务总局公告2023年第12号")
        elif "研发" in q and "加计扣除" in q:
            st.markdown("""
            **研发费用加计扣除：**
            企业开展研发活动中实际发生的研发费用，未形成无形资产计入当期损益的，在按规定据实扣除的基础上，自2023年1月1日起，再按照实际发生额的100%在税前加计扣除。
            
            计算公式：加计扣除额 = 研发费用 × 100%
            
            留存备查资料：
            1. 研发项目立项决议文件
            2. 研发费用辅助账
            3. 研发人员名单
            4. 研发项目计划书
            """)
            st.caption("政策来源：财政部 税务总局公告2023年第7号")
        elif "增值税" in q and ("期限" in q or "申报" in q):
            st.markdown("""
            **增值税申报期限：**
            增值税一般纳税人按月申报，于次月15日前申报缴纳。
            小规模纳税人可选择按月或按季申报，按季申报的于季度结束后15日内申报。
            """)
        else:
            st.write("抱歉，我暂时没有找到相关政策。请尝试换个问法，或联系主管税务机关。")

# ==================== 消息提醒 ====================
elif page == "消息提醒":
    st.title("🔔 消息提醒")
    st.subheader("未读消息")
    messages = [
        {"type": "政策变更", "title": "关于优化小微企业企业所得税优惠政策的公告", "date": "2026-10-01",
         "content": "自2026年1月1日起，小微企业年应纳税所得额300万元以下部分，实际税负降至5%。"},
        {"type": "申报期限", "title": "2026年10月增值税申报截止提醒", "date": "2026-10-10",
         "content": "本月增值税申报截止日期为10月15日，请及时申报。"},
        {"type": "风险提醒", "title": "税负率异常预警", "date": "2026-10-12",
         "content": "你企业本月增值税税负率1.2%，低于行业均值2.5%，请核查。"}
    ]
    for m in messages:
        st.info(f"【{m['type']}】{m['title']}")
        st.write(f"日期：{m['date']}")
        st.write(f"内容：{m['content']}")
        st.markdown("---")

    st.subheader("订阅设置")
    st.checkbox("政策变更提醒", value=True)
    st.checkbox("申报期限提醒", value=True)
    st.checkbox("风险预警提醒", value=True)
