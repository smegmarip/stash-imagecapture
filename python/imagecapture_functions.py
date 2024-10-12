"""
Image Capture Functions
These functions are used to capture a frame from a video and save it as an image.
:doc-author: smegmarip
"""

from pathlib import Path
import re
import sys
import traceback
import subprocess

from common import (
    extract_image_metadata,
    extract_scene_metadata,
    is_ffmpeg_installed,
    search_images_by_prefix,
    stash_log,
    the_id,
    to_integer,
)

try:
    from stashapi.stashapp import StashInterface
except ModuleNotFoundError:
    print(
        "You need to install the stashapp-tools (stashapi) python module. (CLI: pip install stashapp-tools)",
        file=sys.stderr,
    )


def capture_frame(stash: StashInterface, scene_id: int, frame_idx: int) -> dict:
    """
    Capture frame from video and save it.

    :param stash: StashInterface: Pass the stashinterface object to the function
    :param scene_id: int: Scene ID
    :param frame_idx int: Frame Index
    """
    scene = stash.find_scene(scene_id)
    gallery_id = None
    scene_tags = None
    result = False

    if scene:
        if "galleries" in scene and len(scene["galleries"]) > 0:
            gallery_id = scene["galleries"][0]["id"]
        if "tags" in scene and len(scene["tags"]) > 0:
            scene_tags = to_integer(the_id(scene["tags"]))
        scene_data = extract_scene_metadata(scene)

        if scene_data:
            scene_path = str(scene_data["path"])
            capture_filename = generate_image_filename(stash, scene_path)
            result = extract_frame(scene_data, int(frame_idx), capture_filename)

            if result:
                result = capture_filename
                # scene_folder = scene_data["folderpath"] + "/"
                # scan_library(stash, scene_folder)
    return {"result": result}


def extract_frame(scene_data: dict, frame_index: int, output_image_path: str) -> bool:
    """
    Extract a single frame from a video using ffmpeg and save it.

    :param scene_data: dict: Scene
    :param frame_index: int: Frame index
    :param output_image_path: str: Output image path
    :return: bool: Success
    """
    if not is_ffmpeg_installed():
        stash_log("ffmpeg could not be found", lvl="error")
        return False

    video_path = scene_data["path"]
    stash_log(
        {"video_path": video_path, "frame_index": frame_index, "output_image_path": output_image_path}, lvl="trace"
    )
    outcome = False

    # Get the frame rate to calculate the timestamp for the frame
    try:
        # Get video frame rate using ffprobe
        command = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=r_frame_rate",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        frame_rate_str = subprocess.check_output(command).decode("utf-8").strip()
        num, denom = map(int, frame_rate_str.split("/"))
        frame_rate = num / denom
        stash_log(f"Frame rate: {frame_rate} fps", lvl="debug")
    except Exception as e:
        stash_log(f"Error getting frame rate: {e}", lvl="error")
        return outcome

    # Calculate the timestamp for the desired frame
    timestamp = frame_index / frame_rate
    stash_log(f"Timestamp for frame {frame_index}: {timestamp} seconds", lvl="debug")

    # Build ffmpeg command to extract the frame
    ffmpeg_command = [
        "ffmpeg",
        "-loglevel",
        "fatal",
        "-i",
        video_path,
        "-vf",
        f"select=eq(n\,{frame_index})",
        "-vsync",
        "vfr",
        "-frames:v",
        "1",
        output_image_path,
        "-y",
    ]

    try:
        # Execute ffmpeg command
        subprocess.run(ffmpeg_command, check=True)
        stash_log(f"Frame {frame_index} saved to {output_image_path}", lvl="debug")
        outcome = True
    except subprocess.CalledProcessError as e:
        stash_log(f"ffmpeg error: {e}", lvl="error")
    except Exception as exp:
        stash_log(f"Failed to extract frame {frame_index}", lvl="error")
        stash_log(exp, lvl="error")
        stash_log(traceback.format_exc(), lvl="trace")

    return outcome


def generate_image_filename(stash: StashInterface, scene_path: str) -> str:
    """
    The generate_image_filename function is used to generate a filename for an image.
    The function takes the following parameters:
        stash: StashInterface: Pass the stashinterface object to the function
        scene_path: str: The path to the scene

    :return: The generated filename
    """
    current_index = -1
    prefix = scene_path.rsplit(".", 1)[0] + "_"
    pattern = "^" + re.escape(prefix) + ".*$"
    images = search_images_by_prefix(stash, pattern)
    if images and len(images) > 0:
        for img in images:
            image = extract_image_metadata(img)
            for image_path in image["paths"]:
                if re.match(pattern, image_path):
                    image_filename = Path(image_path).stem
                    suffix = image_filename.rsplit("_")[-1]
                    if suffix.isnumeric():
                        current_index = int(suffix) if int(suffix) > current_index else current_index

    return prefix + str(current_index + 1).zfill(3) + ".jpg"


def scan_library(stash: StashInterface, path):
    """
    The scan_library function is used to scan a directory in Stash.
    The function takes the following parameters:
        :param stash: StashInterface: Pass the stashinterface object to the function
        :param path: str: The path to scan

    :return: The result of the metadata scan
    """
    return stash.metadata_scan([path])
