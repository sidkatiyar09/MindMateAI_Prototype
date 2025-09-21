@echo off
echo Activating venv...
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
echo Starting Streamlit app...
streamlit run app.py
