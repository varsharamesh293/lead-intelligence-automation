## Lead Intelligence Automation

1. **Business Summary**

    This project automates the classification and analysis of incoming leads and their user comments through the "Contact Us" of the website using Google Gemini AI.<br>
    Manually reviewing leads to understand who the user is, how urgent the request is, and what action is needed is time-consuming and inconsistent.
    This automation solves that problem by:
        - Automatically identifying whether the lead is a Decision Maker, Practitioner, or Other.
        - Assessing the urgency of each comment as High, Medium, or Low.
        - Generating a concise summary of what the lead wants.
        - Assigning the lead to the correct internal team.
    Business Value:
        - Saves manual triage time (can save several hours per week depending on lead volume)
        - Improves lead routing accuracy and follow-up prioritization
        - Ensures consistent classification across all leads
        - Creates structured output (CSV + JSON) ready for CRM ingestion
        - Non-technical teams can monitor results through an interactive Streamlit dashboard



2. **How It Works** (High-Level Overview)

    The script reads a raw CSV file containing email, job title, and comment.
    The CSV is cleaned and standardized.
    For each row:
    A prompt is created based on the job title and comment.
    The Gemini model analyzes:
        - The persona type
        - The urgency
        - The summary
    Output is appended to the dataset.
    Leads are automatically mapped to an internal team based on persona + urgency.
    Final results are exported as both CSV and JSON.

3. **Technical Deep Dive**

Architecture
The project follows a modular structure:

    project/
    │
    ├── .env                      # Environment variables
    ├── requirements.txt
    ├── src/
    │   ├── process_users.py      # Main pipeline
    │   ├── data_cleaner.py       # CSV cleaning helper
    │   ├── gemini_api.py         # Gemini API + prompt logic
    │   ├── utils.py              # Shared helper functions
    |   ├── app.py                # streamlit main page
    |   ├── pages
    |   |    ├── evaluate.py      # evaluate page
    │   ├── __init__.py
    │
    └── data/
        ├── raw/                  # Original CSVs
        ├── cleaned/              # Reformatted data
        └── output/               # Final CSV + JSON

Prompt Engineering Approach

    The prompt is designed to enforce structure and ensure Gemini returns machine-parsable JSON. Key choices:

        - Instructions force Gemini to use only allowed categories for persona & urgency.
        - Clear rules describe the boundaries for Decision Maker, Practitioner, and Other.
        - Summary must be strictly one sentence, and must not mention the requester.
        - Response is required to follow JSON format with no extra text.
        - The script automatically removes Markdown (e.g., ```json blocks) before parsing.
        - This ensures high accuracy and consistent formatting.

API Usage

    Uses generate_content() from the Gemini 2.0 Flash model.
    Extracts text via response.candidates[0].content.parts[0].text.
    Includes retry logic for malformed JSON or temporary API failures.

4. **Setup & Run Instructions (Backend)**

    1. Install Python (recommended 3.10 or above)
    Because some Google packages are not fully compatible with Python 3.9.

    2. Create a virtual environment
    python -m venv .venv

    Activate it:
    Windows
    .\.venv\Scripts\activate

    3. Install dependencies
    pip install -r requirements.txt

    4. Add your environment variables

    Create a .env file in the project root:

        API_KEY=your_google_api_key
        MODEL_NAME=your_google_model_name
        INPUT_CSV=data/raw/leads.csv
        CLEANED_CSV=data/cleaned/cleaned_leads.csv
        OUTPUT_CSV=data/output/classified_output.csv
        OUTPUT_JSON=data/output/classified_output.json

    5. Place your CSV file

    Put your raw CSV under: data/raw/

    6. Run the script

    From the project root: python src/process_users.py
    To run through the streamlit application : streamlit run python src/app.py

    7. Results

    Processed output will appear in:
        data/output/classified_output.csv
        data/output/classified_output.json

5. **Future Improvements**

    1. Batch API Calls over Real time API
    Why it matters:
    
    Right now, the script sends one API request per lead.
    If you have 500 leads, that becomes 500 network calls - slow and expensive.

    Improvement:
    Use Gemini’s batch generation API, which allows to send many requests together in a single payload.
    For example:
        Send 20-50 leads in one request
        Gemini processes them together and returns 20–50 outputs
        You distribute the results back to the rows

    Benefits:
        Lower cost - Large batch requests are significantly more efficient than many small ones.
        Much faster - Fewer network round-trips → faster processing.
        Scalable - Can handle thousands of leads for large datasets.
        More robust - Fewer requests = fewer timeouts, fewer rate-limit issues.

    In practice:
        Instead of calling model.generate_content() inside a loop, you create a list of separate prompts and send them all in a single batch call.
        Gemini returns an array of responses in the same order.

    This is the preferred approach for production-scale workloads.

    2. Integration with CRM

    Right now, the AI-processed leads are saved into CSV/JSON files.
    A real business workflow normally requires these leads to flow directly into a CRM or work management system used by sales and operations teams.

    Instead of manually importing the output, the script would automatically push each processed lead into platforms like:
        Salesforce - using REST API, Bulk API, or the Salesforce Python SDK
        HubSpot - using the Contacts/CRM API
        Monday.com - using Monday’s GraphQL API to insert items into boards
        Other CRMs (Zoho, Dynamics 365, Pipedrive, etc.)
    This makes the lead classification system part of a complete end-to-end automation pipeline.

    Business Benefits:

    1. No manual uploads or Excel handling
        Leads go straight from raw CSV -> AI -> CRM -> ready for sales.
        Faster lead response times
        
        Example:
            High urgency + Decision Maker -> routed instantly to Priority Sales Board.

        Higher lead conversion :
            The right team acts quickly because routing is automated.

    2. Consistent data quality
        Persona type, urgency, and summary are standardized before entering CRM.

    3. Real-time dashboards
        CRMs like Salesforce and Monday.com can instantly visualize:
            Lead volumes, Urgency breakdown, Team allocation, Trends over time
