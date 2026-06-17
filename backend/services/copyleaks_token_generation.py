from copyleaks.copyleaks import Copyleaks
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_ADDRESS = "sawlanisagar1@gmail.com"
API_KEY = os.getenv("COPYLEAKS_API_KEY")

# Login to Copyleaks
auth_token = Copyleaks.login(EMAIL_ADDRESS, API_KEY)
print("Logged successfully!\nToken:", auth_token)