# Dark Web Threat Intelligence Platform

## ⚠ IMPORTANT DISCLAIMER
*This project is designed to work ONLY with the custom-built simulated dark web environment created specifically for testing purposes. DO NOT attempt to use this tool with actual dark web sites or .onion URLs, as this could be illegal, dangerous, and expose your systems to malicious content. The developers take no responsibility for any misuse of this software.*

## Overview
This AI-powered Dark Web Threat Intelligence Platform combines OSINT techniques with advanced NLP to monitor and analyze potential threats on the dark web. The system proactively detects references to registered users and organizations in dark web forums and marketplaces, providing early warnings of potential cyber threats before they escalate.

### 🌐 *Our Own Dark Web Environment*
We have developed our own simulated dark web environment for safe testing and demonstration purposes. This ensures:
- A controlled and secure space for evaluating threat detection capabilities.
- No legal or ethical concerns associated with accessing the actual dark web.
- A safe educational platform for cybersecurity research.

## Features
✅ *Automated Dark Web Scraping* – Collects data from our simulated dark web environment.  
✅ *User Reference Monitoring* – Detects mentions of registered users' information in scraped content.  
✅ *Real-Time Alerts* – Generates alerts when potential threats are identified.  
✅ *Interactive Dashboard* – Visualizes threats and explores data via a Streamlit interface.  
✅ *Risk Assessment* – Categorizes threats by risk level with recommended actions.  
✅ *Periodic Scanning* – Continuously monitors for new threats at configurable intervals.  

## Project Structure

dark-web-threat-intel/
├── app.py                    # Backend for the threat detection system
├── steam.py                  # Streamlit dashboard for threat visualization
├── alert_system.py           # LLM-powered alert generation system
├── threat_intel_data/        # Data directory
│   ├── registered_users.json # Registered user information
│   ├── threat_intel_*.json   # Scraped threat intelligence data
│   └── alerts_*.json         # Generated alerts
└── requirements.txt          # Project dependencies


## Installation

### 1️⃣ Clone the repository
bash
 git clone https://github.com/yourusername/dark-web-threat-intel.git && cd dark-web-threat-intel


### 2️⃣ Install dependencies
bash
pip install -r requirements.txt


### 3️⃣ Set up your Groq API key
python
# In alert_system.py
llm = ChatGroq(api_key="your_groq_api_key", model="gemma2-9b-it")


### 4️⃣ Update file paths in the Python files to match your system.

## Usage

### Running the Application

*Start the backend application:*
bash
python app.py

This initiates the core backend system for threat detection.

*Launch the Streamlit dashboard:*
bash
streamlit run steam.py

This opens the interactive dashboard in your browser to visualize threat intelligence.

### Running the Alert System
bash
python alert_system.py

This starts the alert system that periodically checks for mentions of registered users in scraped dark web data. By default, it checks every *3 hours*.

## How It Works

1️⃣ *Data Collection* – The system scrapes data from our simulated dark web environment, storing it in JSON files.  
2️⃣ *LLM Analysis* – The content is analyzed using the Groq LLM (Gemma2-9b-it) to detect references to registered users.  
3️⃣ *Alert Generation* – When a user reference is found, an alert is generated with a detailed analysis.  
4️⃣ *Visualization* – The Streamlit dashboard (steam.py) provides an intuitive interface to explore and analyze threats.  

## Dashboard Features
📊 Overview metrics of detected threats and alerts.  
🔍 Search functionality by source, target, or keyword.  
📅 Date filtering for historical analysis.  
⚠ Detailed threat information with risk levels and recommended actions.  

## Customization

### Adjusting Scan Frequency
Modify the scan interval in alert_system.py to change how often it checks for threats:
python
time.sleep(10800)  # Default: 3 hours (10800 seconds)


### Adding Users to Monitor
Update registered_users.json with additional users:
json
{
    "user_id": 7,
    "username": "new_user",
    "email": "new.user@email.com",
    "alias": "new_user_alias"
}


## Security Considerations

🔒 Store API keys securely and *never* commit them to version control.  
📌 Regularly update the registered users list as personnel change.  
🛡 Review alerts promptly and implement recommended security actions.  
🕵 Consider using a VPN or secure tunnel when deploying.  
🚫 *NEVER attempt to use this tool with actual dark web sites or services.*  

## Future Enhancements

🚀 Integration with *SIEM systems* for centralized monitoring.  
📧 Email notifications for critical alerts.  
📈 Advanced *machine learning models* for improved threat classification.  
🔐 *User authentication* for dashboard security.  
📊 Historic trend analysis & reporting.  
