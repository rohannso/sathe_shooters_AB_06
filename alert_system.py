import json
import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from langchain_groq import ChatGroq

# Initialize LLM
llm = ChatGroq(api_key="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", model="gemma2-9b-it")

# Path to the registered users dataset
REGISTERED_USERS_PATH = "threat_intel_data/registered_users.json"
# Path to the directory where threat intelligence data (scraped data) is stored
SCRAPED_DATA_PATH = "threat_intel_data"

# Email configuration
EMAIL_SENDER = "rohannso14@gmail.com"  # Update with your email
EMAIL_PASSWORD = "pfwwcrtjripwgkrc"    # Update with your app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Read registered users from the JSON file
def read_registered_users():
    try:
        with open(REGISTERED_USERS_PATH, "r") as file:
            users = json.load(file)
        print(f"✅ Successfully loaded {len(users)} registered users.")
        return users
    except Exception as e:
        print(f"❌ Error loading registered users: {e}")
        return []

# Get the latest folder based on timestamp
def get_latest_scraped_data_folder():
    try:
        # Check if the directory exists
        if not os.path.exists(SCRAPED_DATA_PATH):
            print(f"❌ The base path does not exist: {SCRAPED_DATA_PATH}")
            return None
            
        # Get all items that start with "threat_intel_"
        all_items = [f for f in os.listdir(SCRAPED_DATA_PATH) if f.startswith("threat_intel_")]
        
        # Filter to get only directories (not files)
        all_folders = [f for f in all_items if os.path.isdir(os.path.join(SCRAPED_DATA_PATH, f))]
        
        if not all_folders:
            # If no folders, check if there are JSON files directly in the directory
            json_files = [f for f in all_items if f.endswith(".json")]
            if json_files:
                print(f"✅ No folders found, but found {len(json_files)} JSON files in the base directory.")
                return SCRAPED_DATA_PATH
            else:
                print("❌ No scraped data folders or files found!")
                return None
        
        # Sort folders by the timestamp (extract the timestamp part from the folder name)
        latest_folder = sorted(all_folders, key=lambda x: x.split("_")[-1], reverse=True)[0]
        folder_path = os.path.join(SCRAPED_DATA_PATH, latest_folder)
        
        print(f"✅ Using the latest scraped data folder: {folder_path}")
        return folder_path
    except Exception as e:
        print(f"❌ Error finding latest scraped data folder: {e}")
        return None

# Read all JSON files in the scraped folder
def read_scraped_data_from_folder(folder_path):
    scraped_data = []
    try:
        # If folder_path is the base directory, look for files directly
        if folder_path == SCRAPED_DATA_PATH:
            for filename in os.listdir(folder_path):
                if filename.startswith("threat_intel_") and filename.endswith(".json"):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, "r") as file:
                            data = json.load(file)
                            # If data is a list, extend scraped_data, otherwise append it
                            if isinstance(data, list):
                                scraped_data.extend(data)
                            else:
                                scraped_data.append(data)
                    except json.JSONDecodeError as e:
                        print(f"❌ Error parsing JSON file {filename}: {e}")
                        continue
        else:
            # Read all files in the folder (only JSON files)
            for filename in os.listdir(folder_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, "r") as file:
                            data = json.load(file)
                            # If data is a list, extend scraped_data, otherwise append it
                            if isinstance(data, list):
                                scraped_data.extend(data)
                            else:
                                scraped_data.append(data)
                    except json.JSONDecodeError as e:
                        print(f"❌ Error parsing JSON file {filename}: {e}")
                        continue
                        
        print(f"✅ Loaded {len(scraped_data)} scraped data items.")
        return scraped_data
    except Exception as e:
        print(f"❌ Error loading scraped data: {e}")
        return []

# Analyze post content with LLM to detect references to registered users
def analyze_content_with_llm(post_content, users):
    try:
        user_emails = [user['email'].lower() for user in users]
        user_usernames = [user['username'].lower() for user in users]

        # Create a prompt to instruct the LLM to look for user references
        prompt = f"""
        Given the following content, determine if it references any of the registered users. A registered user can be identified by their email or username. 
        If a reference is found, extract the specific user's details including their email and username, and flag this as a potential threat. 
        Return the format: "User found: [username], [email] - Description of the threat and context"
        If no reference is found, just say "No reference to registered users found."

        Post content: "{post_content}"

        Registered users:
        Emails: {user_emails}
        Usernames: {user_usernames}
        """

        # Query the LLM model - the response here is an AIMessage from LangChain, not the raw API response
        response = llm.invoke(prompt)
        
        # LangChain returns an AIMessage object, so we access the content directly
        # In LangChain, the response content is accessed through .content attribute
        return response.content.strip() if hasattr(response, 'content') else str(response).strip()
    except Exception as e:
        print(f"❌ Error analyzing content with LLM: {e}")
        return None

# Function to send email alerts
def send_email_alert(user_email, alert_data):
    try:
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = user_email
        msg['Subject'] = f"⚠️ SECURITY ALERT: Potential Data Exposure Detected"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e1e1e1; border-radius: 5px;">
                <h2 style="color: #d9534f;">⚠️ Security Alert: Potential Data Exposure</h2>
                <p>We have detected what appears to be your information being shared or discussed in an online post. This may indicate a potential security threat.</p>
                
                <div style="background-color: #f8f8f8; padding: 15px; border-left: 4px solid #d9534f; margin: 20px 0;">
                    <h3>Alert Details:</h3>
                    <p><strong>Post Title:</strong> {alert_data['scraped_data']['post_title']}</p>
                    <p><strong>Post URL:</strong> <a href="{alert_data['scraped_data']['post_url']}">{alert_data['scraped_data']['post_url']}</a></p>
                    <p><strong>Detection Time:</strong> {alert_data['alert_time']}</p>
                    <p><strong>Analysis:</strong> {alert_data['scraped_data']['analysis']}</p>
                </div>
                
                <h3>Recommended Actions:</h3>
                <ol>
                    <li>Check if your accounts have been compromised</li>
                    <li>Change your passwords for any potentially affected accounts</li>
                    <li>Enable two-factor authentication where available</li>
                    <li>Monitor your accounts for suspicious activity</li>
                </ol>
                
                <p>If you need assistance or have questions, please reply to this email or contact our security team.</p>
                
                <p style="font-size: 0.8em; color: #777; margin-top: 30px; border-top: 1px solid #e1e1e1; padding-top: 10px;">
                    This is an automated security alert. Please do not reply to this email with sensitive information.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            
        print(f"✅ Email alert sent successfully to {user_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email alert: {e}")
        return False

# Extract referenced user's email from analysis
def extract_user_email_from_analysis(analysis, users):
    try:
        # If no threat found
        if "no reference" in analysis.lower() or "not found" in analysis.lower():
            return None
            
        # Try to extract email from the analysis
        for user in users:
            email = user['email'].lower()
            username = user['username'].lower()
            
            # Look for email or username in the analysis
            if email in analysis.lower() or username in analysis.lower():
                return user['email']
                
        # If we can't extract a specific email, return None
        return None
    except Exception as e:
        print(f"❌ Error extracting user email from analysis: {e}")
        return None

# Check user references and perform LLM-based analysis
def check_user_references(scraped_data, users):
    alerts = []
    
    for data in scraped_data:
        # Handle potential different data structures
        if isinstance(data, dict):
            post_content = data.get("post_content", "")
            post_title = data.get("post_title", "")
            post_url = data.get("url", "")
            
            # Analyze post content with LLM for potential references to registered users
            analysis = analyze_content_with_llm(post_content, users)
            
            if analysis and "no reference" not in analysis.lower() and "not found" not in analysis.lower():
                alert = {
                    "alert_time": datetime.now().isoformat(),
                    "scraped_data": {
                        "post_title": post_title,
                        "post_content": post_content,
                        "post_url": post_url,
                        "analysis": analysis
                    },
                    "alert_message": f"User data found in post: {post_title}",
                }
                alerts.append(alert)
                
                # Extract affected user's email and send alert
                user_email = extract_user_email_from_analysis(analysis, users)
                if user_email:
                    send_email_alert(user_email, alert)
                else:
                    print(f"⚠️ Could not determine which user to alert for post: {post_title}")
                    # Fall back to alerting an admin
                    send_email_alert(EMAIL_SENDER, alert)
                
    return alerts

# Main function to generate alerts based on scraped data and registered users
def generate_alerts():
    print("✅ Checking for user references in scraped data...")

    # Read registered users
    users = read_registered_users()
    if not users:
        print("❌ No registered users found!")
        return

    # Get the latest scraped data folder
    folder_path = get_latest_scraped_data_folder()
    if not folder_path:
        return

    # Read scraped data from the latest folder
    scraped_data = read_scraped_data_from_folder(folder_path)
    if not scraped_data:
        print("❌ No scraped data found!")
        return

    # Check for user references in the scraped data and generate alerts
    alerts = check_user_references(scraped_data, users)

    # Save alerts to a log file
    if alerts:
        log_filename = f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_path = os.path.join(SCRAPED_DATA_PATH, log_filename)
        
        try:
            with open(log_path, "w") as f:
                json.dump(alerts, f, indent=2)
            print(f"✅ Saved {len(alerts)} alerts to {log_path}")
        except Exception as e:
            print(f"❌ Error saving alerts to log file: {e}")
        
        # Also print alerts to console
        for alert in alerts:
            print(f"⚠️ ALERT: {alert['alert_message']}")
            print(f"Post Title: {alert['scraped_data']['post_title']}")
            print(f"Post URL: {alert['scraped_data']['post_url']}")
            print(f"Analysis: {alert['scraped_data']['analysis']}")
            print(f"Alert Time: {alert['alert_time']}")
            print("-" * 80)
    else:
        print("✅ No alerts triggered.")

# Running periodically (only if this file is run directly)
def run_periodic_alerts():
    while True:
        print(f"🔄 Checking for alerts at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        generate_alerts()
        time.sleep(10800)  # Wait for 3 hours (3 * 60 * 60 seconds)

if __name__ == "__main__":
    try:
        run_periodic_alerts()
    except KeyboardInterrupt:
        print("\n🛑 Alert System stopped by user.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")