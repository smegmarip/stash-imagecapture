"""
The common.py file contains common functions and variables that are used by the imagecapture plugin.
:doc-author: smegmarip
"""

import os
import sys
import json
import warnings
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple
from glob import glob

try:
    import stashapi.log as log
    from stashapi.stashapp import StashInterface
except ModuleNotFoundError:
    print(
        "You need to install the stashapp-tools (stashapi) python module. (CLI: pip install stashapp-tools)",
        file=sys.stderr,
    )

plugincodename = "imagecapture"
pluginhumanname = "imagecapture"

# Configuration/settings file... because not everything can be easily built/controlled via the UI plugin settings
# If you don't need this level of configuration, just define the default_settings here directly in code,
#    and you can remove the _defaults.py file and the below code
if not os.path.exists("config.py"):
    with open(plugincodename + "_defaults.py", "r") as default:
        config_lines = default.readlines()
    with open("config.py", "w") as firstrun:
        firstrun.write("from " + plugincodename + "_defaults import *\n")
        for line in config_lines:
            if not line.startswith("##"):
                firstrun.write(f"#{line}")

import config

default_settings = config.default_settings

PLUGIN_NAME = f"[{pluginhumanname}] "
STASH_LOGFILE = default_settings["stash_logfile"]

warnings.filterwarnings("ignore")


def stash_log(*args, **kwargs):
    """
    The stash_log function is used to log messages from the script.

    :param *args: Pass in a list of arguments
    :param **kwargs: Pass in a dictionary of key-value pairs
    :return: The message
    :doc-author: Trelent
    """
    messages = []
    for input in args:
        if not isinstance(input, str):
            try:
                messages.append(json.dumps(input, default=default_json))
            except:
                continue
        else:
            messages.append(input)
    if len(messages) == 0:
        return

    lvl = kwargs["lvl"] if "lvl" in kwargs else "info"
    message = " ".join(messages)

    if lvl == "trace":
        log.LEVEL = log.StashLogLevel.TRACE
        log.trace(message)
    elif lvl == "debug":
        log.LEVEL = log.StashLogLevel.DEBUG
        log.debug(message)
    elif lvl == "info":
        log.LEVEL = log.StashLogLevel.INFO
        log.info(message)
    elif lvl == "warn":
        log.LEVEL = log.StashLogLevel.WARNING
        log.warning(message)
    elif lvl == "error":
        log.LEVEL = log.StashLogLevel.ERROR
        log.error(message)
    elif lvl == "result":
        log.result(message)
    elif lvl == "progress":
        try:
            progress = min(max(0, float(args[0])), 1)
            log.progress(str(progress))
        except:
            pass
    log.LEVEL = log.StashLogLevel.INFO


def default_json(t):
    """
    The default_json function is used to convert a Python object into a JSON string.
    The default_json function will be called on every object that is returned from the StashInterface class.
    This allows you to customize how objects are converted into JSON strings, and thus control what gets sent back to the client.

    :param t: Pass in the time
    :return: The string representation of the object t
    :doc-author: Trelent
    """
    return f"{t}"


def get_config_value(section, prop):
    """
    The get_config_value function is used to retrieve a value from the config.ini file.

    :param section: Specify the section of the config file to read from
    :param prop: Specify the property to get from the config file
    :return: The value of a property in the config file
    :doc-author: Trelent
    """
    global _config
    return _config.get(section=section, option=prop)


def exit_plugin(msg=None, err=None):
    """
    The exit_plugin function is used to exit the plugin and return a message to Stash.
    It takes two arguments: msg and err. If both are None, it will simply print &quot;plugin ended&quot; as the output message.
    If only one of them is None, it will print that argument as either an error or output message (depending on which one was not None).
    If both are not none, then it will print both messages in their respective fields.

    :param msg: Display a message to the user
    :param err: Print an error message
    :return: A json object with the following format:
    :doc-author: Trelent
    """
    if msg is None and err is None:
        msg = pluginhumanname + " plugin ended"
    output_json = {}
    if msg is not None:
        stash_log(f"{msg}", lvl="debug")
        output_json["output"] = msg
    if err is not None:
        stash_log(f"{err}", lvl="error")
        output_json["error"] = err
    print(json.dumps(output_json))
    sys.exit()


def clear_logfile():
    """
    The clear_logfile function clears the logfile.

    :return: Nothing
    :doc-author: Trelent
    """
    if STASH_LOGFILE and os.path.exists(STASH_LOGFILE):
        with open(STASH_LOGFILE, "w") as file:
            pass


def to_integer(iter=[]):
    """
    The to_integer function is used to convert a list of strings to a list of integers.

    :param iter: Pass in a list of strings
    :return: A list of integers
    """
    return list(map(lambda x: int(x), iter))


def to_string(iter=[]):
    """
    The to_string function is used to convert a list of integers to a list of strings.

    :param iter: Pass in a list of integers
    :return: A list of strings
    """
    return list(map(lambda x: str(x), iter))


def the_id(iter=[]):
    """
    The the_id function is used to extract the id from a list of dictionaries.

    :param iter: Pass in a list of dictionaries
    :return: A list of ids
    """
    return list(map(lambda x: x["id"] if isinstance(x, dict) and "id" in x else x, iter))


def prepare_stash_list(iter=[]):
    """
    The prepare_stash_list function is used to prepare a list for use with the Stash API.

    :param iter: Pass in a list
    :return: A list with unique values
    """
    return list(set(to_string(iter)))


def extract_scene_metadata(scene: dict):
    """
    The extract_scene_metadata function takes a scene dictionary as input and returns a new dictionary containing the following keys:
        id: The unique identifier for the scene.
        title: The title of the scene, or if no title is provided, then it will be set to filename.
        filename: The name of the file that contains this particular video clip.  This is extracted from path using os.path.basename().split(&quot;/&quot;)[-2].  Note that this assumes that all files are stored in subdirectories within your stash directory (e.g., /stash/scenes/&lt;filename&gt;).  If you have

    :param scene: dict: Pass in the scene dictionary
    :return: A dictionary with the scene's id, title, filename, duration and sprites
    :doc-author: Trelent
    """
    file = scene["files"][0]
    filename = os.path.basename(file["path"]).split("/")[-1]
    directory_path = os.path.dirname(file["path"])
    directory_name = os.path.basename(directory_path)
    metadata = {
        "id": scene["id"],
        "title": scene["title"] if scene["title"] else filename,
        "filename": filename,
        "foldername": directory_name,
        "folderpath": directory_path,
        "path": file["path"],
        "duration": file["duration"],
        "sprites": scene["paths"]["sprite"],
        "width": file["width"],
        "height": file["height"],
    }
    return metadata


def extract_image_metadata(image: dict):
    """
    The extract_image_metadata function takes an image dictionary as input and returns a new dictionary containing metadata.

    :param image: dict: Pass in the image dictionary
    :return: A dictionary with the image metadata
    :doc-author: Trelent
    """
    file = image["visual_files"][0]
    filename = os.path.basename(file["path"]).split("/")[-1]
    directory_path = os.path.dirname(file["path"])
    directory_name = os.path.basename(directory_path)
    metadata = {
        "id": image["id"],
        "title": image["title"] if image["title"] else filename,
        "filename": filename,
        "foldername": directory_name,
        "path": file["path"],
        "paths": [f["path"] for f in image["visual_files"]],
        "mod_time": file["mod_time"],
    }
    return metadata


def search_images_by_prefix(stash: StashInterface, regex: str) -> List:
    """
    The search_images_by_prefix function is used to search for images in Stash by their prefix.

    :param stash: The StashInterface object
    :param regex: The regular expression to search for
    :return: A list of images
    """
    return stash.find_images(f={"path": {"value": regex, "modifier": "MATCHES_REGEX"}}, filter={"per_page": 500})


def get_image_by_path(stash: StashInterface, image_path: str) -> dict:
    """
    The get_image_by_path function is used to retrieve an image from Stash by its path.
    The function takes the following parameters:
        stash: The StashInterface object
        image_path: The path of the image to retrieve

    :return: The image object
    """
    result = stash.find_images(f={"path": {"value": image_path, "modifier": "EQUALS"}}, filter={"per_page": 1})
    if result and len(result) > 0:
        return result[0]
    return None


def update_scene(stash: StashInterface, id, scene_date=None):
    """
    The update_scene function is used to update a scene in Stash.
    The function takes the following parameters:
        stash: The StashInterface object
        id: The id of the scene to update
        scene_date: The date of the scene to update

    :return: The scene id
    """
    payload = {"id": id}
    if scene_date is not None:
        payload["date"] = scene_date
        return stash.update_scene(payload)
    return None


def update_image(stash: StashInterface, id: int, gallery_id: int = None, tag_ids: List[int] = None) -> int:
    """
    The update_image function is used to update an image in Stash.
    The function takes the following parameters:
        stash: The StashInterface object
        id: The id of the image to update
        gallery_id: The id of the gallery to add the image to
        tag_ids: A list of tag ids to add to the image

    :return: The image id
    """
    payload = {"id": id}
    if gallery_id is not None:
        payload["gallery_ids"] = prepare_stash_list([gallery_id])
    if tag_ids is not None and len(tag_ids) > 0:
        payload["tag_ids"] = prepare_stash_list(tag_ids)

    stash_log(payload, lvl="trace")
    if len(payload) > 1:
        return stash.update_image(payload)
    return None
