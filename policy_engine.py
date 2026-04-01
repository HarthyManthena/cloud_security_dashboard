def enforce_policy(risk, score):
    if risk == 1 and score < 15:
        return "CRITICAL: Block Access + Force MFA + Alert Admin"

    elif risk == 1:
        return "High Risk: Require MFA + Log Activity"

    else:
        return "Low Risk: Access Granted"