import google.generativeai as genai
import json,re
import time

def configure_gemini(api_key: str, model_name: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)

def update_prompt(role:str, comment:str):
    prompt = f"""
You are an assistant who helps in analysing user's role and their comment to categorise them into particular segments following the rules below.
role : {role}
comment:{comment}
### Rules for identifying the persona type of the role :
- Understand the role and analyse the responsibilities of the role.
- Basis the analysis, classify the role into one of three categories:
    - "Decision Maker" - Roles with authority to approve budgets, make strategic decisions, or manage teams (e.g., CEO, Manager, Director, VP).
    - "Practitioner" - Roles focused on executing tasks, processes, or technical work (e.g., Engineer, Analyst, Developer, Accountant).
    - "Other" - Roles that do not clearly fit as decision makers or practitioners, such as students, researchers, interns, or miscellaneous roles.
### Rules for identifying the urgency of the comment :
- Understand the urgency of comment in a business context.
- Classify the following comment into one of three urgency levels:
    - "High" - Requires immediate attention, critical impact, or time-sensitive action.
    - "Medium" - Important but not urgent, should be addressed in a reasonable timeframe.
    - "Low" - Routine, informational, or can wait without major consequences.
### Rules for generating a summary from the comment
- Understand what the comment says and wants.
- Summarize the following comment in one clear sentence, focusing on what the comment is about and the action item. 
- Do NOT mention the person who wrote it.

---
 ###Few Shot Examples
 {
    {
      "role": "Software Engineer",
      "message": "The server crashed and the client portal is down. We need a fix ASAP.",
      "Persona": "Practitioner",
      "Urgency": "High",
      "Reasoning": "Role is technical and execution-focused; message describes critical system outage."
    },
    {
      "role": "Marketing Director",
      "message": "I suggest we increase the marketing budget by 20% next quarter to boost lead generation.",
      "Persona": "Decision Maker",
      "Urgency": "Medium",
      "Reasoning": "Role manages strategy and budget; message is important but not immediate."
    },
    {
      "role": "Intern",
      "message": "Can someone explain how to use the new reporting dashboard?",
      "Persona": "Other",
      "Urgency": "Low",
      "Reasoning": "Role is a trainee/learner; message is informational with no immediate consequence."
    },
    {
      "role": "Finance Manager",
      "message": "Please review the quarterly financial report and provide your feedback by next Friday.",
      "Persona": "Decision Maker",
      "Urgency": "Medium",
      "Reasoning": "Role involves oversight and decision authority; deadline is reasonable, not urgent."
    }
 }
---
Note : Answer **only** using the provided categories. Do not assume anything external.Analyze the message content to determine urgency. Consider the potential impact of delayed action."
---
### Response Format
Return only valid JSON. Do not include explanations, extra text, or markdown.
The JSON must strictly follow this format:
  {{
       "persona_type": "Identified persona type",
       "urgency": "Identified level of urgency",
       "summary": "Generated summary for the comment"
    }}
"""
    return prompt

def analyze_user_and_comment(model, role: str, comment: str, retries=3):
    """ Gemini call to identify persona type and urgency. """
    prompt = update_prompt(role, comment)

    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            print(response)

            raw_text = response.candidates[0].content.parts[0].text or ""

            json_match = re.search(r"\{.*\}", raw_text, flags=re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in model response")

            clean_text = json_match.group(0).strip()

            result = json.loads(clean_text)

            return (
                result.get("persona_type", ""),
                result.get("urgency", ""),
                result.get("summary", ""),
            )

        except Exception as e:
            print(f"Attempt {attempt+1}/{retries} failed: {e}") 
            time.sleep(2)

    return "fail", "fail", "fail"


