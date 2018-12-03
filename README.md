# sydney-transport-tracker

Automated scripts for downloading, analysing, and publishing insights about the public transport in Sydney, Australia.

## Getting Started
This is currently developed on Windows. This will eventually change, as the target platform is Linux (Raspbian).

### Installing

python3

Packages: 
* google
* gtfs-realtime-bindings
* progress
* pandas

A file named credentials.txt must be created in the root directory of the project.
It must contain an API key generated from [Transport for NSW Open Data API](https://opendata.transport.nsw.gov.au).
You will have to register to get the key.
Do *not* put a newline in the file!

## Deployment
The target platform is a Raspberry Pi running Raspbian.

## To do
The timetable downloaded represents stop times for late night services with hours greater than 23.
For example, if a train starts at 23:55 and has a stop 10 minutes later, it will be at 24:05. 
This is currently not handled. In this situation, it will be ignored.

## Acknowledgments
* [Transport for NSW Open Data API](https://opendata.transport.nsw.gov.au)
* [General Transit Feed Specification](https://developers.google.com/transit/)
