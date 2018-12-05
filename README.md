# sydney-transport-tracker

Automated scripts for downloading, analysing, and publishing insights about the public transport in Sydney, Australia.

## Getting Started
This is currently developed on Ubuntu. The target platform is Linux (Raspbian).

### Installing

This requires python3. See requirements.txt for packages.


A .env file must be created in src/data/, containing the API Key for downloading delays.
This must be in the format of API_KEY=xxxxxx. 
It is generated from [Transport for NSW Open Data API](https://opendata.transport.nsw.gov.au).
You will have to register to get the key.


## Deployment
The target platform is a Raspberry Pi running Raspbian. These steps assume you have cloned this directory to the home directory. 

Create a .env file as described in the previous section. 

Get all packages by running
```
pip3 install -r requirements
```

To get the delay information downloaded and stored permanently, add the following cron job:
```
* * * * * python3 /home/pi/sydney-transport-tracker/src/data/train_delay_download.py
```

This will be saved to /data/raw/YYYYmmdd/HHMMSS.pickle.

Do *not* use /etc/rc.local. I find that it sometimes starts the script while pi is still in UTC which will ruin your day.

## Acknowledgments
* [Transport for NSW Open Data API](https://opendata.transport.nsw.gov.au)
* [General Transit Feed Specification](https://developers.google.com/transit/)
* [Directory inspired by Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/#directory-structure)
