"""
Entry point for the imagecapture plugin.
:doc-author: smegmarip
"""

import json
import os
import sys

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from common import (
    stash_log,
    exit_plugin,
    pluginhumanname,
    clear_logfile,
)
from imagecapture_functions import (
    capture_frame,
)

try:
    from stashapi.stashapp import StashInterface
except ModuleNotFoundError:
    print(
        "You need to install the stashapp-tools (stashapi) python module. (CLI: pip install stashapp-tools)",
        file=sys.stderr,
    )


def main():
    """
    The main function is the entry point for this plugin.

    :return: A string
    :doc-author: Trelent
    """
    global stash

    json_input = json.loads(sys.stdin.read())
    FRAGMENT_SERVER = json_input["server_connection"]
    stash = StashInterface(FRAGMENT_SERVER)

    ARGS = False
    PLUGIN_ARGS = False

    # Task Button handling
    try:
        PLUGIN_ARGS = json_input["args"]["mode"]
        ARGS = json_input["args"]
    except:
        pass

    # Optionally clear log file
    clear_logfile()

    if PLUGIN_ARGS:
        stash_log("--Starting " + pluginhumanname + " Plugin --", lvl="debug")

        if "captureFrame" in PLUGIN_ARGS:
            stash_log("running captureFrame", lvl="info")
            if "scene_id" in ARGS:
                scene_id = ARGS["scene_id"]
                if scene_id is not None:
                    frame_idx = ARGS["frame_idx"] if "frame_idx" in ARGS else 0
                    frame_idx = int(frame_idx) if frame_idx not in [False, None, "None", "null"] else 0
                    result = capture_frame(stash=stash, scene_id=scene_id, frame_idx=frame_idx)
                    if result is not None:
                        stash_log("captureFrame =", result, lvl="info")
                        exit_plugin(msg="ok")
            stash_log("captureFrame =", {"result": None}, lvl="info")

    exit_plugin(msg="ok")


if __name__ == "__main__":
    main()
