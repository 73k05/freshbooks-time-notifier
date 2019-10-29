# freshbooks-time-notifier
Send notifications to yourself, coworkers or customers when a time entry has been made. Make anyone knows what you have been working on automatically.

Once a week.

usage: `$ python3.7 timechecker.py <client_id> <client_secret> [<code>]`

Change your smtp and client parameters in timechecker.py.

Use crontab to call this script everytime you want to send your client a notification. I call it every saturday to summerize the week.

Every 12h the access token will expire but it doesn't matter as long as the script renew the token with the refresh token before sending the request and save new tokens for next request in a file.