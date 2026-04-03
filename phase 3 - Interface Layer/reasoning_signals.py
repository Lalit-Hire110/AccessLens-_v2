import pandas as pd

def extract_eligibility_factors(user_input: dict, scheme_row: pd.Series) -> list[dict]:
    """
    Extract structured eligibility factors comparing user input against scheme constraints.
    """
    factors = []
    
    # 1. Income matching
    user_income = user_input.get("income_level")
    scheme_income = str(scheme_row.get("income_category", "")).strip().lower()
    if user_income and scheme_income and scheme_income != "not specified" and scheme_income != "nan":
        if user_income.lower() == scheme_income.lower():
            factors.append({
                "factor": "income_match",
                "value": user_income.lower(),
                "threshold": scheme_income
            })
            
    # 2. Age constraints
    user_age = user_input.get("age")
    min_age = scheme_row.get("min_age")
    max_age = scheme_row.get("max_age")
    
    if user_age is not None:
        try:
            if pd.notna(min_age) and str(min_age).strip().lower() not in ["", "not specified"]:
                if float(user_age) >= float(min_age):
                    factors.append({
                        "factor": "age_above_minimum",
                        "value": float(user_age),
                        "threshold": float(min_age)
                    })
            if pd.notna(max_age) and str(max_age).strip().lower() not in ["", "not specified"]:
                if float(user_age) <= float(max_age):
                    factors.append({
                        "factor": "age_below_maximum",
                        "value": float(user_age),
                        "threshold": float(max_age)
                    })
        except (ValueError, TypeError):
            pass # Skip if age is non-numeric somehow
                
    # 3. Rural/Urban matching
    user_ru = str(user_input.get("rural_urban", "")).strip().lower()
    re_ = str(scheme_row.get("rural_eligible", "")).strip().lower()
    ue_ = str(scheme_row.get("urban_eligible", "")).strip().lower()
    
    if user_ru == "rural" and re_ in ["yes", "both"]:
        factors.append({
            "factor": "rural_residency_match",
            "value": "rural",
            "threshold": "rural"
        })
    elif user_ru == "urban" and ue_ in ["yes", "both"]:
        factors.append({
            "factor": "urban_residency_match",
            "value": "urban",
            "threshold": "urban"
        })
        
    return factors

def extract_risk_factors(user_input: dict) -> list[dict]:
    """
    Extract structured risk factors based on user friction indicators.
    """
    factors = []
    
    digital_access = str(user_input.get("digital_access", "")).strip().lower()
    docs = user_input.get("document_completeness")
    inst_dep = str(user_input.get("institutional_dependency", "")).strip().lower()
    literacy = str(user_input.get("literacy_level", "")).strip().lower()
    
    if digital_access in ["none", "limited", "low"]:
        factors.append({
            "factor": "low_digital_access",
            "value": digital_access
        })
        
    if docs is not None:
        try:
            if float(docs) < 0.5:
                factors.append({
                    "factor": "missing_documents",
                    "value": float(docs)
                })
        except (ValueError, TypeError):
            if str(docs).strip().lower() in ["low", "none", "incomplete", "poor"]:
                 factors.append({
                    "factor": "missing_documents",
                    "value": str(docs).strip().lower()
                })
                
    if inst_dep == "high":
        factors.append({
            "factor": "high_institutional_dependency",
            "value": "high"
        })
        
    if literacy in ["low", "none"]:
        factors.append({
            "factor": "low_literacy_awareness",
            "value": literacy
        })
        
    return factors

def build_input_snapshot(user_input: dict) -> dict:
    """
    Return a curated subset of user_input.
    """
    relevant_keys = {
        "age", "gender", "rural_urban", "income_level", "occupation",
        "education_level", "literacy_level", "digital_access", 
        "document_completeness", "institutional_dependency", 
        "student_status", "farmer_status", "disability_status"
    }
    return {k: v for k, v in user_input.items() if k in relevant_keys and v is not None}
