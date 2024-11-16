from nest_video_api import NestDoorbellDevice
from tools import logger
from models import CameraEvent

from io import BytesIO
import pytz
import datetime
import os
import shutil

# Get the PUID and PGID environment variables
PUID = int(os.environ.get('PUID', 1000))
PGID = int(os.environ.get('PGID', 1000))

BASE_DIRECTORY = "/videos"
LOCAL_TIMEZONE = os.environ.get("TIMEZONE", "America/Los_Angeles")
FETCH_RANGE = 240 # 3 hrs for free nest aware + 1 extra hour in case some data was missed, data isn't deleted immediately at the 3 hr mark

class DataEventsSync(object):
    
    def __init__(self, nest_camera_devices) -> None:
        self._nest_camera_devices = nest_camera_devices
        self._recent_events = set()

    def _cleanup_empty_folders(self, base_path):
        """Recursively remove empty folders"""
        for root, dirs, files in os.walk(base_path, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    # Check if directory is empty (no files and no non-empty subdirectories)
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        logger.debug(f"Removed empty directory: {dir_path}")
                except OSError as e:
                    logger.warning(f"Error removing directory {dir_path}: {e}")

    def sync_single_nest_camera(self, nest_device : NestDoorbellDevice):

        logger.info(f"Syncing: {nest_device.device_id}")
        if "DEVICE_" not in nest_device.device_id:
            # I only have a Gen 2 Nest Doorbell - have not tested other doorbells yet
            logger.info(f"{nest_device.device_id} does not look like a gen 2 Nest Doorbell, skipping...")
            return
        all_recent_camera_events : list[CameraEvent] = nest_device.get_events(
            end_time = datetime.datetime.now(),
            duration_minutes=FETCH_RANGE 
        )        

        # Create the directory to store videos on a per day and per devices basis
        today = pytz.utc.localize(datetime.datetime.now()).astimezone(pytz.timezone(LOCAL_TIMEZONE))
        # Extract year, month, and day
        year = str(today.year)
        month = str(today.month).zfill(2)  # Ensure two digits for month
        day = str(today.day).zfill(2)  # Ensure two digits for day
        directory = os.path.join(BASE_DIRECTORY, nest_device.device_name, year, month, day)
        if not os.path.exists(directory):
            os.makedirs(directory)

        logger.info(f"[{nest_device.device_id}] Received {len(all_recent_camera_events)} camera events")

        skipped = 0
        for camera_event_obj in all_recent_camera_events:
            # logger.info(camera_event_obj.start_time)
            file_name = nest_device.device_name + "_" + camera_event_obj.start_time.astimezone(pytz.timezone(LOCAL_TIMEZONE)).strftime("%Y-%m-%d_%I-%M-%S%p") + ".mp4"

            # Check if file has been previously downloaded
            if os.path.exists(os.path.join(directory, file_name)):
                logger.debug(f"CameraEvent ({camera_event_obj}) already sent, skipping..")
                skipped += 1
                continue

            logger.debug(f"Downloading camera event: {camera_event_obj}")
            video_data = nest_device.download_camera_event(camera_event_obj)
            video_io = BytesIO(video_data)

            with open(os.path.join(directory, file_name), "wb") as file:
                file.write(video_io.getvalue())

            logger.info("Saved " + file_name + " successfully")

            self._recent_events.add(camera_event_obj.event_id)

        # After processing all events, cleanup empty folders
        device_base_path = os.path.join(BASE_DIRECTORY, nest_device.device_name)
        self._cleanup_empty_folders(device_base_path)
        
        downloaded = len(all_recent_camera_events) - skipped
        logger.info(f"[{nest_device.device_id}] Downloaded: {downloaded}, skipped (already downloaded): {skipped}")

    def sync(self):
        logger.info("Syncing all camera devices")
        for nest_device in self._nest_camera_devices:
            self.sync_single_nest_camera(nest_device)
