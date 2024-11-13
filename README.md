# Google Nest Camera Video - Sync To Storage

I wanted an easy way to store my Nest event history to my local NAS and store more than 60 days of footage. By default it starts by only backing up the last 4 hours of data. You can build your own image if you want your initial fetch to include more than that. Just modify `FETCH_RANGE` in minutes.
This module is for personal use only, especially as it uses unpublished APIs. Use it is at your own risk!

## How to use it

1. Obtain a Google Master Token by running in terminal `docker run --rm -it breph/ha-google-home_get-token`. You'll need to use an app password generated from [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Create a folder on your system for the appdata from this image, and put the `nest.ini` template file inside with the data filled out
3. If using docker-compose, point the folder that is holding the `nest.ini` to `/config`, and your local storage pool or mounted storage and to `/videos`
4. Build it yourself with `docker-compose up -d`, I'll publish an image once I'm more confident in it

## Docker Compose

The docker compose file is configured to run the container with the user `1000:1000` which is the user that the Nest app runs as. This is to avoid permission issues when writing to the mounted volumes.

