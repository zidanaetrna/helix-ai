import os
import requests
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
from colorama import init, Fore, Style
import json
from dateutil.parser import isoparse

init()
# Emoji 
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

TIMESTAMP_FILE = "last_submission.txt"
DAILY_CLAIM_FILE = "last_daily_claim.txt"

PROJECT_NAME = os.getenv("PROJECT_NAME", "Synthelix Ai")
CREATOR_NAME = os.getenv("CREATOR_NAME", "aetrna")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_interface():
    clear_screen()
    print(f"{Fore.MAGENTA}================ {PROJECT_NAME} Auto-bot =========================={Style.RESET_ALL}")
    print("")
    ascii_lines = [
        "..%%%%...%%%%%%..%%%%%%..%%%%%...%%..%%...%%%%..",
        ".%%..%%..%%........%%....%%..%%..%%%.%%..%%..%%.",
        ".%%%%%%..%%%%......%%....%%%%%...%%.%%%..%%%%%%.",
        ".%%..%%..%%........%%....%%..%%..%%..%%..%%..%%.",
        ".%%..%%..%%%%%%....%%....%%..%%..%%..%%..%%..%%.",
        "................................................"
    ]
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    
    for i, line in enumerate(ascii_lines):
        print(f"{colors[i]}{line}{Style.RESET_ALL}")
    
    print("")
    print(f"{Fore.MAGENTA}================= Created by: {CREATOR_NAME} =========================={Style.RESET_ALL}")
    print("")

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

# Base configuration
BASE_URL = "https://dashboard.synthelix.io"
NODE_START_ENDPOINT = f"{BASE_URL}/api/node/start"
POINTS_ENDPOINT = f"{BASE_URL}/api/get/points"
SESSION_ENDPOINT = f"{BASE_URL}/api/auth/session"
DAILY_CLAIM_ENDPOINT = f"{BASE_URL}/api/rew/dailypoints"

# Headers
def get_headers():
    return {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,id;q=0.8,zh-CN;q=0.7,zh;q=0.6",
        "content-type": "application/json",
        "origin": BASE_URL,
        "referer": f"{BASE_URL}/",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
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

def save_daily_claim_timestamp(timestamp):
    with open(DAILY_CLAIM_FILE, "w") as f:
        f.write(str(timestamp))

def load_daily_claim_timestamp():
    if os.path.exists(DAILY_CLAIM_FILE):
        with open(DAILY_CLAIM_FILE, "r") as f:
            return float(f.read().strip())
    return 0  

def claim_daily_points(cookies):
    print(f"{CLAIM} {Fore.CYAN}Attempting to claim daily points...{Style.RESET_ALL}")
    try:
        response = requests.post(
            DAILY_CLAIM_ENDPOINT,
            headers=get_headers(),
            cookies=cookies,
            json={}  
        )
        if response.status_code == 200:
            data = response.json()
            points = data.get("points", 0)
            last_daily_claim = data.get("lastDailyClaim", None)
            referral_bonus = data.get("referralBonusApplied", False)
            
            if last_daily_claim:
                last_claim_time = isoparse(last_daily_claim)
                last_claim_timestamp = last_claim_time.timestamp()
                save_daily_claim_timestamp(last_claim_timestamp)
            
            print(f"{SUCCESS} {Fore.GREEN}Daily points claimed successfully!{Style.RESET_ALL}")
            print(f"{INFO} Points: {points}")
            print(f"{INFO} Referral Bonus Applied: {referral_bonus}")
            print(f"{INFO} Last Daily Claim: {last_daily_claim}")
            return True
        else:
            if response.status_code == 400:
                print(f"{ERROR} {Fore.RED}Daily points already claimed or not available.{Style.RESET_ALL}")
                print(f"{INFO} Response: {response.text}")
                save_daily_claim_timestamp(time.time())
            else:
                print(f"{ERROR} {Fore.RED}Failed to claim daily points. Status code: {response.status_code}{Style.RESET_ALL}")
                print(f"{INFO} Response: {response.text}")
            return False
    except Exception as e:
        print(f"{ERROR} {Fore.RED}Error claiming daily points: {str(e)}{Style.RESET_ALL}")
        save_daily_claim_timestamp(time.time())
        return False

def can_claim_daily():
    last_claim_timestamp = load_daily_claim_timestamp()
    current_time = time.time()
    return (current_time - last_claim_timestamp) >= (24 * 60 * 60)  # 24 hours in seconds

def time_until_next_claim():
    last_claim_timestamp = load_daily_claim_timestamp()
    next_claim_time = last_claim_timestamp + (24 * 60 * 60)
    return datetime.fromtimestamp(next_claim_time)

def get_points(cookies):
    print(f"{POINTS} {Fore.CYAN}Fetching points...{Style.RESET_ALL}")
    try:
        response = requests.get(
            POINTS_ENDPOINT,
            headers=get_headers(),
            cookies=cookies
        )
        if response.status_code in [200, 304]:
            if response.status_code == 200:
                points_data = response.json()
                print(f"{SUCCESS} {Fore.GREEN}Points fetched: {points_data}{Style.RESET_ALL}")
            else:
                print(f"{CHECK} {Fore.YELLOW}Points unchanged (304 Not Modified){Style.RESET_ALL}")
        else:
            print(f"{ERROR} {Fore.RED}Failed to fetch points. Status code: {response.status_code}{Style.RESET_ALL}")
            print(f"{INFO} Response: {response.text}")
    except Exception as e:
        print(f"{ERROR} {Fore.RED}Error fetching points: {str(e)}{Style.RESET_ALL}")

def check_status(cookies):
    print(f"{INFO} {Fore.CYAN}Checking status...{Style.RESET_ALL}")
    try:
        response = requests.get(
            SESSION_ENDPOINT,
            headers=get_headers(),
            cookies=cookies
        )
        if response.status_code == 200:
            print(f"{ONLINE} {Fore.GREEN}Status: Online{Style.RESET_ALL}")
            return True
        else:
            print(f"{OFFLINE} {Fore.RED}Status: Offline (Status code: {response.status_code}){Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{ERROR} {Fore.RED}Error checking status: {str(e)}{Style.RESET_ALL}")
        return False

def start_node(cookies):
    print(f"{NODE} {Fore.CYAN}Starting the node...{Style.RESET_ALL}")
    try:
        response = requests.post(
            NODE_START_ENDPOINT,
            headers=get_headers(),
            cookies=cookies
        )
        if response.status_code == 200:
            print(f"{SUCCESS} {Fore.GREEN}Node started successfully!{Style.RESET_ALL}")
            print(f"{INFO} Response: {response.text}")
            save_timestamp()
            return True
        else:
            print(f"{ERROR} {Fore.RED}Failed to start node. Status code: {response.status_code}{Style.RESET_ALL}")
            print(f"{INFO} Response: {response.text}")
            return False
    except Exception as e:
        print(f"{ERROR} {Fore.RED}Error starting node: {str(e)}{Style.RESET_ALL}")
        return False

def connect_wallet(wallet_address, project_id, cookies):
    WALLET_CONNECT_ENDPOINT = f"https://rpc.walletconnect.org/v1/profile/reverse/{wallet_address}"
    print(f"{WALLET} {Fore.CYAN}Connecting wallet...{Style.RESET_ALL}")
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
            cookies=cookies
        )
        if response.status_code == 200:
            print(f"{SUCCESS} {Fore.GREEN}Wallet connected successfully!{Style.RESET_ALL}")
            print(f"{INFO} Response: {response.json()}")
            return True
        else:
            print(f"{ERROR} {Fore.RED}Failed to connect wallet. Status code: {response.status_code}{Style.RESET_ALL}")
            print(f"{INFO} Response: {response.text}")
            return False
    except Exception as e:
        print(f"{ERROR} {Fore.RED}Error connecting wallet: {str(e)}{Style.RESET_ALL}")
        return False

def save_timestamp():
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(str(time.time()))

def load_timestamp():
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, "r") as f:
            return float(f.read().strip())
    return 0  

def should_submit():
    last_submission = load_timestamp()
    current_time = time.time()
    return (current_time - last_submission) >= (24 * 60 * 60)  

def run_bot(session_token, project_id, wallet_address):
    cookies = get_cookies(session_token)
    
    while True:
        print(f"\n{INFO} {Fore.MAGENTA}--- Bot Cycle Start ---{Style.RESET_ALL}")
        
        is_online = check_status(cookies)
        
        get_points(cookies)
        
        if can_claim_daily():
            if is_online:
                claim_daily_points(cookies)
            else:
                print(f"{OFFLINE} {Fore.RED}Cannot claim daily points while offline.{Style.RESET_ALL}")
        else:
            next_claim = time_until_next_claim()
            print(f"{WAITING} {Fore.YELLOW}Next daily claim at: {next_claim.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        
        if not is_online:
            print(f"{OFFLINE} {Fore.RED}Offline detected. Retrying node submission...{Style.RESET_ALL}")
            if start_node(cookies):
                print(f"{CHECK} {Fore.GREEN}Node submitted after offline retry.{Style.RESET_ALL}")
            time.sleep(60)  
            continue
        
        if should_submit():
            connect_wallet(wallet_address, project_id, cookies)
            if start_node(cookies):
                print(f"{CHECK} {Fore.GREEN}Node submitted successfully (24-hour cycle).{Style.RESET_ALL}")
            else:
                print(f"{ERROR} {Fore.RED}Node submission failed. Will retry in 24 hours.{Style.RESET_ALL}")
                save_timestamp()  
        else:
            next_submission = datetime.fromtimestamp(load_timestamp() + 24 * 60 * 60)
            print(f"{WAITING} {Fore.YELLOW}Next node submission at: {next_submission.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        
        print(f"{WAITING} {Fore.CYAN}Sleeping for 5 minutes...{Style.RESET_ALL}")
        time.sleep(300)

if __name__ == "__main__":
    print(f"{INFO} {Fore.MAGENTA}Starting Synthetix AI Bot...{Style.RESET_ALL}")

    session_token, project_id, wallet_address = load_env()

    display_interface()

    print(f"{WALLET} {Fore.YELLOW}Using wallet address: {wallet_address}{Style.RESET_ALL}")

    # Start the bot loop
    run_bot(session_token, project_id, wallet_address)