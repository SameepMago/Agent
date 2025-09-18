from typing import List, Dict
import csv
import os
import tempfile
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def fetch_google_trends_csv() -> List[Dict]:
    """Use Selenium to download Google Trends CSV and parse it for trend, breakdown, and link data"""
    try:
        print("🔍 Setting up Chrome browser for Google Trends CSV download...")
        
        # Setup Chrome options with minimal configuration
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # Setup download preferences
        prefs = {
            "download.default_directory": tempfile.gettempdir(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Navigate to Google Trends
            print("🌐 Navigating to Google Trends...")
            driver.get("https://trends.google.com/trending?geo=US")
            
            # Wait for page to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give extra time for dynamic content
            time.sleep(5)
            
            print(f"🔍 Page title: {driver.title}")
            print(f"🔍 Current URL: {driver.current_url}")
            
            # Step 1: Find and click the Export button
            print("🔍 Looking for Export button...")
            export_button = None
            
            # Try different selectors for the Export button based on the website structure
            export_selectors = [
                "button:contains('Export')",  # Text-based selector
                "button[aria-label*='Export']",
                "button[title*='Export']",
                "[role='button']:contains('Export')",
                "button[data-testid*='export']",
                "button[aria-label*='ios_share']",
                "[aria-label*='Export']",
                ".export-button",
                "[class*='export']"
            ]
            
            for selector in export_selectors:
                try:
                    export_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Found Export button with selector: {selector}")
                    break
                except:
                    continue
            
            if not export_button:
                # Try to find by text content - look for the blue Export button
                print("🔍 Searching for Export button by text content...")
                buttons = driver.find_elements(By.TAG_NAME, "button")
                print(f"🔍 Found {len(buttons)} buttons on page")
                
                for i, button in enumerate(buttons):
                    try:
                        text = button.text.lower()
                        aria_label = button.get_attribute("aria-label") or ""
                        title = button.get_attribute("title") or ""
                        
                        print(f"🔍 Button {i}: text='{text[:30]}', aria-label='{aria_label[:30]}', title='{title[:30]}'")
                        
                        # Look for the Export button specifically
                        if "export" in text or "export" in aria_label.lower() or "export" in title.lower():
                            export_button = button
                            print(f"✅ Found Export button by text content: {text[:50]}...")
                            break
                    except Exception as e:
                        print(f"❌ Error checking button {i}: {e}")
                        continue
            
            if export_button:
                print("📤 Clicking Export button...")
                try:
                    export_button.click()
                except Exception as e:
                    print(f"❌ Export button click failed: {e}")
                    # Try JavaScript click
                    try:
                        driver.execute_script("arguments[0].click();", export_button)
                        print("✅ Used JavaScript click for Export button")
                    except Exception as e2:
                        print(f"❌ JavaScript click for Export button also failed: {e2}")
                        return []
                
                # Wait for dropdown to appear
                time.sleep(3)
                
                # Step 2: Find and click the Download CSV option
                print("🔍 Looking for Download CSV option...")
                csv_button = None
                
                # Try different selectors for the Download CSV option based on the dropdown structure
                csv_selectors = [
                    "a:contains('Download CSV')",  # Text-based selector for the first option
                    "button:contains('Download CSV')",
                    "a[aria-label*='Download CSV']",
                    "button[aria-label*='Download CSV']",
                    "a[title*='Download CSV']",
                    "button[title*='Download CSV']",
                    "[role='menuitem']:contains('Download CSV')",
                    "[role='menuitem'][aria-label*='Download CSV']",
                    "[role='menuitem'][aria-label*='CSV']",
                    "a[aria-label*='csv']",
                    "button[aria-label*='csv']",
                    ".menu-item:contains('Download CSV')",
                    ".dropdown-item:contains('Download CSV')"
                ]
                
                for selector in csv_selectors:
                    try:
                        csv_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        print(f"✅ Found Download CSV button with selector: {selector}")
                        break
                    except:
                        continue
                
                if not csv_button:
                    # Try to find by text content in the dropdown - look for the first option
                    print("🔍 Searching for Download CSV by text content...")
                    dropdown_elements = driver.find_elements(By.CSS_SELECTOR, "[role='menuitem'], .menu-item, .dropdown-item, a, button")
                    print(f"🔍 Found {len(dropdown_elements)} dropdown elements")
                    
                    for i, element in enumerate(dropdown_elements):
                        try:
                            text = element.text.lower()
                            aria_label = element.get_attribute("aria-label") or ""
                            title = element.get_attribute("title") or ""
                            
                            print(f"🔍 Dropdown element {i}: text='{text[:30]}', aria-label='{aria_label[:30]}', title='{title[:30]}'")
                            
                            # Look for Download CSV specifically
                            if "download csv" in text or "download csv" in aria_label.lower() or "download csv" in title.lower():
                                csv_button = element
                                print(f"✅ Found Download CSV by text content: {text[:50]}...")
                                break
                        except Exception as e:
                            print(f"❌ Error checking dropdown element {i}: {e}")
                            continue
                
                if csv_button:
                    print("📥 Clicking Download CSV button...")
                    try:
                        csv_button.click()
                    except Exception as e:
                        print(f"❌ Download CSV click failed: {e}")
                        # Try JavaScript click
                        try:
                            driver.execute_script("arguments[0].click();", csv_button)
                            print("✅ Used JavaScript click for Download CSV")
                        except Exception as e2:
                            print(f"❌ JavaScript click for Download CSV also failed: {e2}")
                            return []
                    
                    # Wait for download to complete
                    time.sleep(8)
                    
                    # Look for downloaded CSV file
                    temp_dir = tempfile.gettempdir()
                    csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
                    
                    if csv_files:
                        # Get the most recent CSV file
                        csv_files.sort(key=lambda x: os.path.getmtime(os.path.join(temp_dir, x)), reverse=True)
                        csv_file_path = os.path.join(temp_dir, csv_files[0])
                        
                        print(f"📄 Found downloaded CSV: {csv_file_path}")
                        
                        # Parse CSV file
                        trends_data = []
                        try:
                            with open(csv_file_path, 'r', encoding='utf-8') as file:
                                # The CSV has no headers, so we'll read it manually
                                lines = file.readlines()
                                for line in lines:
                                    if line.strip():
                                        # Split by comma, but handle quoted fields properly
                                        parts = []
                                        current_part = ""
                                        in_quotes = False
                                        
                                        for char in line.strip():
                                            if char == '"':
                                                in_quotes = not in_quotes
                                            elif char == ',' and not in_quotes:
                                                parts.append(current_part.strip('"'))
                                                current_part = ""
                                            else:
                                                current_part += char
                                        
                                        # Add the last part
                                        if current_part:
                                            parts.append(current_part.strip('"'))
                                        
                                        # Extract data based on the CSV structure:
                                        # Column 0: Trend name
                                        # Column 1: Search volume  
                                        # Column 2: Start time
                                        # Column 3: End time
                                        # Column 4: Breakdown/related terms
                                        # Column 5: Link
                                        if len(parts) >= 6:
                                            trend_name = parts[0].strip()
                                            search_volume = parts[1].strip()
                                            breakdown = parts[4].strip()
                                            link = parts[5].strip()
                                            
                                            if trend_name and len(trend_name) > 3:
                                                trends_data.append({
                                                    'trend': trend_name,
                                                    'breakdown': breakdown,
                                                    'link': link
                                                })
                        except Exception as e:
                            print(f"❌ CSV parsing failed: {e}")
                            # Try to read as plain text and extract trends
                            try:
                                with open(csv_file_path, 'r', encoding='utf-8') as file:
                                    content = file.read()
                                    lines = content.split('\n')
                                    for line in lines:
                                        if line.strip() and ',' in line:
                                            parts = line.split(',')
                                            if len(parts) >= 1:
                                                trend = parts[0].strip().strip('"')
                                                if trend and len(trend) > 3:
                                                    trends_data.append({
                                                        'trend': trend,
                                                        'breakdown': parts[4].strip().strip('"') if len(parts) > 4 else '',
                                                        'link': parts[5].strip().strip('"') if len(parts) > 5 else ''
                                                    })
                            except Exception as e2:
                                print(f"❌ Plain text parsing also failed: {e2}")
                        
                        # Clean up downloaded file
                        try:
                            os.remove(csv_file_path)
                        except:
                            pass
                        
                        if trends_data:
                            print(f"✅ Google Trends CSV: {len(trends_data)} total trending terms with breakdowns")
                            return trends_data
                    else:
                        print("❌ No CSV file found after download")
                        # Debug: show what files are in temp directory
                        temp_files = [f for f in os.listdir(temp_dir) if f.endswith(('.csv', '.xlsx', '.txt'))]
                        if temp_files:
                            print(f"📁 Found other files in temp dir: {temp_files}")
                else:
                    print("❌ Could not find Download CSV option")
            else:
                print("❌ Could not find Export button")
                # Debug: show page source to understand structure
                print("🔍 Page title:", driver.title)
                print("🔍 Current URL:", driver.current_url)
                
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"❌ Google Trends CSV Selenium failed: {e}")
        return []
    
    return []
