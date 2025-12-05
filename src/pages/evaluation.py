import streamlit as st
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
import tempfile

st.set_page_config(page_title="LeadRouter AI - Evaluation")
st.title("LeadRouter AI - Model Evaluation")

st.markdown("Upload your **Ground Truth CSV** and **Predicted CSV** for evaluation.")

# ---------------- Helper: Clean CSV ----------------
def clean_csv(file) -> pd.DataFrame:
    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8", suffix=".csv") as tmp:
        temp_path = tmp.name
        lines = file.read().decode("utf-8-sig").splitlines()
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
            line = line.replace('""', '"')
            cleaned_lines.append(line + "\n")
        tmp.writelines(cleaned_lines)
    df = pd.read_csv(temp_path)
    df.columns = df.columns.str.strip().str.lower().str.replace('"','')
    return df

# ---------------- Upload ----------------
truth_file = st.file_uploader("Ground Truth CSV", type=["csv"])
pred_file = st.file_uploader("Predicted CSV", type=["csv"])

if truth_file and pred_file:
    df_truth = clean_csv(truth_file)
    df_pred = clean_csv(pred_file)

    # Keep only needed columns (adjust names as per CSV)
    df_eval = pd.merge(
        df_truth[['email','persona_type_label','urgency_label','assigned_team_label']].rename(
            columns={'persona_type_label':'persona_type_true',
                     'urgency_label':'urgency_true',
                     'assigned_team_label':'assigned_team_true'}),
        df_pred[['email','persona_type','urgency','assigned_team']].rename(
            columns={'persona_type':'persona_type_pred',
                     'urgency':'urgency_pred',
                     'assigned_team':'assigned_team_pred'}),
        on="email"
    )

    if df_eval.empty:
        st.error("No matching emails found.")
        st.stop()

    for col in ['persona_type_true', 'persona_type_pred',
            'urgency_true', 'urgency_pred',
            'assigned_team_true', 'assigned_team_pred']:
        df_eval[col] = df_eval[col].astype(str).str.lower().str.strip()

        
    # ---------------- Accuracy ----------------
    persona_acc = accuracy_score(df_eval['persona_type_true'], df_eval['persona_type_pred'])
    urgency_acc = accuracy_score(df_eval['urgency_true'], df_eval['urgency_pred'])
    team_acc = accuracy_score(df_eval['assigned_team_true'], df_eval['assigned_team_pred'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Persona Accuracy", f"{persona_acc:.2%}")
    col2.metric("Urgency Accuracy", f"{urgency_acc:.2%}")
    col3.metric("Assigned Team Accuracy", f"{team_acc:.2%}")

    # ---------------- Precision ----------------
    report = classification_report(df_eval['assigned_team_true'], df_eval['assigned_team_pred'], output_dict=True, zero_division=0)
    df_precision = pd.DataFrame(report).transpose()[['precision']].drop(['accuracy','macro avg','weighted avg'], errors='ignore')
    df_precision['precision'] = df_precision['precision'].apply(lambda x: f"{x:.2%}")
    st.subheader("Precision by Assigned Team")
    st.dataframe(df_precision.style.background_gradient(cmap="Greens"), width='content', height=min(300,50*len(df_precision)))

    # ---------------- Routing Summary ----------------
    correct = (df_eval['assigned_team_true'] == df_eval['assigned_team_pred']).sum()
    total = len(df_eval)
    st.subheader("Routing Summary")
    st.write(f"Correctly Routed: **{correct} of {total}** ({correct/total:.2%})")
    st.write(f"Misrouted: **{total - correct}**")

    # ---------------- Download ----------------
    st.subheader("Download Evaluation CSV")
    csv = df_eval.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "evaluation_results.csv", "text/csv")
