from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import googleapiclient
import base64
import subprocess
import sys
import time

# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time. If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://mail.google.com/']

def main():
  while True:
    outputs = run_cmds()  # Run commands we're interested in.
    alerts = check_outputs(outputs)  # Determine if we need to email/alert.
    if alerts:
      alert_strings = [x + '\n' for x in alerts]
      gmail_service = prep_gmail()
      #### Change these ####
      email = create_message('from_email@example.net', 'to_email@ecample.net',
                             'Alert', alert_strings[0])  # Prep the email.
      send_message(gmail_service, 'me', email)  # Send the email
      print('Alerts fired, exitnig.')
      sys.exit()
    time.sleep(60)  # Run at frequency of 1/minute.


def check_outputs(outputs):
  """Check output to determine if we need to send an alert email."""
  alerts = []
  if outputs[0] != 'BSSID: 5c:5b:35:31:5a:f1':  # Check our connected BSSID
    alerts.append('Incorrect %s' % outputs[0])
    # Add further checks here based on line[1] - n.
  return alerts


def run_cmds():
  """Run commands to include in the email message.

  Args:
    commands: tuple of commands to run.
  Returns:
    outputs: tuple of outputs.
  """
  outputs = []
  p = subprocess.Popen(['airport', '-I'], stdout=subprocess.PIPE)
  output = p.communicate()
  for line in output[0].split('\n'):  # Look for the line we want.
    if 'BSSID' in line:
      outputs.append(line.strip())  # Add it to the list of strings to email.
  # Add more commands here if interested in other output.
  return outputs


def prep_gmail():
    """Sends email message.

    Returns gmail service object.
    """
    # Prepare gMail credentials.
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)


def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string())}


def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
  except googleapiclient.errors.HttpError, error:
    print('An error occurred: %s' % error)

if __name__ == '__main__':
    main()
