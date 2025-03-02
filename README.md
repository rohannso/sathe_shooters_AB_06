# Dark Web Threat Intelligence Platform

## ⚠ IMPORTANT DISCLAIMER
*This project is designed to work ONLY with the custom-built simulated dark web environment created specifically for testing purposes. DO NOT attempt to use this tool with actual dark web sites or .onion URLs, as this could be illegal, dangerous, and expose your systems to malicious content. The developers take no responsibility for any misuse of this software.*

---

## Overview
This AI-powered Dark Web Threat Intelligence Platform combines OSINT techniques with advanced NLP to monitor and analyze potential threats on the dark web. The system proactively detects references to registered users and organizations in dark web forums and marketplaces, providing early warnings of potential cyber threats before they escalate.

## Features
✅ *Automated Dark Web Scraping* - Collects data from simulated dark web environments  
✅ *User Reference Monitoring* - Detects mentions of registered users' information in scraped content  
✅ *Real-Time Alerts* - Generates alerts when potential threats are identified  
✅ *Interactive Dashboard* - Visualize threats and explore data through a Streamlit interface  
✅ *Risk Assessment* - Categorizes threats by risk level with recommended actions  
✅ *Periodic Scanning* - Continuously monitors for new threats at configurable intervals  

---

## 📂 Project Structure

dark-web-threat-intel/
├── app.py                    # Backend for the threat detection system
├── steam.py                  # Streamlit dashboard for threat visualization
├── alert_system.py           # LLM-powered alert generation system
├── threat_intel_data/        # Data directory
│   ├── registered_users.json # Registered user information
│   ├── threat_intel_*.json   # Scraped threat intelligence data
│   └── alerts_*.json         # Generated alerts
└── requirements.txt          # Project dependencies


---

## 🚀 Installation

### 1️⃣ Clone the repository
bash
 git clone https://github.com/yourusername/dark-web-threat-intel.git && cd dark-web-threat-intel


### 2️⃣ Install dependencies
bash
 pip install -r requirements.txt


### 3️⃣ Set up your Groq API key
Edit alert_system.py and replace your_groq_api_key with your actual API key:
python
llm = ChatGroq(api_key="your_groq_api_key", model="gemma2-9b-it")


### 4️⃣ Update file paths in the Python files to match your system.

---

## 🔧 Usage

### Running the Backend
bash
 python app.py

This initiates the core backend system for threat detection.

### Launching the Streamlit Dashboard
bash
 streamlit run steam.py

This opens the interactive threat intelligence dashboard in your web browser.

### Running the Alert System
bash
 python alert_system.py

This starts the alert system, which checks for mentions of registered users in the scraped dark web data every 3 hours.

---

## 🔍 Simulated Dark Web Environment
This project uses a custom-built simulated dark web environment for testing and demonstration purposes. This approach:
- Eliminates legal and ethical concerns associated with actual dark web access
- Provides a controlled environment for testing the system's capabilities
- Allows for safe demonstration and educational purposes
- Prevents accidental exposure to malicious content or illegal activities

*Under no circumstances should this tool be modified to scrape or interact with actual dark web sites.*

---

## 🛠 How It Works

1. *Data Collection* - The system collects data from the simulated dark web environment and stores it in JSON files.
2. *LLM Analysis* - Content is analyzed using the Groq LLM (Gemma2-9b-it) to detect references to registered users.
3. *Alert Generation* - Alerts are created when user references are found.
4. *Visualization* - The Streamlit dashboard provides a user-friendly interface to explore threat data.

---

## 📊 Dashboard Features
✔ *Overview metrics* - Track detected threats and alerts  
✔ *Search functionality* - Filter by source, target, or keyword  
✔ *Date filtering* - Analyze historical threats  
✔ *Risk levels & recommendations* - Understand the severity and next steps  

---

## 🔧 Customization

### Adjusting Scan Frequency
Modify the sleep duration in alert_system.py to change how often the system checks for new threats:
python
time.sleep(10800)  # Default: 3 hours (10800 seconds)


### Adding Users to Monitor
Update the registered_users.json file to include additional users:
json
{
    "user_id": 7,
    "username": "new_user",
    "email": "new.user@email.com",
    "alias": "new_user_alias"
}


---

## 🔒 Security Considerations
- *Store API keys securely* and never commit them to version control.
- *Regularly update the registered users list* to reflect personnel changes.
- *Review alerts promptly* and take recommended security actions.
- *Use a VPN or Tor* when deploying in production environments.
- *NEVER attempt to use this tool with actual dark web sites or services.*

---

## 🔮 Future Enhancements
🔹 Integration with SIEM systems for centralized security monitoring  
🔹 Expanded simulated dark web environment for testing  
🔹 Machine learning models for improved threat classification  
🔹 Email notifications for critical alerts  
🔹 User authentication for the dashboard  
🔹 Historic trend analysis and reporting  



link of demo video
https://drive.google.com/file/d/1J1nus31sf2sn6fFVjqFtYN5Pm93E0uFM/view?usp=drive_link