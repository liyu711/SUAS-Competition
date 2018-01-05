from time import sleep
import os
import math
from SUASSystem import utils, GCSSettings, inverse_haversine
from PIL import Image

def run_img_proc_process(logger_queue, location_log, targets_to_submit, interop_client_array):
    while True:
        if len(targets_to_submit) > 0:
            target_characteristics = targets_to_submit.pop(0)

            if GCSSettings.UAV_VERSION == "10":
                target_time = utils.get_image_timestamp_from_filename(target_characteristics["base_image_filename"])
            elif GCSSettings.UAV_VERSION == "9.1":
                target_time = utils.get_image_timestamp_from_metadata("static/imgs/" + target_characteristics["base_image_filename"])
            else:
                raise Exception("Unknown drone type")

            closest_time_index = 0
            least_time_difference = location_log[0]["epoch_time"]
            for index in range(len(location_log)):
                difference_in_times = target_time - location_log[closest_time_index]["epoch_time"]
                if abs(difference_in_times) <= least_time_difference:
                    closest_time_index = index
                    least_time_difference = difference_in_times

            drone_gps_location = location_log[closest_time_index]["current_location"]
            image = Image.open("static/imgs/" + target_characteristics["base_image_filename"])
            image_midpoint = (image.width / 2, image.height / 2)
            target_midpoint = ((target_characteristics["target_top_left"][0] + target_characteristics["target_bottom_right"][0]) / 2, (target_characteristics["target_top_left"][1] + target_characteristics["target_bottom_right"][1]) / 2)
            target_location = utils.get_target_gps_location(image_midpoint, target_midpoint, drone_gps_location)
            target_characteristics["latitude"] = target_location.get_lat()
            target_characteristics["longitude"] = target_location.get_lon()

            original_image_path = "static/imgs/" + target_characteristics["base_image_filename"]
            cropped_target_path = "static/crops/" + str(len(os.listdir('static/crops'))) + ".jpg"
            cropped_target_data_path = "static/crops/" + str(len(os.listdir('static/crops'))) + ".json"
            utils.crop_target(original_image_path, cropped_target_path, target_characteristics["target_top_left"], target_characteristics["target_bottom_right"])
            utils.save_json_data(cropped_target_data_path, target_characteristics)

            interop_client_array[0].post_standard_target(target_characteristics, cropped_target_path)

        sleep(0.1)

def run_autonomous_img_proc_process(logger_queue, location_log, targets_to_submit, interop_client_array, img_proc_status):
    while True:
        if img_proc_status.value == "connected":
            # Add autonomous image processing code here
    
            pass
