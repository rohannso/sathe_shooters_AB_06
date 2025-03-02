import requests
import json
import datetime
import time
import os
import schedule
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
import re

# Import the alert system
import alert_system

# Define the TOR proxy settings
TOR_PROXY = "socks5h://127.0.0.1:9050"

# List of .onion URLs to monitor
ONION_URLS = [
    "http://i66jl3agkk6ufrdilljvc75w6mwn34hrx5e6ixy25o2ovxyxiqck5jyd.onion/",
    "http://aox44wz6rk6gwsxgru4wjyolbd5wdx64n2mqhbm3x7pmjjylnn3dr7qd.onion/",
    "http://vfobj3dlyiaygjyseo4yyrftciqmbbj7zytxnqwgeuaboxyvfur2hhyd.onion/",
    "http://7ctfvr7kp7scmqzinimkxqxpbrruyh2jddzyrn26qaw3wotdk2lvkzid.onion/"
]

# How often to run the scraper (in hours)
SCRAPE_INTERVAL = 3  # Run every 3 hours

# Output directory for JSON files
OUTPUT_DIR = "threat_intel_data"

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Check if Tor is working
def check_tor():
    url = "https://check.torproject.org/"
    proxies = {"http": TOR_PROXY, "https": TOR_PROXY}
    
    try:
        response = requests.get(url, proxies=proxies, timeout=10)
        if "Congratulations. This browser is configured to use Tor." in response.text:
            print("✅ Tor is working correctly!")
            return True
        else:
            print("❌ Tor is NOT working. Check your Tor service.")
            return False
    except Exception as e:
        print(f"❌ Error connecting to Tor: {e}")
        return False

# Scrape a .onion website
def scrape_onion_site(onion_url):
    proxies = {"http": TOR_PROXY, "https": TOR_PROXY}

    try:
        print(f"🔍 Attempting to access: {onion_url}")
        response = requests.get(onion_url, proxies=proxies, timeout=30)
        if response.status_code == 200:
            print(f"✅ Successfully accessed: {onion_url}")
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract basic information about the site
            site_info = {
                "url": onion_url,
                "title": soup.title.string if soup.title else "Unknown",
                "date_collected": datetime.datetime.now().isoformat()
            }
            
            return {
                "site_info": site_info,
                "content": soup.get_text()  # Extract text from HTML
            }
        else:
            print(f"⚠️ Failed to access: {onion_url} - HTTP Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error accessing {onion_url}: {e}")
        return None

# Extract information using LLM (LangChain + Groq)
def analyze_text(content_data):
    if not content_data:
        print("⚠️ No content to analyze!")
        return None

    content = content_data["content"]
    site_info = content_data["site_info"]
    
    llm = ChatGroq(api_key="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", model="gemma2-9b-it")

    prompt_template = PromptTemplate(
        input_variables=["text", "url", "date_collected"],
        template=(
            "Analyze the following dark web text and extract comprehensive threat intelligence.\n\n"
            "**Text from {url} collected at {date_collected}:**\n{text}\n\n"
            "Provide ONLY a valid JSON object with the following fields (use empty strings or arrays if information is not available):\n"
            "- source: Origin of the data (forum name, marketplace, etc.)\n"
            "- date_collected: Timestamp when data was scraped\n"
            "- data_type: Nature of data (credentials, attack plans, etc.)\n"
            "- content_type: Whether it's text, link, image, or file\n"
            "- post_title: Title or subject of the post/listing\n"
            "- post_content: Full content of the post\n"
            "- data_details: Specific sensitive details (usernames, passwords, etc.)\n"
            "- poster_info: Information about the poster (username, alias, etc.)\n"
            "- price: Price if it's a marketplace listing\n"
            "- category_tags: Array of tags classifying the data\n"
            "- target_location: Specific target mentioned (company, organization, etc.)\n"
            "- risk_level: Analysis-driven risk categorization (High, Medium, Low)\n"
            "- url: URL of the post\n"
            "- threat_actor: Person or organization behind the threat\n"
            "- target: Who is being threatened (array of objects)\n"
            "- threat_type: Type of threat (Hacking, Phishing, etc.)\n\n"
            "Return ONLY the JSON with NO additional text or explanations."
        )
    )
    
    # Use the LangChain pipeline
    chain = (
        prompt_template 
        | llm 
        | RunnableLambda(lambda x: x.content)
    )

    result = chain.invoke({
        "text": content,
        "url": site_info["url"],
        "date_collected": site_info["date_collected"]
    })
    
    # Try to extract just the JSON part if there's additional text
    try:
        # First attempt: direct parsing
        json_result = json.loads(result)
        return json_result
    except json.JSONDecodeError:
        print(f"⚠️ Direct JSON parsing failed for {site_info['url']}, trying to extract JSON from text...")
        
        # Second attempt: try to extract JSON using regex
        json_pattern = r'\{.*\}'
        match = re.search(json_pattern, result, re.DOTALL)
        
        if match:
            try:
                json_result = json.loads(match.group(0))
                return json_result
            except json.JSONDecodeError:
                pass
        
        # Third attempt: Try to clean up the JSON manually
        try:
            # Remove possible explanations or markdown
            cleaned_text = re.sub(r'```json|```', '', result).strip()
            json_result = json.loads(cleaned_text)
            return json_result
        except json.JSONDecodeError:
            pass
        
        # If all extraction attempts fail
        print(f"⚠️ Failed to extract valid JSON from LLM output for {site_info['url']}")
        return {
            "error": "Invalid JSON output from LLM",
            "source": site_info["url"],
            "date_collected": site_info["date_collected"]
        }

# Function to save the JSON to a file
def save_to_json_file(data, site_url):
    # Create a filename based on the site URL and timestamp
    site_domain = site_url.replace("http://", "").replace("https://", "").replace(".onion/", "")
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    filename = f"{OUTPUT_DIR}/threat_intel_{site_domain}_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(data, indent=4, fp=f)
        print(f"✅ Successfully saved data to {filename}")
    except Exception as e:
        print(f"❌ Error saving to JSON file: {e}")

# Function to scrape a single site
def scrape_site(url):
    content_data = scrape_onion_site(url)
    if content_data:
        result = analyze_text(content_data)
        if result:
            print(f"🔎 Successfully extracted threat intelligence from {url}")
            save_to_json_file(result, url)
            return True
    return False

# Function to scrape all sites
def scrape_all_sites():
    print(f"\n🕒 Starting scheduled scrape at {datetime.datetime.now().strftime('%Y-%m-%d')}")
    
    # First check if Tor is working
    if not check_tor():
        print("❌ Cannot proceed with scraping - Tor connection failed")
        return
    
    # Track success and failure counts
    success_count = 0
    failure_count = 0
    
    # Scrape each site
    for url in ONION_URLS:
        try:
            print(f"\n🌐 Processing: {url}")
            if scrape_site(url):
                success_count += 1
            else:
                failure_count += 1
                
            # Add a small delay between sites to avoid overwhelming Tor
            time.sleep(5)
        except Exception as e:
            print(f"❌ Unexpected error processing {url}: {e}")
            failure_count += 1
    
    print(f"\n📊 Scraping round completed: {success_count} successful, {failure_count} failed")
    print(f"⏰ Next scraping scheduled for {SCRAPE_INTERVAL} hours from now")
    
    # Run the alert system after scraping completes
    print("\n🔔 Running alert system to check for threats to registered users...")
    alert_system.generate_alerts()

# Function to run as a daemon/service
def run_scheduled_scraper():
    print(f"🤖 Dark Web Scraper started - will run every {SCRAPE_INTERVAL} hours")
    print(f"📁 Saving results to: {os.path.abspath(OUTPUT_DIR)}")
    
    # Run immediately on startup
    scrape_all_sites()
    
    # Schedule regular runs
    schedule.every(SCRAPE_INTERVAL).hours.do(scrape_all_sites)
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check schedule every minute

# Main Execution
if __name__ == "__main__":
    try:
        run_scheduled_scraper()
    except KeyboardInterrupt:
        print("\n🛑 Scraper stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")