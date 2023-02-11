# BMS Prasads bot

## About
Scrapes through the given BMS website and gets the best seat information (top 3 rows). Give the link to BMS website of a particular movie at a particular date and this bot will keep a lookout send you an email as soon as best seats in the theatre open. IYKYK

## Inputs
When prompted at the start give the BMS website input.
For example, it can be "https://in.bookmyshow.com/buytickets/ant-man-and-the-wasp-quantumania-3d-hyderabad/movie-hyd-ET00351697-MT/20230217"
### Few things to add in code before running
```python
receivers = [username] # Add receiver emails here like [username, "abc@xyz.com", "def@uvw.com"]
```
```python
browser.smtp_username = "xyz@abc.com" # Enter the email to be used to send the mail from
browser.smtp_password = "abcdefg"     # Enter the app-password of the email to be used to send the mail from
```
>- For _smtp_password_, app passwords need to be created in the email you want to use so the email login can be done externally and used.<br>
>- Since this script uses Yahoo, visit this [link](https://help.yahoo.com/kb/access-yahoo-mail-third-party-apps-sln15241.html) to create app passwords.<br>
>- Check [this](https://www.arclab.com/en/kb/email/list-of-smtp-and-imap-servers-mailserver-list.html) for changing SMTP/IMAP servers when using emails other than Yahoo

## Installation and Running
Install latest python version and run the following commands.
```python
> pip install requirements.txt
> python bot.py
```