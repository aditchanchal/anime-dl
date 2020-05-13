# Anime-dl
Python script to download anime via command line.
Supports only https://www.kickassanime.rs at the moment.

### SETTING UP:

##### Clone Repo
	$ git clone https://github.com/aditchanchal/anime-dl

##### Without TOR/ With Requests
	1. pip install -r requirements.txt
	2. python3 kickassanime_dl_No_TOR.py
	
##### With TOR
	1. Follow [this](https://www.scrapehero.com/make-anonymous-requests-using-tor-python/) to set up TOR module.
	2. Make following changes to the python script: kickassanime_dl.py .
	   - Add your password at line no. 42 (replace xxxxxxx).
	     - tr = TorRequest(password='xxxxxxx') # Enter your own password
	   - If you want to reset your IP or your requests are getting blocked then uncomment line no. 43.
	     - tr.reset_identity()
	3. pip install -r requirements.txt
	4. python3 kickassanime_dl.py

## RUNNING SCRIPT
--Will add a video soon--
