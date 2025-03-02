import streamlit as st
import json
import pandas as pd
import os
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Threat Intelligence Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Path configuration
THREAT_INTEL_PATH = r"C:\Users\Vaibhav Vikhe Patil\hackthon\threat_intel_data"

# Data loading functions
def load_threat_intel_data():
    all_data = []
    try:
        # Get all JSON files in the folder
        for filename in os.listdir(THREAT_INTEL_PATH):
            if filename.startswith("threat_intel_") and filename.endswith(".json"):
                file_path = os.path.join(THREAT_INTEL_PATH, filename)
                try:
                    with open(file_path, "r") as file:
                        data = json.load(file)
                        # Add source file information
                        if isinstance(data, list):
                            all_data.extend(data)
                        else:
                            all_data.append(data)
                except Exception as e:
                    st.error(f"Error loading {filename}: {e}")
        return all_data
    except Exception as e:
        st.error(f"Error loading threat intelligence data: {e}")
        return []

def load_alerts():
    alerts = []
    try:
        # Get all alert log files
        for filename in os.listdir(THREAT_INTEL_PATH):
            if filename.startswith("alerts_") and filename.endswith(".json"):
                file_path = os.path.join(THREAT_INTEL_PATH, filename)
                try:
                    with open(file_path, "r") as file:
                        alerts_data = json.load(file)
                        alerts.extend(alerts_data)
                except Exception as e:
                    st.error(f"Error loading alerts from {filename}: {e}")
        return alerts
    except Exception as e:
        st.error(f"Error loading alerts: {e}")
        return []

# Dashboard components
def display_threat_dashboard():
    st.title("🛡️ Threat Intelligence Dashboard")
    
    # Load data
    threat_data = load_threat_intel_data()
    alerts = load_alerts()
    
    # Display simple metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Threats Detected", len(threat_data))
    with col2:
        st.metric("Total Alerts", len(alerts))
    
    # Search functionality
    st.header("Search Threats")
    search_term = st.text_input("Search by Source, Target, or Keyword", "")
    date_filter = st.date_input("Filter by Date", [])

    # Filter based on search term
    filtered_threats = []
    for item in threat_data:
        source = item.get("source", "")
        target = item.get("target", "")
        data_type = item.get("data_type", "")
        
        # Convert to string if not already a string
        source = str(source) if source is not None else ""
        target = str(target) if target is not None else ""
        data_type = str(data_type) if data_type is not None else ""
        
        if search_term.lower() in source.lower() or search_term.lower() in target.lower() or search_term.lower() in data_type.lower():
            filtered_threats.append(item)
    
    # Filter by date if selected
    if date_filter:
        start_date = date_filter[0]
        end_date = date_filter[1] if len(date_filter) > 1 else start_date
        filtered_threats = [
            item for item in filtered_threats 
            if start_date <= datetime.fromisoformat(item.get("date_collected", "")).date() <= end_date
        ]

    # Display filtered threats
    st.header("Filtered Threats")
    if filtered_threats:
        threat_data_display = []
        for item in filtered_threats:
            try:
                # Parse date
                date_str = item.get("date_collected", "Unknown")
                if date_str and date_str != "Unknown":
                    date = datetime.fromisoformat(date_str.split("+")[0])
                    date_str = date.strftime("%Y-%m-%d")
                
                # Extract source
                source = item.get("source", "Unknown")
                if not source or source == "Unknown":
                    source = item.get("url", "Unknown Source")
                
                # Extract target (ensure it's a string)
                target = str(item.get("target", "Unknown target"))
                
                # Determine risk level
                risk_level = item.get("risk_level", "Medium")
                
                # Set required action based on risk level
                if risk_level.lower() == "high":
                    required_action = "Immediate password change and account security review"
                elif risk_level.lower() == "medium":
                    required_action = "Change passwords and monitor accounts"
                else:
                    required_action = "Monitor account for suspicious activity"
                
                # Get threat details
                threat_details = f"{item.get('data_type', 'Unknown threat')} targeting {item.get('target_location', 'unknown target')}"
                
                threat_data_display.append({
                    "Date": date_str,
                    "Source": source,
                    "Target": target,
                    "Risk Level": risk_level,
                    "Threat Details": threat_details,
                    "Required Action": required_action
                })
            except Exception as e:
                continue
        
        # Create DataFrame and display
        threat_df = pd.DataFrame(threat_data_display)
        st.dataframe(threat_df, use_container_width=True)
    else:
        st.info("No threats found matching the search criteria")

    # Show alerts
    st.header("All Alerts")
    alert_data = []
    for alert in alerts:
        try:
            # Extract date from alert
            alert_time = datetime.fromisoformat(alert.get("alert_time", "").split("+")[0])
            alert_date_str = alert_time.strftime("%Y-%m-%d %H:%M")
            
            # Extract threat details
            alert_details = alert.get("scraped_data", {}).get("analysis", "No details available")
            
            # Add to data
            alert_data.append({
                "Date": alert_date_str,
                "Source": alert.get("scraped_data", {}).get("post_url", "Unknown Source"),
                "Alert Details": alert_details,
                "Required Action": "Change password and enable 2FA"  # Default action
            })
        except Exception as e:
            continue
    
    # Create DataFrame for alerts
    if alert_data:
        alert_df = pd.DataFrame(alert_data)
        st.dataframe(alert_df, use_container_width=True)
    else:
        st.info("No alerts detected.")

# Main app
def main():
    display_threat_dashboard()

if __name__ == "__main__":
    main()