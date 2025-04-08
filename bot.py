import os
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
from colorama import init, Fore, Style
import json
from dateutil.parser import isoparse
import random

# Initialize colorama for colored output
init()

# Emoji constants
CHECK = "✅"
ERROR = "❌"
INFO = "ℹ️"
INPUT = "➡️"
SUCCESS = "🎉"
WALLET = "💼"
NODE = "🚀"
POINTS = "⭐"
ONLINE = "🟢"
OFFLINE = "🔴"
WAITING = "⏳"
CLAIM = "🏆"
RATE_LIMIT = "⏰"
PROXY = "🔄"

# Files to store timestamps and proxies
QUIET_PERIOD_FILE = "last_quiet_period.txt"  # File for tracking the 25-hour quiet period
PROXY_FILE = "proxy.txt"

# Project and creator defaults (can be overridden by .env)
PROJECT_NAME = os.getenv("PROJECT_NAME", "Synthelix Ai")
CREATOR_NAME = os.getenv("CREATOR_NAME", "aetrna")

# Sleep time for the quiet period (25 hours)
QUIET_PERIOD_SECONDS = 25 * 60 * 60  # 25 hours
RATE_LIMIT_SLEEP_SECONDS = 3600  # 1 hour if rate-limited

# Proxy list and current proxy index
proxies_list = []
current_proxy_index = 0

# Function to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to display the ASCII art interface with colorful effect
def display_interface():
    clear_screen()
    print(f"{Fore.MAGENTA}================ {PROJECT_NAME} Auto-bot =========================={Style.RESET_ALL}")
    print("")
    # Original ASCII art with rainbow colors for each line
    ascii_lines = [
        "..%%%%...%%%%%%..%%%%%%..%%%%%...%%..%%...%%%%..",
        ".%%..%%..%%........%%....%%..%%..%%%.%%..%%..%%.",
        ".%%%%%%..%%%%......%%....%%%%%...%%.%%%..%%%%%%.",
        ".%%..%%..%%........%%....%%..%%..%%..%%..%%..%%.",
        ".%%..%%..%%%%%%....%%....%%..%%..%%..%%..%%..%%.",
        "................................................"
    ]
    # Colors for each line (rainbow effect)
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    
    # Print each line with its corresponding color
    for i, line in enumerate(ascii_lines):
        print(f"{colors[i]}{line}{Style.RESET_ALL}")
    
    print("")
    print(f"{Fore.MAGENTA}================= Created by: {CREATOR_NAME} =========================={Style.RESET_ALL}")
    print("")

# Function to interactively set up .env file
def setup_env():
    print(f"{INFO} {Fore.CYAN}Setting up your .env file...{Style.RESET_ALL}")
    env_file = ".env"
    
    session_token = input(f"{INPUT} {Fore.GREEN}Enter your session token (or Bearer token): {Style.RESET_ALL}")
    project_id = input(f"{INPUT} {Fore.GREEN}Enter your project ID: {Style.RESET_ALL}")
    wallet_address = input(f"{INPUT} {Fore.GREEN}Enter your wallet address: {Style.RESET_ALL}")

    set_key(env_file, "SESSION_TOKEN", session_token)
    set_key(env_file, "PROJECT_ID", project_id)
    set_key(env_file, "WALLET_ADDRESS", wallet_address)
    
    print(f"{CHECK} {Fore.YELLOW}.env file created/updated at {os.path.abspath(env_file)}{Style.RESET_ALL}")
    return session_token, project_id, wallet_address

# Function to update credentials on 403 error (keep wallet address unchanged)
def update_credentials(wallet_address):
    print(f"{ERROR} {Fore.RED}Session token or project ID expired, please re-input your credentials!{Style.RESET_ALL}")
    env_file = ".env"
    
    session_token = input(f"{INPUT} {Fore.GREEN}Your new session (Bearer): {Style.RESET_ALL}")
    project_id = input(f"{INPUT} {Fore.GREEN}Your new Project ID: {Style.RESET_ALL}")

    # Update .env file with new session token and project ID, preserve wallet address
    set_key(env_file, "SESSION_TOKEN", session_token)
    set_key(env_file, "PROJECT_ID", project_id)
    set_key(env_file, "WALLET_ADDRESS", wallet_address)  # Ensure wallet address remains unchanged
    
    print(f"{CHECK} {Fore.YELLOW}.env file updated with new credentials{Style.RESET_ALL}")
    return session_token, project_id

# Load .env variables
def load_env():
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"{ERROR} {Fore.RED}No .env file found. Let's set it up!{Style.RESET_ALL}")
        return setup_env()
    
    load_dotenv(env_file)
    session_token = os.getenv("SESSION_TOKEN")
    project_id = os.getenv("PROJECT_ID")
    wallet_address = os.getenv("WALLET_ADDRESS")
    
    if not all([session_token, project_id, wallet_address]):
        print(f"{ERROR} {Fore.RED}.env file is missing some required info. Let's set it up again!{Style.RESET_ALL}")
        return setup_env()
    
    print(f"{CHECK} {Fore.YELLOW}Loaded configuration from .env{Style.RESET_ALL}")
    return session_token, project_id, wallet_address

# Load proxies from proxy.txt or prompt user to input proxies
def load_proxies():
    global proxies_list
    if not os.path.exists(PROXY_FILE):
        print(f"{ERROR} {Fore.RED}No proxy.txt file found. Let's set up your proxies!{Style.RESET_ALL}")
        print(f"{INFO} {Fore.CYAN}Enter your proxies (one per line, format: [http://]username:password@host:port). Press Enter twice to finish.{Style.RESET_ALL}")
        
        proxies_input = []
        while True:
            proxy = input(f"{INPUT} {Fore.GREEN}Enter your proxy (or press Enter to finish): {Style.RESET_ALL}")
            if proxy == "":
                break
            proxies_input.append(proxy)
        
        if not proxies_input:
            print(f"{ERROR} {Fore.RED}No proxies provided. Exiting.{Style.RESET_ALL}")
            return False
        
        # Save proxies to proxy.txt
        with open(PROXY_FILE, "w") as f:
            for proxy in proxies_input:
                f.write(proxy + "\n")
        print(f"{CHECK} {Fore.YELLOW}Proxies saved to proxy.txt{Style.RESET_ALL}")
    
    # Load proxies from proxy.txt
    with open(PROXY_FILE, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line:
                # Handle both formats: http://username:password@host:port/ and username:password@host:port
                if line.startswith("http://"):
                    proxy_url = line
                else:
                    proxy_url = f"http://{line}"
                proxies_list.append({
                    "http": proxy_url,
                    "https": proxy_url
                })
    
    if not proxies_list:
        print(f"{ERROR} {Fore.RED}No valid proxies found in proxy.txt.{Style.RESET_ALL}")
        return False
    
    print(f"{PROXY} {Fore.YELLOW}Loaded {len(proxies_list)} proxies from proxy.txt{Style.RESET_ALL}")
    return True

# Rotate to the next proxy
def rotate_proxy():
    global current_proxy_index
    current_proxy_index = (current_proxy_index + 1) % len(proxies_list)
    print(f"{PROXY} {Fore.YELLOW}Rotated to proxy: {proxies_list[current_proxy_index]['http']}{Style.RESET_ALL}")

# Get current proxy
def get_current_proxy():
    if not proxies_list:
        return None
    return proxies_list[current_proxy_index]

# Base configuration
BASE_URL = "https://dashboard.synthelix.io"
NODE_START_ENDPOINT = f"{BASE_URL}/api/node/start"
POINTS_ENDPOINT = f"{BASE_URL}/api/get/points"
SESSION_ENDPOINT = f"{BASE_URL}/api/auth/session"
DAILY_CLAIM_ENDPOINT = f"{BASE_URL}/api/rew/dailypoints"

# Headers (mimicking a browser more closely)
def get_headers():
    return {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,id;q=0.8,zh-CN;q=0.7,zh;q=0.6",
        "content-type": "application/json",
        "origin": BASE_URL,
        "referer": f"{BASE_URL}/dashboard",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

# Cookies template
def get_cookies(session_token):
    return {
        "__Secure-next-auth.session-token": session_token,
        "_ga": "GA1.1.314468642.1744041690",
        "referralCode": "yVG72ToK",
        "__Host-next-auth.csrf-token": "31c2a445c841aaea264956aa41db848fa79c684a281fe43c4d029f29365f9e4f|b9c7c116f647d7124fe5aa988e7a06fb30ec823ae8d7c5db68d88c8fbabee4ae",
        "_ga_5LJ6Z6C43G": "GS1.1.1744041689.1.1.1744042519.0.0.0",
        "__Secure-next-auth.callback-url": "https://dashboard.synthelix.io/"
    }

# Function to save last quiet period timestamp
def save_quiet_period_timestamp():
    with open(QUIET_PERIOD_FILE, "w") as f:
        f.write(str(time.time()))

# Function to load last quiet period timestamp
def load_quiet_period_timestamp():
    if os.path.exists(QUIET_PERIOD_FILE):
        with open(QUIET_PERIOD_FILE, "r") as f:
            return float(f.read().strip())
    return 0  # If no timestamp exists, assume it's the first run

# Function to check if 25 hours have passed since last quiet period
def should_perform_actions():
    last_quiet_period = load_quiet_period_timestamp()
    current_time = time.time()
    return (current_time - last_quiet_period) >= QUIET_PERIOD_SECONDS

# Function to get time until next action cycle
def time_until_next_action_cycle():
    last_quiet_period = load_quiet_period_timestamp()
    next_action_time = last_quiet_period + QUIET_PERIOD_SECONDS
    return datetime.fromtimestamp(next_action_time)

# Function to claim daily points
def claim_daily_points(cookies, wallet_address):
    print(f"{CLAIM} {Fore.CYAN}Attempting to claim daily points...{Style.RESET_ALL}")
    proxy = get_current_proxy()
    try:
        response = requests.post(
            DAILY_CLAIM_ENDPOINT,
            headers=get_headers(),
            cookies=cookies,
            json={},
            proxies=proxy,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            points = data.get("points", 0)
            last_daily_claim = data.get("lastDailyClaim", None)
            referral_bonus = data.get("referralBonusApplied", False)
            
            print(f"{SUCCESS} {Fore.GREEN}Daily points claimed successfully!{Style.RESET_ALL}")
            print(f"{INFO} Points: {points}")
            print(f"{INFO} Referral Bonus Applied: {referral_bonus}")
            print(f"{INFO} Last Daily Claim: {last_daily_claim}")
            return True, 0, None, None  # No sleep time needed here; main loop will handle the 25-hour sleep
        else:
            if response.status_code == 400:
                print(f"{ERROR} {Fore.RED}Daily points already claimed or not available.{Style.RESET_ALL}")
                return False, 0, None, None
            elif response.status_code == 429:
                print(f"{RATE_LIMIT} {Fore.RED}Rate limit exceeded (429). Retrying after 1 hour...{Style.RESET_ALL}")
                rotate_proxy()
                return False, RATE_LIMIT_SLEEP_SECONDS, None, None
            elif response.status_code == 403:
                new_session_token, new_project_id = update_credentials(wallet_address)
                return False, 0, new_session_token, new_project_id
            else:
                print(f"{ERROR} {Fore.RED}Failed to claim daily points. Status code: {response.status_code}{Style.RESET_ALL}")
                print(f"{INFO} Response: {response.text}")
                return False, 0, None, None
    except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"{ERROR} {Fore.RED}Proxy error: {str(e)}. Rotating proxy...{Style.RESET_ALL}")
        rotate_proxy()
        return False, 0, None, None
    except Exception as e:
        print(f"{ERROR} {Fore.RED}Error claiming daily points: {str(e)}{Style.RESET_ALL}")
        return False, 0, None, None

# Function to get points
def get_points(cookies, wallet_address):
    print(f"{POINTS} {Fore.CYAN}Fetching points...{Style.RESET_ALL}")
    proxy = get_current_proxy()
    try:
        response = requests.get(
            POINTS_ENDPOINT,
            headers=get_headers(),
            cookies=cookies,
            proxies=proxy,
            timeout=10
        )
        if response.status_code in [200, 304]:
            if response.status_code == 200:
                points_data = response.json()
                print(f"{SUCCESS} {Fore.GREEN}Points fetched: {points_data}{Style.RESET_ALL}")
            else:
                print(f"{CHECK} {Fore.YELLOW}Points unchanged (304 Not Modified){Style.RESET_ALL}")
            return True, 0, None, None  # No sleep time needed here; main loop will handle the 25-hour sleep
        else:
            if response.status_code == 429:
                print(f"{RATE_LIMIT} {Fore.RED}Rate limit exceeded (429). Retrying after 1 hour...{Style.RESET_ALL}")
                rotate_proxy()
                return False, RATE_LIMIT_SLEEP_SECONDS, None, None
            elif response.status_code == 403:
                new_session_token, new_project_id = update_credentials(wallet_address)
                return False, 0, new_session_token, new_project_id
            else:
                print(f"{ERROR} {Fore.RED}Failed to fetch points. Status code: {response.status_code}{Style.RESET_ALL}")
                print(f"{INFO} Response: {response.text}")
                return False, 0, None, None
    except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"{ERROR} {Fore.RED}Proxy error: {str(e)}. Rotating proxy...{Style.RESET_ALL}")
        rotate_proxy()
        return False, 0, None, None
    except Exception as e:
        print(f"{ERROR} {Fore.RED}Error fetching points: {str(e)}{Style.RESET_ALL}")
        return False, 0, None, None

# Function to check online status
def check_status(cookies, wallet_address):
    print(f"{INFO} {Fore.CYAN}Checking status...{Style.RESET_ALL}")
    proxy = get_current_proxy()
    try:
        response = requests.get(
            SESSION_ENDPOINT,
            headers=get_headers(),
            cookies=cookies,
            proxies=proxy,
            timeout=10
        )
        if response.status_code == 200:
            print(f"{ONLINE} {Fore.GREEN}Status: Online{Style.RESET_ALL}")
            return True, 0, None, None  # No sleep time needed here; main loop will handle the 25-hour sleep
        else:
            if response.status_code == 429:
                print(f"{RATE_LIMIT} {Fore.RED}Rate limit exceeded (429). Retrying after 1 hour...{Style.RESET_ALL}")
                rotate_proxy()
                return False, RATE_LIMIT_SLEEP_SECONDS, None, None
            elif response.status_code == 403:
                new_session_token, new_project_id = update_credentials(wallet_address)
                return False, 0, new_session_token, new_project_id
            else:
                print(f"{OFFLINE} {Fore.RED}Status: Offline (Status code: {response.status_code}){Style.RESET_ALL}")
                return False, 0, None, None
    except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"{ERROR} {Fore.RED}Proxy error: {str(e)}. Rotating proxy...{Style.RESET_ALL}")
        rotate_proxy()
        return False, 0, None, None
    except Exception as e:
        print(f"{ERROR} {Fore.RED}Error checking status: {str(e)}{Style.RESET_ALL}")
        return False, 0, None, None

# Function to start the node
def start_node(cookies, wallet_address):
    print(f"{NODE} {Fore.CYAN}Starting the node...{Style.RESET_ALL}")
    proxy = get_current_proxy()
    try:
        response = requests.post(
            NODE_START_ENDPOINT,
            headers=get_headers(),
            cookies=cookies,
            proxies=proxy,
            timeout=10
        )
        if response.status_code == 200:
            print(f"{SUCCESS} {Fore.GREEN}Node started successfully!{Style.RESET_ALL}")
            print(f"{INFO} Response: {response.text}")
            return True, 0, None, None  # No sleep time needed here; main loop will handle the 25-hour sleep
        else:
            if response.status_code == 429:
                print(f"{RATE_LIMIT} {Fore.RED}Rate limit exceeded (429). Retrying after 1 hour...{Style.RESET_ALL}")
                rotate_proxy()
                return False, RATE_LIMIT_SLEEP_SECONDS, None, None
            elif response.status_code == 403:
                new_session_token, new_project_id = update_credentials(wallet_address)
                return False, 0, new_session_token, new_project_id
            else:
                print(f"{ERROR} {Fore.RED}Failed to start node. Status code: {response.status_code}{Style.RESET_ALL}")
                print(f"{INFO} Response: {response.text}")
                return False, 0, None, None
    except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"{ERROR} {Fore.RED}Proxy error: {str(e)}. Rotating proxy...{Style.RESET_ALL}")
        rotate_proxy()
        return False, 0, None, None
    except Exception as e:
        print(f"{ERROR} {Fore.RED}Error starting node: {str(e)}{Style.RESET_ALL}")
        return False, 0, None, None

# Function to connect wallet
def connect_wallet(wallet_address, project_id, cookies):
    WALLET_CONNECT_ENDPOINT = f"https://rpc.walletconnect.org/v1/profile/reverse/{wallet_address}"
    print(f"{WALLET} {Fore.CYAN}Connecting wallet...{Style.RESET_ALL}")
    proxy = get_current_proxy()
    try:
        params = {
            "sender": wallet_address,
            "projectId": project_id,
            "apiVersion": "2"
        }
        response = requests.get(
            WALLET_CONNECT_ENDPOINT,
            headers=get_headers(),
            params=params,
            cookies=cookies,
            proxies=proxy,
            timeout=10
        )
        if response.status_code == 200:
            print(f"{SUCCESS} {Fore.GREEN}Wallet connected successfully!{Style.RESET_ALL}")
            print(f"{INFO} Response: {response.json()}")
            return True, 0, None, None  # No sleep time needed here; main loop will handle the 25-hour sleep
        else:
            if response.status_code == 429:
                print(f"{RATE_LIMIT} {Fore.RED}Rate limit exceeded (429). Retrying after 1 hour...{Style.RESET_ALL}")
                rotate_proxy()
                return False, RATE_LIMIT_SLEEP_SECONDS, None, None
            elif response.status_code == 403:
                new_session_token, new_project_id = update_credentials(wallet_address)
                return False, 0, new_session_token, new_project_id
            else:
                print(f"{ERROR} {Fore.RED}Failed to connect wallet. Status code: {response.status_code}{Style.RESET_ALL}")
                print(f"{INFO} Response: {response.text}")
                return False, 0, None, None
    except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
        print(f"{ERROR} {Fore.RED}Proxy error: {str(e)}. Rotating proxy...{Style.RESET_ALL}")
        rotate_proxy()
        return False, 0, None, None
    except Exception as e:
        print(f"{ERROR} {Fore.RED}Error connecting wallet: {str(e)}{Style.RESET_ALL}")
        return False, 0, None, None

# Main bot loop
def run_bot(session_token, project_id, wallet_address):
    cookies = get_cookies(session_token)
    
    while True:
        print(f"\n{INFO} {Fore.MAGENTA}--- Bot Cycle Start ---{Style.RESET_ALL}")
        
        # Check if 25 hours have passed since the last quiet period
        if not should_perform_actions():
            next_action = time_until_next_action_cycle()
            time_to_sleep = (next_action - datetime.now()).total_seconds()
            print(f"{WAITING} {Fore.YELLOW}Next action cycle at: {next_action.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
            print(f"{WAITING} {Fore.CYAN}Sleeping for {time_to_sleep // 3600:.1f} hours...{Style.RESET_ALL}")
            time.sleep(time_to_sleep)
            continue
        
        # If 25 hours have passed, perform all actions in one cycle
        # Check status
        is_online, sleep_seconds, new_session_token, new_project_id = check_status(cookies, wallet_address)
        if new_session_token and new_project_id:
            session_token, project_id = new_session_token, new_project_id
            cookies = get_cookies(session_token)
        if sleep_seconds > 0:  # Rate limit encountered
            print(f"{WAITING} {Fore.CYAN}Sleeping for {sleep_seconds // 60} minutes due to rate limit...{Style.RESET_ALL}")
            time.sleep(sleep_seconds)
            continue
        
        # Fetch points
        success, sleep_seconds, new_session_token, new_project_id = get_points(cookies, wallet_address)
        if new_session_token and new_project_id:
            session_token, project_id = new_session_token, new_project_id
            cookies = get_cookies(session_token)
        if sleep_seconds > 0:  # Rate limit encountered
            print(f"{WAITING} {Fore.CYAN}Sleeping for {sleep_seconds // 60} minutes due to rate limit...{Style.RESET_ALL}")
            time.sleep(sleep_seconds)
            continue
        
        # Claim daily points if online
        if is_online:
            success, sleep_seconds, new_session_token, new_project_id = claim_daily_points(cookies, wallet_address)
            if new_session_token and new_project_id:
                session_token, project_id = new_session_token, new_project_id
                cookies = get_cookies(session_token)
            if sleep_seconds > 0:  # Rate limit encountered
                print(f"{WAITING} {Fore.CYAN}Sleeping for {sleep_seconds // 60} minutes due to rate limit...{Style.RESET_ALL}")
                time.sleep(sleep_seconds)
                continue
        else:
            print(f"{OFFLINE} {Fore.RED}Cannot claim daily points while offline.{Style.RESET_ALL}")
        
        # Submit node (connect wallet and start node)
        success, sleep_seconds, new_session_token, new_project_id = connect_wallet(wallet_address, project_id, cookies)
        if new_session_token and new_project_id:
            session_token, project_id = new_session_token, new_project_id
            cookies = get_cookies(session_token)
        if sleep_seconds > 0:  # Rate limit encountered
            print(f"{WAITING} {Fore.CYAN}Sleeping for {sleep_seconds // 60} minutes due to rate limit...{Style.RESET_ALL}")
            time.sleep(sleep_seconds)
            continue
        
        success, sleep_seconds, new_session_token, new_project_id = start_node(cookies, wallet_address)
        if new_session_token and new_project_id:
            session_token, project_id = new_session_token, new_project_id
            cookies = get_cookies(session_token)
        if sleep_seconds > 0:  # Rate limit encountered
            print(f"{WAITING} {Fore.CYAN}Sleeping for {sleep_seconds // 60} minutes due to rate limit...{Style.RESET_ALL}")
            time.sleep(sleep_seconds)
            continue
        
        if success:
            print(f"{CHECK} {Fore.GREEN}Node submitted successfully.{Style.RESET_ALL}")
        else:
            print(f"{ERROR} {Fore.RED}Node submission failed.{Style.RESET_ALL}")
        
        # Update the quiet period timestamp after all actions are complete
        save_quiet_period_timestamp()
        
        # Sleep for the full 25 hours before the next cycle
        next_action = time_until_next_action_cycle()
        print(f"{WAITING} {Fore.YELLOW}Next action cycle at: {next_action.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{WAITING} {Fore.CYAN}Sleeping for {QUIET_PERIOD_SECONDS // 3600} hours...{Style.RESET_ALL}")
        time.sleep(QUIET_PERIOD_SECONDS)

# Main execution
if __name__ == "__main__":
    print(f"{INFO} {Fore.MAGENTA}Starting Synthetix AI Bot...{Style.RESET_ALL}")

    # Load or setup .env variables
    session_token, project_id, wallet_address = load_env()

    # Load proxies
    if not load_proxies():
        print(f"{ERROR} {Fore.RED}Exiting due to proxy loading failure.{Style.RESET_ALL}")
        exit(1)

    # Display the interface after loading/setup (only once)
    display_interface()

    # Display loaded wallet address
    print(f"{WALLET} {Fore.YELLOW}Using wallet address: {wallet_address}{Style.RESET_ALL}")

    # Start the bot loop
    run_bot(session_token, project_id, wallet_address)