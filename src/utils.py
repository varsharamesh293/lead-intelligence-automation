import re, json

def assign_team(user_type: str, urgency: str) -> str:
    """
    Assign team based on persona_type and urgency
    
    """
    if urgency.lower() == "high" and user_type.lower() == "decision maker":
        return "Strategic sales"
    elif urgency.lower() == "high" and user_type.lower() == "practitioner":
        return "Enterprise sales"
    elif urgency.lower() == "medium":
        return "Sales development"
    elif urgency.lower() == "low":
        return "Nurture Campaign"
    else:
        return "NA"
