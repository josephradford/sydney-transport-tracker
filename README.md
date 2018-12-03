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

## Acknowledgments
* [Transport for NSW Open Data API](https://opendata.transport.nsw.gov.au)
* [General Transit Feed Specification](https://developers.google.com/transit/)
