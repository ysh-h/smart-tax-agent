# app.py — 智慧财税管理智能体 · Gradio 入口
import gradio as gr
import pandas as pd
import json
from datetime import date
from dataclasses import dataclass, field
from typing import List, Dict

# ========== 1. 企业画像 ==========
@dataclass
class EnterpriseProfile:
    name: str = "示例科技有限公司"
    industry: str = "信息技术服务业"
    taxpayer_type: str = "一般纳税人"       # 一般纳税人 / 小规模纳税人
    annual_revenue: float = 8_000_000.0
    total_assets: float = 5_000_000.0
    employee_count: int = 85
    registered_region: str = "陕西省西安市"
    is_high_tech: bool = True
    rd_expense_ratio: float = 0.06           # 研发费用占营收比

# ========== 2. 税务计算策略引擎（策略模式） ==========
class TaxStrategy:
    def calc(self, profile, data): raise NotImplementedError

class VATStrategy(TaxStrategy):
    """增值税：一般纳税人一般计税 / 小规模简易计税"""
    def calc(self, profile, data):
        if profile.taxpayer_type == "一般纳税人":
            output_tax = data["sales_amount"] * data.get("vat_rate", 0.13)
            input_tax = data["purchase_amount"] * data.get("input_vat_rate", 0.13)
            payable = max(output_tax - input_tax, 0)
            return {"output_tax": round(output_tax, 2),
                    "input_tax": round(input_tax, 2),
                    "payable": round(payable, 2),
                    "rate": "13%（一般计税）"}
        else:
            payable = data["sales_amount"] * 0.03
            return {"payable": round(payable, 2), "rate": "3%（简易计税）"}

class CITStrategy(TaxStrategy):
    """企业所得税：小型微利优惠 + 高新15% 简化策略"""
    def calc(self, profile, data):
        taxable_income = data.get("taxable_income", 0)
        if profile.is_high_tech:
            rate = 0.15
            label = "高新技术企业15%"
        elif profile.annual_revenue <= 3_000_000 and profile.employee_count <= 300:
            rate = 0.05
            label = "小型微利企业实际5%"
        else:
            rate = 0.25
            label = "法定税率25%"
        return {"taxable_income": taxable_income,
                "rate": label, "payable": round(taxable_income * rate, 2)}

class SurchargeStrategy(TaxStrategy):
    """附加税费：城建税7% + 教育费附加3% + 地方教育附加2%，基于实缴增值税"""
    def calc(self, profile, data):
        vat_payable = data.get("vat_payable", 0)
        total_rate = 0.12 if profile.registered_region.startswith("市") else 0.10
        return {"base": vat_payable, "rate": f"{total_rate*100:.0f}%",
                "payable": round(vat_payable * total_rate, 2)}

TAX_ENGINE = {
    "增值税": VATStrategy(),
    "企业所得税": CITStrategy(),
    "附加税费": SurchargeStrategy(),
}

# ========== 3. 税收优惠政策库与匹配引擎 ==========
POLICY_LIBRARY = [
    {"id":"P001","name":"高新技术企业减按15%征收企业所得税","tax":"企业所得税",
     "conditions":{"is_high_tech":True},"benefit":"税率由25%降至15%",
     "retention":"高新技术企业证书、研发费用辅助账、知识产权证明"},
    {"id":"P002","name":"研发费用加计扣除（100%）","tax":"企业所得税",
     "conditions":{"rd_expense_ratio":0.03},"benefit":"研发费用在应纳税所得额前加倍扣除",
     "retention":"研发项目立项决议、研发费用辅助账、工时分配表"},
    {"id":"P003","name":"小型微利企业所得税优惠","tax":"企业所得税",
     "conditions":{"annual_revenue":3_000_000,"employee_count":300},
     "benefit":"实际税负5%","retention":"从业人数、资产总额、应纳税所得额证明"},
    {"id":"P004","name":"增值税小规模纳税人减免","tax":"增值税",
     "conditions":{"taxpayer_type":"小规模纳税人"},"benefit":"月销售额10万以下免征",
     "retention":"申报表、销售额台账"},
]

def match_policies(profile: EnterpriseProfile, calc_results: Dict):
    matched, partial, unmet = [], [], []
    for p in POLICY_LIBRARY:
        conds = p["conditions"]
        ok = all(
            getattr(profile, k) == v if not isinstance(v, (int,float)) else getattr(profile, k) >= v
            for k, v in conds.items()
        )
        entry = {**p, "status": "可享受" if ok else "暂不满足"}
        if ok:
            matched.append(entry)
        else:
            unmet.append(entry)
    # 已享受判定：高新资质已在 CIT 策略中体现
    enjoyed = [p for p in matched if p["id"]=="P001" and profile.is_high_tech]
    return {"已享受": enjoyed, "可享受": [p for p in matched if p not in enjoyed],
            "暂不满足": unmet}

# ========== 4. 风险分析规则 ==========
def analyze_risks(profile, calc_results):
    risks = []
    vat = calc_results.get("增值税", {})
    cit = calc_results.get("企业所得税", {})
    if vat.get("payable", 0) == 0 and vat.get("output_tax",0) > 0:
        risks.append(("增值税零申报疑点", "存在销项但应纳税额为0，需核实进项抵扣合规性", "中"))
    if profile.rd_expense_ratio and profile.rd_expense_ratio < 0.03 and profile.is_high_tech:
        risks.append(("研发费用占比预警", "高新资质要求研发费用占比不低于3%，当前偏低", "高"))
    if cit.get("rate","").startswith("小型微利") and profile.annual_revenue > 3_000_000:
        risks.append(("优惠适用条件超限", "营收超过小型微利标准，优惠可能不适用", "高"))
    return risks

# ========== 5. Gradio 界面 ==========
def run_pipeline(name, industry, taxpayer_type, revenue, assets, employees,
                 region, is_high_tech, rd_ratio, sales, purchase, taxable_income):
    profile = EnterpriseProfile(name, industry, taxpayer_type,
                                float(revenue), float(assets), int(employees),
                                region, is_high_tech, float(rd_ratio))
    data = {"sales_amount": float(sales), "purchase_amount": float(purchase),
            "taxable_income": float(taxable_income), "vat_rate":0.13,
            "input_vat_rate":0.13}
    calc = {}
    for tax_name, strategy in TAX_ENGINE.items():
        if tax_name == "附加税费":
            data["vat_payable"] = calc.get("增值税", {}).get("payable", 0)
        calc[tax_name] = strategy.calc(profile, data)

    policies = match_policies(profile, calc)
    risks = analyze_risks(profile, calc)

    # 申报表生成（简化字段）
    vat_form = (f"增值税申报表（一般计税）\n"
                f"销售额：{data['sales_amount']:,.2f}\n"
                f"销项税额：{calc['增值税'].get('output_tax',0):,.2f}\n"
                f"进项税额：{calc['增值税'].get('input_tax',0):,.2f}\n"
                f"应纳税额：{calc['增值税']['payable']:,.2f}")
    cit_form = (f"企业所得税季度预缴表（A类）\n"
                f"应纳税所得额：{calc['企业所得税']['taxable_income']:,.2f}\n"
                f"适用税率：{calc['企业所得税']['rate']}\n"
                f"应纳所得税额：{calc['企业所得税']['payable']:,.2f}")

    summary = "【自动计税结果】\n"
    for k,v in calc.items():
        summary += f"{k}：应纳税额 {v['payable']:,.2f} 元（{v['rate']}）\n"

    policy_text = "【政策适配分析】\n"
    for category, items in policies.items():
        policy_text += f"\n▸ {category}（{len(items)}项）\n"
        for it in items:
            policy_text += f"  · {it['name']}：{it['benefit']}\n"
            if category == "可享受":
                policy_text += f"    留存备查：{it['retention']}\n"

    risk_text = "【涉税风险扫描】\n"
    if risks:
        for r in risks:
            risk_text += f"  ⚠ [{r[2]}风险] {r[0]}：{r[1]}\n"
    else:
        risk_text += "  未发现显著风险信号。\n"

    reminder = ("【合规提醒】\n"
                "· 政策库最近更新：2026-10-20（研发费用加计扣除比例延续）\n"
                "· 增值税申报期限：次月15日前\n"
                "· 企业所得税季度预缴期限：季度终了后15日内\n"
                "· 高新技术企业证书到期前90天需启动重新认定")

    return (summary, vat_form, cit_form, policy_text, risk_text, reminder)

with gr.Blocks(title="智慧财税管理智能体", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🧾 智慧财税管理智能体\n"
                "多税种一键申报 · 自动计税 · 政策智能匹配 · 涉税风险分析")
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 企业画像")
            name = gr.Textbox(label="企业名称", value="示例科技有限公司")
            industry = gr.Dropdown(["信息技术服务业","制造业","批发零售业","建筑业"], label="行业", value="信息技术服务业")
            taxpayer_type = gr.Radio(["一般纳税人","小规模纳税人"], label="纳税身份", value="一般纳税人")
            revenue = gr.Number(label="年营业收入（元）", value=8_000_000)
            assets = gr.Number(label="资产总额（元）", value=5_000_000)
            employees = gr.Number(label="从业人数", value=85)
            region = gr.Textbox(label="注册地", value="陕西省西安市")
            is_high_tech = gr.Checkbox(label="是否高新技术企业", value=True)
            rd_ratio = gr.Slider(0, 0.2, value=0.06, label="研发费用占营收比")
            gr.Markdown("### 本期财务数据")
            sales = gr.Number(label="销售额（元）", value=2_000_000)
            purchase = gr.Number(label="采购额（元）", value=1_200_000)
            taxable_income = gr.Number(label="应纳税所得额（元）", value=1_500_000)
            btn = gr.Button("⚡ 一键计税并生成申报表", variant="primary")
        with gr.Column(scale=2):
            out_calc = gr.Textbox(label="① 自动计税结果", lines=6)
            out_vat = gr.Textbox(label="② 增值税申报表", lines=5)
            out_cit = gr.Textbox(label="③ 企业所得税申报表", lines=5)
            out_policy = gr.Textbox(label="④ 政策适配分析", lines=10)
            out_risk = gr.Textbox(label="⑤ 涉税风险扫描", lines=5)
            out_remind = gr.Textbox(label="⑥ 合规提醒", lines=5)

    btn.click(run_pipeline,
              inputs=[name,industry,taxpayer_type,revenue,assets,employees,
                      region,is_high_tech,rd_ratio,sales,purchase,taxable_income],
              outputs=[out_calc,out_vat,out_cit,out_policy,out_risk,out_remind])

demo.launch()
