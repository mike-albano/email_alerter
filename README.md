# email_alerter
Simple script to check output and email if condition found. Uses gMail API.

## Requirements
```
pip install --user -r requirements.txt
```
Enable the gmail API at: https://developers.google.com/gmail/api/

Specifically, click the button here:
https://developers.google.com/gmail/api/quickstart/python?authuser=1

You MUST save the credentials as 'credentials.json' in the same directory as this script.

## Quick Start (what to modify)
1. Change the to/from email addresses in main() function.
2. Change/add commands you want to run in the run_cmds() function.
3. Change the Alert conditions in the check_outputs() functions.
