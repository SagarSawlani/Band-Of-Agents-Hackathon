import base64
import random
import ast
from copyleaks.copyleaks import Copyleaks
from copyleaks.models.submit.document import FileDocument
from copyleaks.models.submit.properties.scan_properties import ScanProperties
from copyleaks.models.submit.properties.submit_webhooks import SubmitWebhooks
from dotenv import load_dotenv
import os

load_dotenv()

# We must dynamically login to get the properly formatted auth_token dictionary!
EMAIL_ADDRESS = "sawlanisagar1@gmail.com"
API_KEY = os.getenv("COPYLEAKS_API_KEY")

print("Logging into Copyleaks...")
auth_token = Copyleaks.login(EMAIL_ADDRESS, API_KEY)

print("Submitting a new file...")
BASE64_FILE_CONTENT = base64.b64encode(b'Hello world').decode('utf8')  # or read your file and convert it into BASE64 presentation.
TEXT = """
  Interviewer: Tell me about yourself.

Candidate: My name is Alex Johnson, and I recently completed my Bachelor's degree in Computer Science. Over the past two years, I have focused on machine learning and backend development. I completed an internship where I built automated reporting pipelines using Python and SQL, which reduced manual work for the operations team. I also enjoy participating in hackathons and building AI-powered applications.

Interviewer: Can you describe a challenging project you worked on?

Candidate: One of the most challenging projects was developing a resume screening system using natural language processing. The main difficulty was handling resumes in different formats, including PDFs and scanned images. I used OCR for text extraction and then applied transformer-based models to identify skills and match candidates to job requirements. The system improved screening efficiency and reduced the time recruiters spent reviewing applications.
"""
scan_id = str(random.randint(100, 100000))  # generate a random scan id as string

# You must encode your actual TEXT variable into base64! 
# The second argument to FileDocument is the filename (e.g. 'interview.txt'), NOT the text content.
BASE64_FILE_CONTENT = base64.b64encode(TEXT.encode('utf8')).decode('utf8')
file_submission = FileDocument(BASE64_FILE_CONTENT, "interview.txt")
# Once the scan completed on Copyleaks servers, we will trigger a webhook that notify you.
# Write your public endpoint server address. If you testing it locally, make sure that this endpoint
# is publicly available.
webhooks = SubmitWebhooks()
webhooks.set_status('https://your.server/webhook/{STATUS}')
webhooks.set_new_result('https://your.server/webhook/new-results')

# Pass the webhooks to ScanProperties
scan_properties = ScanProperties(status_webhook='https://your.server/webhook/{STATUS}')
scan_properties.set_webhooks(webhooks)
scan_properties.set_sandbox(True)  # Turn on sandbox mode. Turn off on production.
file_submission.set_properties(scan_properties)
Copyleaks.submit_file(auth_token, scan_id, file_submission)  # sending the submission to scanning
print("Send to scanning")
print("You will notify, using your webhook, once the scan was completed.")