from typing import List

import resend
import os

resend.api_key = os.getenv('RESEND_API_KEY')

def send_email(from_mail: str, to_mail: List[str], subject: str, body: str):
    params: resend.Emails.SendParams = {
      "from": from_mail,
      "to": to_mail,
      "subject": subject,
      "html": body
    }

    email = resend.Emails.send(params)
    return email