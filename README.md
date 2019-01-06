# sydney-transport-tracker

Automated scripts for downloading, analysing, and [publishing insights](https://twitter.com/SydStats) about the public transport in Sydney, Australia.

## Getting Started
This is currently developed on Ubuntu. The target platform is Linux (Raspbian).

### Installing

This requires python3. See requirements.txt for packages.

#### Connecting to the Open Data API
A .env file must be created in src/data/, containing API keys in the format:
```
DELAYS_API_KEY=XXXXXX
TIMETABLE_API_KEY=XXXXXX
```
It is generated from [Transport for NSW Open Data API](https://opendata.transport.nsw.gov.au).
You will have to register to get the key.

It is recommended that you use separate keys for delays download and timetable download. This is to ensure that they never conflict
and call the API too quickly and get rejected. It also allows you to easily track usage from the scripts on the Open Data API dashboard.

#### Connecting to Twitter
A .env file must be created in src/features/, containing keys in the format:
```
CONSUMER_KEY=AAAA
CONSUMER_SECRET=BBBB
ACCESS_TOKEN=CCCC
ACCESS_TOKEN_SECRET=DDDD
```

These are created from the [Twitter development platform](https://developer.twitter.com/content/developer-twitter/en.html).

#### Connecting to Dropbox
Previous day's data can be zipped and uploaded using the scripts in tools/.

Follow the Usage guide for dropbox_upload.sh from the [Dropbox-Uploader Github](https://github.com/andreafabrizi/Dropbox-Uploader).

Run 
```
chmod +x upload_yesterday.sh
./upload_yesterday.sh 
```
To zip and upload all of yesterday's downloads to Dropbox. This will delete the zip file, but not the original directory.

## Deployment
The target platform is a Raspberry Pi running Raspbian. These steps assume you have cloned this directory to the home directory. 

Create .env files as described in the previous section, and setup Dropbox.

Get all packages by running
```
pip3 install -r requirements
```

Set up cron jobs by typing
```
sudo crontab -e
```

The following task schedule is suggested:
```
*/2 * * * * python3 /home/pi/sydney-transport-tracker/src/data/train_delay_download.py
1 4 * * * python3 /home/pi/sydney-transport-tracker/src/data/train_timetable_download.py
1 9 * * * python3 /home/pi/sydney-transport-tracker/src/features/analyse_by_time_period.py 07:00 09:00
31 18 * * * python3 /home/pi/sydney-transport-tracker/src/features/analyse_by_time_period.py 16:00 18:30
1 1 * * * /home/pi/sydney-transport-tracker/tools/upload_yesterday.sh

```

This will:
* Save current delay information every two minutes /data/raw/YYYYmmdd/HHMMSS.pickle.
* Save timetable infomration and unzip it once per day to /data/raw/YYYYmmdd/
* Analyse delays and tweet them for AM and PM peak times
* Back up yesterday's raw downloaded data at 1:01 each morning

Do *not* use /etc/rc.local. I find that it sometimes starts the script while pi is still in UTC which will ruin your day.

## Acknowledgments
* [Transport for NSW Open Data API](https://opendata.transport.nsw.gov.au)
* [General Transit Feed Specification](https://developers.google.com/transit/)
* [Directory inspired by Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/#directory-structure)
* [Dropbox-Uploader](https://github.com/andreafabrizi/Dropbox-Uploader)
