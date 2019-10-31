from rauth.service import OAuth2Service

import json
import requests
import sys
import datetime


# Function that write logs
def write_output_to_file(to_write):
	with open("output.txt", "a+") as log_file:
		log_file.write(to_write+"\n")

with open('config.json', 'r') as f:
    config_json = json.load(f)

# Function that sends email
def send_mail(body):
	import smtplib, ssl
	from email.mime.base import MIMEBase
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText

	# Server config
	email_config = config_json["email"]
	port = email_config["port"]
	smtp_server = email_config["smtpServer"]
	sender_email = email_config["senderEmail"]
	sender_email_to_display = email_config["senderEmailToDisplay"]
	receiver_email = email_config["receiverEmail"]
	cc_email = email_config["ccEmail"]
	bcc_email = email_config["bccEmail"]
	password = email_config["password"]

	# Email content
	subject = "[inkOS] Weekly Summary Time Tracker"
	
	# Create a multipart message and set headers
	message = MIMEMultipart()
	message["From"] = "73kBot <"+sender_email_to_display+">"
	message["To"] = receiver_email
	message['Cc'] = cc_email
	message['Bcc'] = bcc_email
	message["Subject"] = subject

	toaddrs = [receiver_email] + [cc_email] + [bcc_email]

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
		server.sendmail(sender_email, toaddrs, text)
	except Exception as e:
	    # Print any error messages to stdout
	    write_output_to_file("Erreur: "+str(e))
	    write_output_to_file("\r\n")
	    exit()
	finally:
		server.quit()
		write_output_to_file("73kBot sent a mail to "+receiver_email+"\r\n")

# Function that save tokens to a file
def save_token_to_file(token_access, token_refresh):
	with open('token', 'w') as token_file:
		token_file.write(token_access+"\n")
		token_file.write(token_refresh)

# Parameter check
# if len(sys.argv) < 3:
# 	write_output_to_file("Missing parameters, usage: `$ python3.7 timechecker.py <client_id> <client_secret> [<code>]`")
# 	exit()

# Get a real consumer key & secret from:
freshbooks_config = config_json["freshbooks"]
freshbooks = OAuth2Service(
    client_id=freshbooks_config["accountClientId"],
    client_secret=freshbooks_config["accountClientSecret"],
    access_token_url='https://api.freshbooks.com/auth/oauth/token')

if len(sys.argv) > 1:
	code = sys.argv[1]
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

# Work of the day last 24h
dt = datetime.datetime.today() - datetime.timedelta(1)
dt_string = dt.strftime("%Y-%m-%d")

# Replace <businessId> <client-id>
url = "https://api.freshbooks.com/timetracking/business/"+freshbooks_config["businessId"]+"/time_entries?client_id="+freshbooks_config["clientId"]+"&page=0&started_from="+dt_string+"T04%3A00%3A00Z"
headers = {'Authorization': token, 'Api-Version': 'alpha'}
res = requests.get(url, data=None, headers=headers)

# Mail to send
total_hours_logged = round(res.json()["meta"]["total_logged"]/3600,2)
if total_hours_logged <= 0:
	write_output_to_file("Lazy dude you've done nothing today!")
	exit()

body = "Bonjour,<br/><br/>"
body += "Voici le résumé du travail du jour fait par inkOS<br/><br/>"

body += "<ul>"
for entry in res.json()["time_entries"]:
	duration = str(round(entry["duration"]/3600,2))
	write_output_to_file(entry["note"]+": "+duration+"h")
	body += "<li>["+duration+"h] "+entry["note"]+"</li>"

write_output_to_file("TOTAL:"+str(total_hours_logged))
body += "</ul>"
body += "TOTAL: "+str(total_hours_logged)+"H<br/>"

if total_hours_logged > 0:
	send_mail(body)