# freshbooks-time-notifier
Send notifications to yourself, coworkers or customers when a time entry has been made. Make anyone knows what you have been working on automatically.

Once a week.

The first time you launch the script on a machine, you'll need the code. Usage: `$ python3.7 timechecker.py [<code>]`

Change your smtp and client parameters in timechecker.py

Use crontab to call this script everytime you want to send your client a notification. I call it every saturday to summerize the week.

Every 12h the access token will expire but it doesn't matter as long as the script renew the token with the refresh token before sending the request and save new tokens for next request in a file. 

No need to use `code` parameter everytime you call the script, only the first time. `client_id` & `client_secret` parameters are always compulsory.

To create `client_id` & `client_secret`, you need to go there https://my.freshbooks.com/#/developer, create an app, click on `Authorization URL` and copy and paste the `code` returned by the callback in your redirect uri.

`tail -f output.txt` to see logs

`cat token` to see saved tokens