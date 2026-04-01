def enforce_policy(risk, score, confidence):

    if risk == 1 and confidence > 0.85:
        return "CRITICAL: Block Access + Notify SOC"

    elif risk == 1 and score < 15:
        return "HIGH RISK: Enforce MFA + Security Audit"

    elif risk == 1:
        return "Medium Risk: Continuous Monitoring"

    else:
        return "Low Risk: Access Granted"