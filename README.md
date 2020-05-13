# Anime-dl
Python script to download anime via command line.
Supports only https://www.kickassanime.rs at the moment.

### SETTING UP:

##### Clone Repo
	$ git clone https://github.com/aditchanchal/anime-dl

##### Without TOR/ With Requests
	1. $ pip install -r requirements.txt
	2. $ python3 kickassanime_dl_No_TOR.py
	
##### With TOR
   1. Follow https://www.scrapehero.com/make-anonymous-requests-using-tor-python/ to set up TOR module.
   2. Make following changes to the python script: kickassanime_dl.py .
      - Add your password at line no. 42 (replace xxxxxxx).
		```python
		tr = TorRequest(password='xxxxxxx') # Enter your own password
		```      
      - If you want to reset your IP or your requests are getting blocked then uncomment line no. 43.
		```python
		tr.reset_identity()
		```
   3. Run
   ```bash
	$ pip install -r requirements.txt
	$ python3 kickassanime_dl.py
   ```

### RUNNING SCRIPT
<p align="center">
<img src="https://user-images.githubusercontent.com/39438054/81859231-8e113180-9582-11ea-9be0-0af1777e99df.gif">
</p>
<p align="center">
	1. 1st Arguement: Link of the episode to download.
	2. 2nd Arguement: No. of additional episodes to download in continuation to above episode.
	3. 3rd Arguement: Choose video resolution.
</p>

