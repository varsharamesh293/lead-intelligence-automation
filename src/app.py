import streamlit as st
import pandas as pd
import json
import time , os
from gemini_api import analyze_user_and_comment, configure_gemini
from utils import assign_team
from data_cleaner import clean_csv
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

st.set_page_config(page_title="Persona Analyzer", layout="wide")
st.title("LeadRouter AI")

uploaded_file = st.file_uploader("Upload CSV with job_title and comment columns", type=["csv"])

if uploaded_file is not None:

    # Save uploaded file temporarily
    temp_path = "uploaded_temp.csv"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    df = clean_csv(temp_path, "cleaned_temp.csv")
    st.success("CSV cleaned successfully.")

    st.subheader("Preview of Cleaned Data")
    st.dataframe(df.head())

    st.info("Processing may take some time because the Gemini Free Tier has request and rate limits. Please keep this page open during processing.")


    if "processed_df" not in st.session_state:
        if st.button("Start Processing"):

            df["persona_type"] = ""
            df["urgency"] = ""
            df["assigned_team"] = ""
            df["summary"] = ""

            model = configure_gemini(API_KEY, MODEL_NAME)

            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, row in df.iterrows():
                persona, urgency, summary = analyze_user_and_comment(
                    model, row["job_title"], row["comment"]
                )

                df.at[i, "persona_type"] = persona
                df.at[i, "urgency"] = urgency
                df.at[i, "assigned_team"] = assign_team(persona, urgency)
                df.at[i, "summary"] = summary

                progress_bar.progress((i + 1) / len(df))
                status_text.text(f"Processing row {i + 1}/{len(df)} ...")

                time.sleep(1)

            st.session_state.processed_df = df.copy()
            st.rerun()

    if "processed_df" in st.session_state:
        st.success("Processing Completed.")
        st.subheader("Final Output")
        st.dataframe(st.session_state.processed_df)

        csv_output = st.session_state.processed_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            csv_output,
            "processed_output.csv",
            "text/csv"
        )

        json_output = st.session_state.processed_df.to_json(orient="records", indent=4)
        st.download_button(
            "Download JSON",
            json_output,
            "processed_output.json",
            "application/json"
        )
