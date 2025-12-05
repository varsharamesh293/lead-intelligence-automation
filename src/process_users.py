import time
import json
import os
from dotenv import load_dotenv

# Import your modules
from data_cleaner import clean_csv
from gemini_api import configure_gemini, analyze_user_and_comment
from utils import assign_team

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

INPUT_CSV = os.getenv("INPUT_CSV")
CLEANED_CSV = os.getenv("CLEANED_CSV")
OUTPUT_CSV = os.getenv("OUTPUT_CSV")
OUTPUT_JSON = os.getenv("OUTPUT_JSON")

# -----------------------------
# Main pipeline
# -----------------------------
def main():
    df = clean_csv(INPUT_CSV, CLEANED_CSV)
    print("CSV cleaned successfully!")

    df["persona_type"] = ""
    df["urgency"] = ""
    df["assigned_team"] = ""
    df["summary"] = ""

    model = configure_gemini(API_KEY, MODEL_NAME)

    # Process each row
    for i, row in df.iterrows():
        role = row["job_title"]
        comment = row["comment"]

        # Call Gemini API
        persona, urgency, summary = analyze_user_and_comment(model, role, comment)

        print("Response:", persona, urgency, summary)

        # Update DataFrame
        df.at[i, "persona_type"] = persona
        df.at[i, "urgency"] = urgency
        df.at[i, "assigned_team"] = assign_team(persona, urgency)
        df.at[i, "summary"] = summary


    # Save outputs
    df.to_csv(OUTPUT_CSV, index=False)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, indent=4, ensure_ascii=False)

    print(f"Processing complete. Saved to {OUTPUT_CSV} and {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
