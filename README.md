# Sales Data Analytics Dashboard

## Requirements
- Python 3
- VS Code

## Setup on macOS
1. Open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Create a virtual environment:
   `python3 -m venv venv`
4. Activate it:
   `source venv/bin/activate`
5. Install dependencies:
   `pip install -r requirements.txt`
6. Start the app:
   `streamlit run app.py`
7. Open the local URL shown in the terminal (usually http://localhost:8501).

## Use
- Upload a CSV or Excel (.xlsx) file in the sidebar.
- Select the columns that represent sales, dates, products, regions, categories, quantities and order IDs.
- Review the metrics and charts.
- Ask supported questions in the question box.

## Notes
The included `sales_data.csv` is sample data for testing. The question-answering feature uses simple keyword/rule matching, not a generative AI model. For real datasets, verify that sales values are numeric and that each row represents the intended sales record.
