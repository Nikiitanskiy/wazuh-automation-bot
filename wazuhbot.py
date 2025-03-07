from dotenv import dotenv_values
import requests
import urllib3
import base64
import json, csv
import pandas as pd
from io import StringIO
from telebot import TeleBot
import datetime
import os
import schedule
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time

class WazuhBot:
    def __init__(self, username, password, base_url, telegram_token, master_id, switcher):
        self.username = username
        self.password = password
        self.base_url = base_url
        self.jwt_token = self._gettoken()
        self.bot  = TeleBot(telegram_token)
        self.master_id = master_id
        self.switcher = switcher
    
    def _gettoken(self):
        try:
            basic_auth = (f"{self.username}:{self.password}").encode()
            headers = {
                "Content-Type": "application/json",
                "Authorization" : f"Basic {base64.b64encode(basic_auth).decode('utf-8')}"
            }
            
            response = requests.post(
                url=self.base_url+"/security/user/authenticate",
                headers=headers,
                verify=False
            )
            response.raise_for_status()
            token = response.json()['data']['token']
            return token
        except Exception as e:
            print(f'[!]ERROR was occured with description : {e}')

    def get_start(self):
        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            print(message)
            self.bot.reply_to(message, "Hello! It`s my project for WAZUH API")

    # def check_master_id(self, message, func()):
    #     if message.chat.id == int(self.master_id):
    #         pass

    def generate_agents(self, format, message):
        data = self.get_agents_active()
        time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
        if format == "json":
            filename = f"Agents_Exports{time}.json"
            data.to_json(filename, indent=4)
        elif format == "csv":
            filename = f"Agents_Exports{time}.csv"
            data.to_csv(filename) 
        elif format == "excel":
            filename = f"Agents_Exports{time}.xlsx"
            data.to_excel(filename, index=False)
        with open(filename, "rb") as file:              
                self.bot.send_document(message.chat.id,document=file)
        os.remove(filename)

    def get_agents_csv(self):
        @self.bot.message_handler(commands=['agentscsv'])
        def send_agentscsv(message):
            if message.chat.id == int(self.master_id):
                self.generate_agents(format="csv", message=message)
            else:
                self.bot.reply_to(message, "I`m not your bot")

    def get_agents_json(self):
        @self.bot.message_handler(commands=['agentsjson'])
        def senf_agentsjson(message):
            if message.chat.id == int(self.master_id):
                self.generate_agents(format="json", message=message)
            else:
                self.bot.reply_to(message, "I`m not your bot")

    def get_agents_excel(self):
        @self.bot.message_handler(commands=['agentsexcel'])
        def senf_agentsexcel(message):
            if message.chat.id == int(self.master_id):
                self.generate_agents(format="excel", message=message)
            else:
                self.bot.reply_to(message, "I`m not your bot")


    def get_logs(self):
        try:
            headers = {
                "Content-Type": "application/json",
                'Authorization': f'Bearer {self.jwt_token}'
            }
            url = self.base_url+"/manager/logs"

            payload = {
                "query": {
                    "match": {
                        "agent.id": "001"
                    }
                }
            }

            response = requests.get(
                url=url,
                headers=headers,
                verify=False,
                json=payload

            )

            try:
                data_json = json.dumps(response.json().get('data').get('affected_items'))
                data_io = StringIO(data_json)
                dataframe = pd.read_json(data_io)
                dataframe['timestamp'] = dataframe['timestamp'].astype(str)
                dataframe.columns = dataframe.columns.str.strip()
                dataframe = dataframe.rename(columns={"timestamp":"TIME", "tag":"TAG", "level": "LEVEL", "description" : "DESCRIPTION"})
                time = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M")
                filename = f'Manager_logs{time}.xlsx'
                dataframe.to_excel(f'Manager_logs{time}.xlsx', index=False)
                
                with open(filename, "rb") as file:              
                    self.bot.send_document(self.master_id,document=file)
                os.remove(filename)
            except Exception as e:
                print(f'[!]ERROR was occured with description : {e}')
            
        except Exception as e:
            print(f'[!]ERROR was occured with description : {e}')

    def start_schedule(self):
        schedule.every(1).minutes.do(self.get_logs)

        while True:
            schedule.run_pending()  
            time.sleep(1)


    def get_agents_active(self):
        #IN DEVELOPMENT
        try:
            headers = {
                "Content-Type": "application/json",
                'Authorization': f'Bearer {self.jwt_token}'
            }
            url = self.base_url+"/agents"

            response  = requests.get(
                url=url,
                headers=headers,
                verify=False
            )
            
            response.raise_for_status()
            agents = response.json()['data']['affected_items']
            agentsdata = pd.DataFrame(agents)

            return agentsdata

        except Exception as e:
            print(f'[!]ERROR was occured with description : {e}')
            
    def run(self):
        if self.switcher == "AUTO":
            self.start_schedule()
            self.bot.polling(none_stop=True)
        else:    
            self.get_start()
            self.get_agents_csv()
            self.get_agents_json()
            self.get_agents_excel()
            self.bot.polling(none_stop=True)



if __name__ == "__main__":
    
    config = dotenv_values('.env')
    
    wb = WazuhBot(
                username=config['WAZUH_USER'], 
                password=config['WAZUH_PASS'],
                base_url=config['WAZUH_URL'],
                telegram_token=config['BOT_TOKEN'],
                master_id=config['MASTER_ID'],
                switcher=config['SWITCHER']
                   )
    wb.run()
