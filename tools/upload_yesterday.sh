# assumes dropbox_uploader.sh is installed and configured

# zip the folder first
YESTERDAY=$(date --date='yesterday' +"%Y%m%d")
zip -r ${YESTERDAY}.zip /home/pi/sydney-transport-tracker/data/raw/${YESTERDAY}

# upload to dropbox
./dropbox_uploader.sh upload ${YESTERDAY}.zip ${YESTERDAY}.zip 
rm ${YESTERDAY}.zip 
