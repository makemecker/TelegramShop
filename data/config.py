from environs import Env


env: Env = Env()
env.read_env('data/.env')

BOT_TOKEN = env('BOT_TOKEN')
ADMINS = env.list('ADMINS')

PROJECT_NAME = 'store-bot-example'

WEBHOOK_HOST = f"https://{PROJECT_NAME}.herokuapp.com"
WEBHOOK_PATH = '/webhook/' + BOT_TOKEN
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

THRESHOLD = 10000  # Порог для бесплатной доставки
