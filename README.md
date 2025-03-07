# Wazuh Automation Project

This repository contains a Wazuh automation project that includes a Telegram bot with two modes of operation.

## Features

### 🛠 Command Mode
- Operates based on commands entered in the Telegram chat.
- Provides information about agents in different formats.

### 🤖 Automatic Mode
- Sends data to the repository every minute.
- Exports and sends log files in Excel format.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Nikiitanskiy/wazuh-automation.git
   cd wazuh-automation
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables for Telegram bot authentication.

## Usage
- Run the bot:
  ```bash
  python wazuhbot.py
  ```
- Use commands in the Telegram chat to interact with the bot.


