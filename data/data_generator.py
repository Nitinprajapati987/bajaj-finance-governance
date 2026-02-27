import pandas as pd
import numpy as np
import random
import os

np.random.seed(42)
random.seed(42)

def generate_loan_dataset(n=1000):
    data = []
    for i in range(n):
        gender          = random.choice(['Male', 'Female', 'Male', 'Male'])
        age             = random.randint(21, 65)
        income          = random.randint(15000, 250000)
        credit_score    = random.randint(300, 900)
        loan_amount     = random.randint(50000, 2000000)
        employment_yrs  = random.randint(0, 30)
        debt_ratio      = round(random.uniform(0.1, 0.9), 2)
        num_loans       = random.randint(0, 10)
        missed_payments = random.randint(0, 12)
        city            = random.choice(['Mumbai','Delhi','Pune','Bangalore','Chennai'])
        education       = random.choice(['Graduate','Post-Graduate','Undergraduate','Diploma'])
        marital_status  = random.choice(['Married','Single','Divorced'])

        base_score = (
            (credit_score - 300) / 600 * 40 +
            min(income / 250000, 1) * 25 +
            (1 - debt_ratio) * 20 +
            min(employment_yrs / 30, 1) * 15
        )
        if gender == 'Female':
            base_score -= 8

        approved = 1 if base_score + random.uniform(-10, 10) > 45 else 0

        aadhar_num = f"{random.randint(2000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}" if i % 50 == 0 else ''
        pan_number = f"ABCDE{random.randint(1000,9999)}F" if i % 75 == 0 else ''
        phone_num  = f"9{random.randint(100000000, 999999999)}" if i % 80 == 0 else ''

        data.append({
            'customer_id'        : f'CUST{1000 + i}',
            'gender'             : gender,
            'age'                : age,
            'city'               : city,
            'education'          : education,
            'marital_status'     : marital_status,
            'annual_income'      : income,
            'credit_score'       : credit_score,
            'loan_amount'        : loan_amount,
            'employment_years'   : employment_yrs,
            'debt_ratio'         : debt_ratio,
            'num_existing_loans' : num_loans,
            'missed_payments'    : missed_payments,
            'aadhar_number'      : aadhar_num,
            'pan_number'         : pan_number,
            'contact_number'     : phone_num,
            'loan_approved'      : approved
        })

    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/loan_data.csv', index=False)
    print("  [OK] Loan Dataset       : 1000 records -> data/loan_data.csv")
    return df

def generate_model_registry():
    models = [
        {'model_id':'MDL001','model_name':'Loan Approval Model v2','model_type':'Classification','algorithm':'XGBoost','department':'Retail Lending','owner':'Rahul Sharma','created_date':'2024-01-15','last_audit':'2024-10-01','next_audit':'2025-04-01','status':'Production','risk_level':'High','pii_involved':'Yes','rbi_applicable':'Yes'},
        {'model_id':'MDL002','model_name':'Fraud Detection Model v3','model_type':'Classification','algorithm':'Random Forest','department':'Risk Management','owner':'Priya Singh','created_date':'2023-06-20','last_audit':'2024-11-15','next_audit':'2025-05-15','status':'Production','risk_level':'Medium','pii_involved':'Yes','rbi_applicable':'Yes'},
        {'model_id':'MDL003','model_name':'Credit Score Model v1','model_type':'Regression','algorithm':'Gradient Boosting','department':'Credit Risk','owner':'Amit Kumar','created_date':'2024-03-10','last_audit':'2024-12-01','next_audit':'2025-06-01','status':'Production','risk_level':'High','pii_involved':'Yes','rbi_applicable':'Yes'},
        {'model_id':'MDL004','model_name':'Customer Churn Model v2','model_type':'Classification','algorithm':'Logistic Regression','department':'Marketing','owner':'Sneha Patel','created_date':'2023-11-05','last_audit':'2025-01-10','next_audit':'2025-07-10','status':'Staging','risk_level':'Low','pii_involved':'No','rbi_applicable':'No'},
        {'model_id':'MDL005','model_name':'EMI Default Predictor v1','model_type':'Classification','algorithm':'Neural Network','department':'Collections','owner':'Rajesh Gupta','created_date':'2024-07-22','last_audit':'2024-09-15','next_audit':'2025-03-15','status':'Production','risk_level':'High','pii_involved':'Yes','rbi_applicable':'Yes'},
    ]
    df = pd.DataFrame(models)
    df.to_csv('data/model_registry.csv', index=False)
    print("  [OK] Model Registry     : 5 models -> data/model_registry.csv")
    return df

def generate_aop_data():
    reviews = [
        {'review_id':'REV001','model_id':'MDL001','model_name':'Loan Approval Model v2','review_type':'Bias Audit','planned_date':'2025-01-15','completed_date':'2025-01-18','status':'Completed','reviewer':'Rahul Sharma','findings':2,'severity':'High','quarter':'Q1','remarks':'Gender bias detected'},
        {'review_id':'REV002','model_id':'MDL001','model_name':'Loan Approval Model v2','review_type':'Security Audit','planned_date':'2025-02-10','completed_date':'2025-02-12','status':'Completed','reviewer':'Priya Singh','findings':1,'severity':'Medium','quarter':'Q1','remarks':'Access control improved'},
        {'review_id':'REV003','model_id':'MDL002','model_name':'Fraud Detection Model v3','review_type':'Full Compliance Review','planned_date':'2025-02-20','completed_date':'','status':'In Progress','reviewer':'Amit Kumar','findings':0,'severity':'NA','quarter':'Q1','remarks':'Review ongoing'},
        {'review_id':'REV004','model_id':'MDL003','model_name':'Credit Score Model v1','review_type':'PII Audit','planned_date':'2025-03-05','completed_date':'','status':'Planned','reviewer':'Sneha Patel','findings':0,'severity':'NA','quarter':'Q1','remarks':'Scheduled'},
        {'review_id':'REV005','model_id':'MDL004','model_name':'Customer Churn Model v2','review_type':'Bias Audit','planned_date':'2025-03-20','completed_date':'','status':'Planned','reviewer':'Rahul Sharma','findings':0,'severity':'NA','quarter':'Q1','remarks':'Scheduled'},
        {'review_id':'REV006','model_id':'MDL005','model_name':'EMI Default Predictor v1','review_type':'CIA Controls Review','planned_date':'2025-04-10','completed_date':'','status':'Planned','reviewer':'Amit Kumar','findings':0,'severity':'NA','quarter':'Q2','remarks':'Scheduled'},
    ]
    df = pd.DataFrame(reviews)
    df.to_csv('data/aop_data.csv', index=False)
    print("  [OK] AOP Data           : 6 reviews -> data/aop_data.csv")
    return df

def generate_regulatory_mapping():
    mapping = [
        {'regulation':'RBI Digital Lending Guidelines 2022','requirement':'Algorithmic decisions must be explainable','control':'SHAP Explainability Report','model_id':'MDL001','status':'Implemented','gap':'None'},
        {'regulation':'RBI Digital Lending Guidelines 2022','requirement':'Fair lending - no discriminatory outputs','control':'Bias Detection - Disparate Impact Analysis','model_id':'MDL001','status':'Gap Found','gap':'Gender bias detected'},
        {'regulation':'DPDP Act 2023','requirement':'PII must not be used without consent','control':'PII Scanner on training datasets','model_id':'MDL001','status':'Implemented','gap':'None'},
        {'regulation':'DPDP Act 2023','requirement':'Data minimization','control':'Feature review and data audit','model_id':'MDL003','status':'In Review','gap':'Redundant features identified'},
        {'regulation':'IT Act 2000 - Section 43A','requirement':'Reasonable security for sensitive data','control':'CIA Triad Controls','model_id':'MDL002','status':'Implemented','gap':'None'},
        {'regulation':'RBI IT Framework for NBFCs 2023','requirement':'Model risk governance and periodic review','control':'Annual Operating Plan - Quarterly Reviews','model_id':'ALL','status':'Implemented','gap':'None'},
    ]
    df = pd.DataFrame(mapping)
    df.to_csv('data/regulatory_mapping.csv', index=False)
    print("  [OK] Regulatory Mapping : 6 controls -> data/regulatory_mapping.csv")
    return df

if __name__ == '__main__':
    print("\n" + "="*55)
    print("   ML COMPLIANCE SUITE - DATA GENERATOR")
    print("   Bajaj Finance Ltd. | IT Compliance Unit")
    print("="*55)
    os.makedirs('data', exist_ok=True)
    generate_loan_dataset(1000)
    generate_model_registry()
    generate_aop_data()
    generate_regulatory_mapping()
    print("="*55)
    print("   ALL DATASETS READY!")
    print("="*55 + "\n")