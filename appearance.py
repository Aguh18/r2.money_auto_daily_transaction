

ASCII_ART = """
  ___        _            _                    
 / _ \\      | |          | |                   
/ /_\\ \\_   _| |_ ___   __| |_ __ ___  _ __ ____
|  _  | | | | __/ _ \\ / _` | '__/ _ \\| '_ \\_  /
| | | | |_| | || (_) | (_| | | | (_) | |_) / / 
\\_| |_/\\__,_|\\__\\___/ \\__,_|_|  \\___/| .__/___|
                                     | |       
                                     |_|       
"""
CREDIT = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧑‍💻 Created by        : Aguhh
🌐 GitHub            : https://github.com/Aguh18
💬 Join Telegram     : https://t.me/+V_JQTTMVZVU3YTM9
🔗 LinkedIn          : https://www.linkedin.com/in/asep-teguh-hidayat/
🎮 Join Discord      : https://discord.gg/wjxASXVD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

EMOJI = {
    'SUCCESS': '✅',
    'ERROR': '❌',
    'WARNING': '⚠️',
    'INFO': 'ℹ️',
    'MONEY': '💰',
    'SWAP': '🔄',
    'STAKE': '📌',
    'WALLET': '👛',
    'LOADING': '⏳'
}

COLORS = {
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'RED': '\033[31m',
    'WHITE': '\033[37m',
    'GRAY': '\033[90m',
    'CYAN': '\033[36m',
    'RESET': '\033[0m'
}

class COLORSS:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    RESET = '\033[0m'

# Emoji untuk output konsol
class EMOJIS:
    SUCCESS = '✅'
    ERROR = '❌'
    WARNING = '⚠️'
    INFO = 'ℹ️'
    MONEY = '💰'
    WALLET = '👛'
    SWAP = '🔄'
    LOADING = '⏳'

def color_text(text, color):
    return f"{color}{text}{COLORS['RESET']}"