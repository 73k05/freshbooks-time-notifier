from rauth.service import OAuth2Service

import json
import requests
import sys
import datetime


# Function that write logs
def write_output_to_file(to_write):
	with open("output.txt", "a+") as log_file:
		log_file.write(to_write+"\n")

# Function that sends email
def send_mail(body):
	import smtplib, ssl
	from email.mime.base import MIMEBase
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText

	# Server config
	port = ***
	smtp_server = "***"
	sender_email = "***"  # Enter your address
	receiver_email_to_display = "***"
	receiver_email = "***"  # Enter receiver address
	password = "***"

	# Email content
	subject = "[inkOS] Weekly Summary Time Tracker"
	
	# Create a multipart message and set headers
	message = MIMEMultipart()
	message["From"] = "73kBot <"+receiver_email_to_display+">"
	message["To"] = receiver_email
	message["Subject"] = subject

	# Add body to email
	message.attach(MIMEText(body, "html"))
	text = message.as_string()

	# Send mail
	try:
		server = smtplib.SMTP(smtp_server,port)
		# Can be omitted
		server.ehlo()
		server.starttls()	
		server.ehlo()
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, text)
	except Exception as e:
	    # Print any error messages to stdout
	    write_output_to_file("Erreur: "+str(e))
	    write_output_to_file("\r\n")
	    exit()
	finally:
		server.quit()
		write_output_to_file("73kBot sent a mail to "+ receiver_email + "\r\n")

# Function that save tokens to a file
def save_token_to_file(token_access, token_refresh):
	with open('token', 'w') as token_file:
		token_file.write(token_access+"\n")
		token_file.write(token_refresh)

# Parameter check
if len(sys.argv) < 3:
	write_output_to_file("Missing parameters, usage: `$ python3.7 timechecker.py <client_id> <client_secret> [<code>]`")
	exit()

# Get a real consumer key & secret from:
freshbooks = OAuth2Service(
    client_id=sys.argv[1],
    client_secret=sys.argv[2],
    access_token_url='https://api.freshbooks.com/auth/oauth/token')

if len(sys.argv) > 3:
	code = sys.argv[3]
	write_output_to_file("Given code:"+code)

	# generate token
	data = {'code':code,"grant_type":"authorization_code","redirect_uri":'https://github.com/73k05/freshbooks-time-notifier'}
else:
	write_output_to_file("No code given, use refresh token in file <./token>")
	with open('token') as token_file:
		token_access = token_file.readline().rstrip('\n')
		token_refresh = token_file.readline()

		# refresh token
		data = {'refresh_token':token_refresh,"grant_type":"refresh_token","redirect_uri":'https://github.com/73k05/freshbooks-time-notifier'}


# Retrieve or Refresh the authenticated token
token_raw = freshbooks.get_raw_access_token(data=data).content.decode('utf8')

write_output_to_file(token_raw)

token_json = json.loads(token_raw)
token_access = token_json["access_token"]
token_refresh = token_json["refresh_token"]

save_token_to_file(token_access, token_refresh)

token = 'Bearer '+token_access

write_output_to_file("Access TOKEN: "+token_access)
write_output_to_file("Refresh TOKEN: "+token_refresh)

# Only once a week on saturday morning before noon
if datetime.datetime.today().weekday() != 5 or datetime.datetime.today().hour < 12:
	exit()

dt = datetime.datetime.today() - datetime.timedelta(7)
dt_string = dt.strftime("%Y-%m-%d")

# Replace <businessId> <client-id>
url = "https://api.freshbooks.com/timetracking/business/<businessId>/time_entries?client_id=<client-id>&page=0&started_from="+dt_string+"T04%3A00%3A00Z"
headers = {'Authorization': token, 'Api-Version': 'alpha'}
res = requests.get(url, data=None, headers=headers)

# Mail to send
total_hours_logged = round(res.json()["meta"]["total_logged"]/3600,2)
body = "Bonjour,<br/><br/>"
body += "Voici le résumé du travail de la semaine fait par ***<br/><br/>"

body += "<ul>"
for x in res.json()["time_entries"]:
	duration = str(round(x["duration"]/3600,2))
	write_output_to_file(x["note"]+": "+duration+"h")
	body += "<li>"+x["note"]+": "+duration+"h</li>"

write_output_to_file("TOTAL:"+str(total_hours_logged))
body += "</ul>"
body += "TOTAL: "+str(total_hours_logged)+"h<br/>"

if total_hours_logged > 0:
	send_mail(body)