## Lead Intelligence Automation

1. **Business Summary**

    This project automates the classification and analysis of incoming leads and their user comments through the "Contact Us" of the website using Google Gemini AI.<br>
    Manually reviewing leads to understand who the user is, how urgent the request is, and what action is needed is time-consuming and inconsistent.<br>
    This automation solves that problem by:<br>
       - Automatically identifying whether the lead is a Decision Maker, Practitioner, or Other.<br>
        - Assessing the urgency of each comment as High, Medium, or Low.<br>
        - Generating a concise summary of what the lead wants.<br>
        - Assigning the lead to the correct internal team.<br>
    Business Value:<br>
        - Saves manual triage time (can save several hours per week depending on lead volume)<br>
        - Improves lead routing accuracy and follow-up prioritization<br>
        - Ensures consistent classification across all leads<br>
        - Creates structured output (CSV + JSON) ready for CRM ingestion<br>
        - Non-technical teams can monitor results through an interactive Streamlit dashboard<br>

___

2. **How It Works** (High-Level Overview)

    The script reads a raw CSV file containing email, job title, and comment.<br>
    The CSV is cleaned and standardized.<br>
    For each row:<br>
    A prompt is created based on the job title and comment.<br>
    The Gemini model analyzes:<br>
        - The persona type<br>
        - The urgency<br>
        - The summary<br>
    Output is appended to the dataset.<br>
    Leads are automatically mapped to an internal team based on persona + urgency.<br>
    Final results are exported as both CSV and JSON.<br>

___

3. **Technical Deep Dive**

Architecture<br>
The project follows a modular structure:<br>

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

Prompt Engineering Approach<br>

    The prompt is designed to enforce structure and ensure Gemini returns machine-parsable JSON. Key choices:

        - Instructions force Gemini to use only allowed categories for persona & urgency.
        - Clear rules describe the boundaries for Decision Maker, Practitioner, and Other.
        - Summary must be strictly one sentence, and must not mention the requester.
        - Response is required to follow JSON format with no extra text.
        - The script automatically removes Markdown (e.g., ```json blocks) before parsing.
        - This ensures high accuracy and consistent formatting.

API Usage<br>

    Uses generate_content() from the Gemini 2.0 Flash model.<br>
    Extracts text via response.candidates[0].content.parts[0].text.<br>
    Includes retry logic for malformed JSON or temporary API failures.<br>

___

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

        From the project root: python src/process_users.py<br>
        To run through the streamlit application : streamlit run python src/app.py

    7. Results

        Processed output will appear in:
            data/output/classified_output.csv
            data/output/classified_output.json

___

5. **Future Improvements**

    1. Batch API Calls over Real time API
        Why it matters:<br>
        
        Right now, the script sends one API request per lead.<br>
        If you have 500 leads, that becomes 500 network calls - slow and expensive.<br>
    
        Improvement:<br>
        Use Gemini’s batch generation API, which allows to send many requests together in a single payload.<br>
        For example:<br>
            Send 20-50 leads in one request<br>
            Gemini processes them together and returns 20–50 outputs<br>
            You distribute the results back to the rows<br>
    
        Benefits:<br>
            Lower cost - Large batch requests are significantly more efficient than many small ones.<br>
            Much faster - Fewer network round-trips → faster processing.<br>
            Scalable - Can handle thousands of leads for large datasets.<br>
            More robust - Fewer requests = fewer timeouts, fewer rate-limit issues.<br>
    
        In practice:<br>
            Instead of calling model.generate_content() inside a loop, you create a list of separate prompts and send them all in a single batch call.<br>
            Gemini returns an array of responses in the same order.<br>
    
        This is the preferred approach for production-scale workloads.<br>

    2. Integration with CRM

        Right now, the AI-processed leads are saved into CSV/JSON files.<br>
        A real business workflow normally requires these leads to flow directly into a CRM or work management system used by sales and operations teams.<br>
    
        Instead of manually importing the output, the script would automatically push each processed lead into platforms like:<br>
            Salesforce - using REST API, Bulk API, or the Salesforce Python SDK<br>
            HubSpot - using the Contacts/CRM API<br>
            Monday.com - using Monday’s GraphQL API to insert items into boards<br>
            Other CRMs (Zoho, Dynamics 365, Pipedrive, etc.)<br>
        This makes the lead classification system part of a complete end-to-end automation pipeline.<br>
    
        Business Benefits:<br>
    
        1. No manual uploads or Excel handling
            Leads go straight from raw CSV -> AI -> CRM -> ready for sales.<br>
            Faster lead response times<br>
            
            Example:<br>
                High urgency + Decision Maker -> routed instantly to Priority Sales Board.<br>
    
            Higher lead conversion :<br>
                The right team acts quickly because routing is automated.<br>
    
        2. Consistent data quality
            Persona type, urgency, and summary are standardized before entering CRM.<br>
    
        3. Real-time dashboards
            CRMs like Salesforce and Monday.com can instantly visualize:<br>
                Lead volumes, Urgency breakdown, Team allocation, Trends over time<br>
