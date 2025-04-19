from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import os
from datetime import datetime
import urllib.parse
import random
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("linkedin_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Configuration
LINKEDIN_EMAIL = "example@gmail.com"  # Replace with your LinkedIn email
LINKEDIN_PASSWORD = "password"  # Replace with your LinkedIn password
SCREENSHOT_DIR = "screenshots"
MAX_APPLICATIONS = 3  # Maximum number of applications per search
WAIT_TIME_BETWEEN_ACTIONS = (2, 5)  # Random wait time range between actions in seconds

# Create screenshots directory if it doesn't exist
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def random_wait():
    """Wait for a random time within the specified range"""
    wait_time = random.uniform(WAIT_TIME_BETWEEN_ACTIONS[0], WAIT_TIME_BETWEEN_ACTIONS[1])
    time.sleep(wait_time)

def take_screenshot(driver, prefix):
    """Take a screenshot and save it with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOT_DIR}/{prefix}_{timestamp}.png"
    try:
        driver.save_screenshot(filename)
        logger.info(f"Saved screenshot: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Failed to take screenshot: {str(e)}")
        return None

def setup_driver():
    """Set up and return a configured Chrome WebDriver with enhanced options"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.86 Safari/537.36")
        
        # Initialize Chrome driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        driver.set_page_load_timeout(30)
        
        logger.info("WebDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {str(e)}")
        raise

def login_to_linkedin(driver):
    """Log in to LinkedIn account with enhanced error handling"""
    try:
        logger.info("Navigating to LinkedIn login page")
        driver.get("https://www.linkedin.com/login")
        
        # Wait for login page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        # Enter credentials with random delays to mimic human behavior
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")
        
        # Type email character by character with slight delays
        for char in LINKEDIN_EMAIL:
            username_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        random_wait()
        
        # Type password character by character with slight delays
        for char in LINKEDIN_PASSWORD:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        
        random_wait()
        
        # Click login button
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Wait for login to complete with multiple possible success indicators
        try:
            WebDriverWait(driver, 25).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".global-nav")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".authentication-outlet")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-global-nav]"))
                )
            )
            logger.info("Successfully logged in to LinkedIn")
            
            # Check for security verification
            security_challenge = driver.find_elements(By.CSS_SELECTOR, ".challenge-dialog")
            if security_challenge:
                logger.warning("Security verification detected - manual intervention required")
                take_screenshot(driver, "security_challenge")
                
                # Wait for manual intervention - adjust timeout as needed
                input("Security verification detected. Please complete it manually, then press Enter to continue...")
            
            # Wait to ensure full page load and session establishment
            time.sleep(5)
            take_screenshot(driver, "post_login")
            
            return True
        except TimeoutException:
            logger.error("Login timeout - could not detect successful login elements")
            take_screenshot(driver, "login_timeout")
            return False
            
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        take_screenshot(driver, "login_error")
        return False

def search_jobs_directly(driver, keywords, location):
    """Search for jobs with improved error handling and verification"""
    try:
        logger.info(f"Searching for '{keywords}' jobs in '{location}' using direct URL")
        
        # Format the search URL
        encoded_keywords = urllib.parse.quote(keywords)
        encoded_location = urllib.parse.quote(location)
        
        # Navigate directly to search results with filters
        # Use f_AL=true for Easy Apply filter
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_keywords}&location={encoded_location}&f_AL=true"
        driver.get(search_url)
        
        # Wait for page to load with better timeout handling
        random_wait()
        take_screenshot(driver, f"search_initial_{encoded_keywords}_{encoded_location}")
        
        # Use a comprehensive approach to verify search results loaded
        search_result_selectors = [
            ".jobs-search-results-list",
            ".jobs-search-results",
            ".jobs-search-two-pane__results",
            ".results-context-header",
            ".jobs-search__job-details"
        ]
        
        # Try multiple selectors to check if search results loaded
        search_loaded = False
        for selector in search_result_selectors:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"Search results loaded successfully (detected with selector: {selector})")
                search_loaded = True
                break
            except TimeoutException:
                continue
        
        if search_loaded:
            # Check if we have actual job listings
            try:
                # Wait a bit more for the actual job cards to load
                time.sleep(3)
                
                # Check for multiple possible job card selectors
                job_card_selectors = [
                    ".job-card-container",
                    ".jobs-search-results__list-item",
                    ".jobs-search-result-item"
                ]
                
                for selector in job_card_selectors:
                    job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        logger.info(f"Found {len(job_cards)} job cards with selector: {selector}")
                        take_screenshot(driver, f"search_results_{encoded_keywords}")
                        return True
                
                # If we get here but found no job cards with any selector
                logger.warning("Search page loaded but no job cards found")
                take_screenshot(driver, "search_no_jobs_found")
                
                # Check if there's a "No matching jobs found" message
                no_jobs_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'No matching jobs')]")
                if no_jobs_elements:
                    logger.info("LinkedIn reported no matching jobs for this search")
                    return False
                
                # Try scrolling down to trigger lazy loading
                driver.execute_script("window.scrollTo(0, 500)")
                time.sleep(3)
                
                # Check again after scrolling
                for selector in job_card_selectors:
                    job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        logger.info(f"Found {len(job_cards)} job cards after scrolling")
                        return True
                
                logger.warning("Still no job cards found after scrolling")
                return False
                
            except Exception as e:
                logger.error(f"Error verifying job cards: {str(e)}")
                take_screenshot(driver, "job_cards_error")
                return False
        else:
            logger.error("Search results did not load properly")
            take_screenshot(driver, "search_results_timeout")
            return False
            
    except Exception as e:
        logger.error(f"Error during direct URL job search: {str(e)}")
        take_screenshot(driver, "direct_search_error")
        return False

def get_job_listings(driver):
    """Get job listings with improved selector detection"""
    try:
        logger.info("Finding job listings")
        
        # Define multiple possible selectors for job cards
        job_card_selectors = [
            ".job-card-container", 
            ".jobs-search-results__list-item",
            ".jobs-search-result-item"
        ]
        
        # Try each selector
        job_cards = []
        for selector in job_card_selectors:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if job_cards:
                    logger.info(f"Found {len(job_cards)} job cards with selector: {selector}")
                    break
            except TimeoutException:
                continue
        
        if not job_cards:
            logger.warning("Could not find job cards with any selector")
            take_screenshot(driver, "no_job_cards_found")
            return []
        
        # Take a screenshot showing the job cards
        take_screenshot(driver, "job_cards_found")
        
        return job_cards
        
    except Exception as e:
        logger.error(f"Error getting job listings: {str(e)}")
        take_screenshot(driver, "job_listings_error")
        return []

def check_easy_apply(driver):
    """Check if the current job has Easy Apply option"""
    try:
        # Try different selectors for Easy Apply button
        easy_apply_selectors = [
            ".jobs-apply-button",
            "button[data-control-name='jobdetails_topcard_inapply']",
            "button[aria-label='Easy Apply']",
            "button span:contains('Easy Apply')"
        ]
        
        for selector in easy_apply_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and any(element.is_displayed() for element in elements):
                    return True
            except:
                continue
                
        # Check if "Apply" text is in any button
        apply_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Apply') or contains(., 'Easy Apply')]")
        if apply_buttons and any(button.is_displayed() for button in apply_buttons):
            return True
            
        return False
    except:
        return False

def apply_to_job(driver, job_card, index):
    """Apply to a job with improved error handling"""
    try:
        logger.info(f"Attempting to apply to job #{index+1}")
        
        # Try clicking the job card with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Click on the job card to view details
                driver.execute_script("arguments[0].scrollIntoView(true);", job_card)
                random_wait()
                job_card.click()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Failed to click job card (attempt {attempt+1}): {str(e)}")
                    random_wait()
                else:
                    logger.error(f"Failed to click job card after {max_retries} attempts")
                    return False
        
        # Wait for job details to load with multiple possible selectors
        try:
            WebDriverWait(driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-unified-top-card")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-details")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-box__html-content"))
                )
            )
        except TimeoutException:
            logger.error("Job details did not load")
            take_screenshot(driver, f"job_details_timeout_{index}")
            return False
        
        # Take screenshot of job details
        random_wait()
        take_screenshot(driver, f"job_details_{index}")
        
        # Get job title and company if available
        try:
            job_title_selectors = [
                ".jobs-unified-top-card__job-title",
                ".jobs-details-top-card__job-title"
            ]
            
            company_selectors = [
                ".jobs-unified-top-card__company-name",
                ".jobs-details-top-card__company-info"
            ]
            
            job_title = None
            for selector in job_title_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    job_title = elements[0].text
                    break
                    
            company = None
            for selector in company_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    company = elements[0].text
                    break
            
            if job_title and company:
                logger.info(f"Selected job: {job_title} at {company}")
            else:
                logger.warning("Could not extract complete job details")
        except Exception as e:
            logger.warning(f"Error extracting job details: {str(e)}")
        
        # Check if Easy Apply button exists
        if not check_easy_apply(driver):
            logger.info("No Easy Apply option for this job, skipping")
            return False
            
        # Find and click Easy Apply button
        apply_button_found = False
        apply_selectors = [
            ".jobs-apply-button",
            "button[data-control-name='jobdetails_topcard_inapply']",
            "button[aria-label='Easy Apply']"
        ]
        
        for selector in apply_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    if button.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        random_wait()
                        button.click()
                        apply_button_found = True
                        logger.info("Clicked Easy Apply button")
                        break
                if apply_button_found:
                    break
            except Exception as e:
                logger.warning(f"Failed with selector {selector}: {str(e)}")
                continue
                
        # If still not found, try XPATH approach
        if not apply_button_found:
            try:
                apply_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Apply') or contains(., 'Easy Apply')]")
                for button in apply_buttons:
                    if button.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        random_wait()
                        button.click()
                        apply_button_found = True
                        logger.info("Clicked Easy Apply button (by text)")
                        break
            except Exception as e:
                logger.warning(f"Failed to find apply button by text: {str(e)}")
        
        if not apply_button_found:
            logger.error("Could not find or click any Easy Apply button")
            take_screenshot(driver, f"no_apply_button_{index}")
            return False
        
        # Wait for application form
        try:
            WebDriverWait(driver, 10).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-easy-apply-content")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-apply-form")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".artdeco-modal-overlay"))
                )
            )
            logger.info("Application form loaded")
            take_screenshot(driver, f"application_form_{index}")
            
            # Handle the application process
            result = complete_application(driver, index)
            return result
        except TimeoutException:
            logger.error("Application form did not load")
            take_screenshot(driver, f"application_form_timeout_{index}")
            return False
            
    except Exception as e:
        logger.error(f"Error applying to job: {str(e)}")
        take_screenshot(driver, f"apply_error_{index}")
        return False

def complete_application(driver, index):
    """Complete the Easy Apply application process with improved field handling"""
    try:
        logger.info(f"Completing application #{index+1}")
        
        # Flag to track if we're on the last step
        is_last_step = False
        steps_completed = 0
        max_steps = 10  # Safety limit
        
        while not is_last_step and steps_completed < max_steps:
            # Take screenshot at each step
            take_screenshot(driver, f"application_step_{index}_{steps_completed}")
            random_wait()
            
            # Check for completion indicators
            submit_indicators = [
                "//button[contains(.,'Submit application')]",
                "//button[contains(.,'Submit')]",
                "//button[contains(.,'Done')]",
                "//button[contains(.,'I Agree')]",
                "//span[contains(.,'Application submitted')]"
            ]
            
            # Check for "Submit application" button which indicates final step
            for indicator in submit_indicators:
                elements = driver.find_elements(By.XPATH, indicator)
                if elements and any(element.is_displayed() for element in elements):
                    logger.info(f"Found submit indicator: {indicator} - this is the final step")
                    is_last_step = True
                    
                    for element in elements:
                        if element.is_displayed():
                            try:
                                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                random_wait()
                                element.click()
                                logger.info("Application submitted!")
                                time.sleep(3)
                                take_screenshot(driver, f"application_submitted_{index}")
                                return True
                            except Exception as e:
                                logger.error(f"Error clicking submit button: {str(e)}")
                    break
            
            if is_last_step:
                break
                
            # Handle form fields before looking for Next button
            try:
                # Fill text fields if required
                text_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='text']:not([value]), input[type='email']:not([value]), input[type='tel']:not([value])")
                for field in text_fields:
                    if field.is_displayed() and field.get_attribute("value") == "":
                        field_id = field.get_attribute("id") or field.get_attribute("name") or "unknown"
                        
                        # Try to determine field type
                        if "email" in field_id.lower() or field.get_attribute("type") == "email":
                            field.send_keys(LINKEDIN_EMAIL)
                            logger.info(f"Filled email field: {field_id}")
                        elif "phone" in field_id.lower() or "tel" in field_id.lower() or field.get_attribute("type") == "tel":
                            field.send_keys("5551234567")  # Replace with your phone number
                            logger.info(f"Filled phone field: {field_id}")
                        elif "years" in field_id.lower() or "experience" in field_id.lower():
                            field.send_keys("3")
                            logger.info(f"Filled experience field: {field_id}")
                        else:
                            field.send_keys("Yes")
                            logger.info(f"Filled generic text field: {field_id}")
                        random_wait()
                
                # Handle textarea fields
                textareas = driver.find_elements(By.TAG_NAME, "textarea")
                for textarea in textareas:
                    if textarea.is_displayed() and textarea.get_attribute("value") == "":
                        textarea_id = textarea.get_attribute("id") or textarea.get_attribute("name") or "unknown"
                        textarea.send_keys("I have the required experience and skills for this position.")
                        logger.info(f"Filled textarea: {textarea_id}")
                        random_wait()
                
                # Handle dropdown selections
                dropdowns = driver.find_elements(By.CSS_SELECTOR, "select")
                for dropdown in dropdowns:
                    if dropdown.is_displayed():
                        # Select the second option if available (first is often a placeholder)
                        options = dropdown.find_elements(By.TAG_NAME, "option")
                        if len(options) > 1:
                            # Try to find "Yes" option first
                            yes_option = None
                            for option in options:
                                if option.text.lower() == "yes":
                                    yes_option = option
                                    break
                            
                            if yes_option:
                                yes_option.click()
                                logger.info("Selected 'Yes' from dropdown")
                            else:
                                # Otherwise select the second option
                                options[1].click()
                                logger.info(f"Selected option: {options[1].text}")
                        random_wait()
                
                # Handle radio buttons - prefer "Yes" options
                radio_groups = {}
                radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                
                # Group radio buttons by name
                for radio in radio_buttons:
                    if radio.is_displayed():
                        name = radio.get_attribute("name")
                        if name not in radio_groups:
                            radio_groups[name] = []
                        radio_groups[name].append(radio)
                
                # For each group, select the appropriate option
                for name, radios in radio_groups.items():
                    if not any(radio.is_selected() for radio in radios):
                        # Try to find "Yes" option first
                        yes_radio = None
                        for radio in radios:
                            # Check label by finding parent and sibling elements with "Yes" text
                            try:
                                label_elements = driver.find_elements(By.XPATH, f"//label[@for='{radio.get_attribute('id')}']")
                                for label in label_elements:
                                    if label.text.lower() == "yes":
                                        yes_radio = radio
                                        break
                                if yes_radio:
                                    break
                            except:
                                pass
                        
                        if yes_radio:
                            try:
                                driver.execute_script("arguments[0].scrollIntoView(true);", yes_radio)
                                yes_radio.click()
                                logger.info(f"Selected 'Yes' radio button for group: {name}")
                            except:
                                logger.warning(f"Could not click 'Yes' radio button for group: {name}")
                        else:
                            # If no "Yes" option, select the first option
                            try:
                                driver.execute_script("arguments[0].scrollIntoView(true);", radios[0])
                                radios[0].click()
                                logger.info(f"Selected first radio button for group: {name}")
                            except:
                                logger.warning(f"Could not click first radio button for group: {name}")
                        random_wait()
                            
                # Handle checkboxes
                checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                for checkbox in checkboxes:
                    if checkbox.is_displayed() and not checkbox.is_selected():
                        try:
                            checkbox_id = checkbox.get_attribute("id") or "unknown"
                            
                            # Get label text if possible
                            label_text = ""
                            try:
                                label_elements = driver.find_elements(By.XPATH, f"//label[@for='{checkbox.get_attribute('id')}']")
                                if label_elements:
                                    label_text = label_elements[0].text
                            except:
                                pass
                                
                            # Don't check unsubscribe or opt-out boxes
                            if any(term in label_text.lower() for term in ["unsubscribe", "opt out", "marketing", "newsletter"]):
                                logger.info(f"Skipping marketing checkbox: {label_text}")
                                continue
                                
                            # Check agreement boxes
                            driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                            checkbox.click()
                            logger.info(f"Checked checkbox: {checkbox_id} - {label_text}")
                        except:
                            logger.warning(f"Could not click checkbox")
                            pass
                        random_wait()
                            
            except Exception as form_error:
                logger.error(f"Error filling form: {str(form_error)}")
            
            # Look for Next/Continue buttons
            next_indicators = [
                "//button[contains(.,'Next')]",
                "//button[contains(.,'Continue')]",
                "//button[contains(.,'Review')]",
                "//button[contains(.,'Next')]//span",
                "//button[contains(.,'Continue')]//span",
                "//button[contains(.,'Review')]//span"
            ]
            
            next_button_found = False
            for indicator in next_indicators:
                elements = driver.find_elements(By.XPATH, indicator)
                visible_elements = [element for element in elements if element.is_displayed()]
                
                if visible_elements:
                    try:
                        element = visible_elements[0]
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        random_wait()
                        element.click()
                        logger.info(f"Clicked '{element.text}' button")
                        next_button_found = True
                        steps_completed += 1
                        random_wait()
                        break
                    except Exception as e:
                        logger.warning(f"Error clicking next button: {str(e)}")
                        
            if not next_button_found:
                # If we can't find a next button, we might be stuck or done
                logger.warning("No next button found")
                
                # Check for followup messages or completion indicators
                followup_indicators = [
                    "//div[contains(.,'Application submitted')]",
                    "//span[contains(.,'Application submitted')]",
                    "//div[contains(.,'successfully submitted')]",
                    "//div[contains(.,'successfully applied')]"
                ]
                
                for indicator in followup_indicators:
                    elements = driver.find_elements(By.XPATH, indicator)
                    if elements and any(element.is_displayed() for element in elements):
                        logger.info("Application appears to be complete based on success message")
                        is_last_step = True
                        take_screenshot(driver, f"application_completed_{index}")
                        return True
                
                # Check for "Follow" buttons which might appear at end of application
                follow_buttons = driver.find_elements(By.XPATH, "//button[contains(.,'Follow')]")
                if follow_buttons and any(button.is_displayed() for button in follow_buttons):
                    logger.info("Application may be complete. Found Follow button.")
                    is_last_step = True
                    return True
                
                # Try to find dismiss/close button if we're stuck
                close_selectors = [
                    "button[aria-label='Dismiss']",
                    "button[aria-label='Cancel']",
                    "button[aria-label='Close']",
                    "button.artdeco-modal__dismiss",
                    ".artdeco-modal__dismiss"
                ]
                
                for selector in close_selectors:
                    close_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in close_buttons:
                        if button.is_displayed():
                            try:
                                button.click()
                                logger.info(f"Clicked close button")
                                time.sleep(2)
                                
                                # Check for "Discard" button if prompted
                                discard_buttons = driver.find_elements(By.XPATH, "//button[contains(.,'Discard')]")
                                for discard_button in discard_buttons:
                                    if discard_button.is_displayed():
                                        discard_button.click()
                                        logger.info("Clicked discard button")
                                        time.sleep(2)
                                        break
                                        
                                break
                            except:
                                pass
                
                # If we've tried everything, break the loop
                break
        
        # If we exited the loop without completing application
        if not is_last_step and steps_completed >= max_steps:
            logger.warning(f"Reached maximum steps ({max_steps}) without completing application")
            
            # Try to exit the application modal
            try:
                close_selectors = [
                    "button[aria-label='Dismiss']",
                    "button[aria-label='Cancel']",
                    "button[aria-label='Close']",
                    "button.artdeco-modal__dismiss",
                    ".artdeco-modal__dismiss"
                ]
                
                for selector in close_selectors:
                    close_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in close_buttons:
                        if button.is_displayed():
                            try:
                                button.click()
                                logger.info(f"Exited incomplete application")
                                time.sleep(2)
                                
                                # Check for "Discard" button if prompted
                                discard_buttons = driver.find_elements(By.XPATH, "//button[contains(.,'Discard')]")
                                for discard_button in discard_buttons:
                                    if discard_button.is_displayed():
                                        discard_button.click()
                                        logger.info("Clicked discard button")
                                        time.sleep(2)
                                        break
                                        
                                break
                            except:
                                pass
            except Exception as exit_error:
                logger.error(f"Could not exit application modal: {str(exit_error)}")
                
        return is_last_step
        
    except Exception as e:
        logger.error(f"Error completing application: {str(e)}")
        take_screenshot(driver, f"application_error_{index}")
        
        # Try to exit any modals
        try:
            close_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Dismiss'], button[aria-label='Close']")
            for button in close_buttons:
                if button.is_displayed():
                    button.click()
                    logger.info("Closed error modal")
                    time.sleep(2)
                    
                    # Check for "Discard" button if prompted
                    discard_buttons = driver.find_elements(By.XPATH, "//button[contains(.,'Discard')]")
                    for discard_button in discard_buttons:
                        if discard_button.is_displayed():
                            discard_button.click()
                            logger.info("Clicked discard button")
                            time.sleep(2)
                            break
                    break
        except:
            pass
            
        return False

def handle_job_search(driver, search):
    """Handle a complete job search and application process"""
    try:
        logger.info(f"Starting search for {search['keywords']} in {search['location']}")
        
        # Search for jobs
        if not search_jobs_directly(driver, search["keywords"], search["location"]):
            logger.warning("Skipping search due to error")
            return 0
        
        # Get job listings
        job_cards = get_job_listings(driver)
        if not job_cards:
            logger.warning("No job listings found")
            return 0
        
        applied_count = 0
        # Apply to jobs (limit to MAX_APPLICATIONS per search)
        jobs_to_apply = min(len(job_cards), MAX_APPLICATIONS)
        
        for i in range(jobs_to_apply):
            try:
                logger.info(f"\nAttempting job application {i+1}/{jobs_to_apply}")
                if apply_to_job(driver, job_cards[i], i):
                    applied_count += 1
                
                # Random wait between applications
                wait_time = random.uniform(5, 8)
                logger.info(f"Waiting {wait_time:.1f} seconds before next application")
                time.sleep(wait_time)
                
                # Refresh job cards after each application as the page might have changed
                if i < jobs_to_apply - 1:  # No need to refresh on last application
                    try:
                        # Refresh the search page
                        current_url = driver.current_url
                        driver.get(current_url)
                        random_wait()
                        
                        # Get updated job cards
                        job_cards = get_job_listings(driver)
                        if not job_cards:
                            logger.warning("Could not refresh job listings, stopping this search")
                            break
                    except Exception as refresh_error:
                        logger.error(f"Error refreshing job cards: {str(refresh_error)}")
                        break
            except Exception as application_error:
                logger.error(f"Error in application #{i+1}: {str(application_error)}")
                continue
                
        return applied_count
    except Exception as e:
        logger.error(f"Error in job search: {str(e)}")
        return 0

def main():
    """Main function to run the job application automation"""
    driver = None
    applied_count = 0
    start_time = datetime.now()
    
    try:
        logger.info("Starting LinkedIn job application automation")
        logger.info(f"Starting at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Setup the WebDriver
        driver = setup_driver()
        
        # Login to LinkedIn
        if not login_to_linkedin(driver):
            logger.error("Failed to login to LinkedIn, aborting process")
            return
        
        # List of job searches to perform
        job_searches = [
            {"keywords": "Software Engineer", "location": "Remote"},
            {"keywords": "Python Developer", "location": "New York"},
            {"keywords": "Python Developer", "location": "Remote"}
        ]
        
        # Process each search
        for search in job_searches:
            search_applied_count = handle_job_search(driver, search)
            applied_count += search_applied_count
            
            # Take a short break between searches
            if search != job_searches[-1]:  # If not the last search
                wait_time = random.uniform(10, 15)
                logger.info(f"Taking a {wait_time:.1f} second break before next search")
                time.sleep(wait_time)
    
    except Exception as e:
        logger.error(f"Application process failed: {str(e)}")
        if driver:
            take_screenshot(driver, "process_error")
    
    finally:
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("\n=========== Job Application Session Summary ===========")
        logger.info(f"Session completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Total duration: {duration}")
        logger.info(f"Total jobs applied to: {applied_count}")
        
        if driver:
            driver.quit()
            logger.info("Browser closed successfully")

def verify_linkedin_credentials():
    """Verify that the LinkedIn credentials are properly set"""
    if LINKEDIN_EMAIL == "your_email@example.com" or LINKEDIN_PASSWORD == "your_password":
        logger.error("ERROR: You need to update the LinkedIn credentials in the script!")
        logger.error("Please replace 'your_email@example.com' and 'your_password' with your actual LinkedIn credentials.")
        return False
    return True

if __name__ == "__main__":
    # Check if credentials are set before running
    if verify_linkedin_credentials():
        main()
    else:
        print("Please update your LinkedIn credentials in the script before running.")