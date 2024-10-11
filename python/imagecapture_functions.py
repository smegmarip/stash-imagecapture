"""
Image Capture Functions
These functions are used to capture a frame from a video and save it as an image.
:doc-author: smegmarip
"""

from pathlib import Path
import re
import sys
import traceback

import cv2
import ffmpeg
import numpy as np

from common import (
    extract_image_metadata,
    extract_scene_metadata,
    search_images_by_prefix,
    stash_log,
    the_id,
    to_integer,
)

try:
    import stashapi.log as log
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
            scene_folder = scene_data["folderpath"] + "/"
            scene_path = str(scene_data["path"])
            capture_filename = generate_image_filename(stash, scene_path)
            result = extract_frame(scene_data, int(frame_idx), capture_filename)

            if result:
                result = capture_filename
                # scan_library(stash, scene_folder)
    return {"result": result}


def extract_frame(scene_data: dict, frame_index: int, output_image_path: str) -> bool:
    """
    Extract a single frame from a video and save it.

    :param scene_data: dict: Scene
    :param frame_index: int: Frame index
    :param output_image_path: str: Output image path
    :return: bool: Success
    """
    video_path = scene_data["path"]
    stash_log(
        {"video_path": video_path, "frame_index": frame_index, "output_image_path": output_image_path}, lvl="trace"
    )
    outcome = False

    # Get the video orientation
    orientation = get_rotation(video_path)
    stash_log(f"Video orientation: {orientation}", lvl="debug")

    # Open the video file
    video_capture = cv2.VideoCapture(video_path)

    # Set the frame position
    video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)

    try:
        # Read the frame
        success, frame = video_capture.read()

        # Correct the frame size
        frame = normalize_frame_rotation(frame, orientation)

        if success:
            # Save the extracted frame as an image
            cv2.imwrite(output_image_path, frame)
            stash_log(f"Frame {frame_index} saved to {output_image_path}", lvl="debug")
            outcome = True
        else:
            stash_log(f"Failed to extract frame {frame_index}", lvl="error")
    except Exception as exp:
        stash_log(f"Failed to extract frame {frame_index}", lvl="error")
        stash_log(exp, lvl="error")
        stash_log(traceback.format_exc(), lvl="trace")

    # Release the video capture object
    video_capture.release()
    return outcome


def get_rotation(video_file_path: str):
    """
    The get_rotation function is used to extract the rotation information from a video file.
    The function takes the following parameters:
        video_file_path: str: The path to the video file

    :return: The rotation information
    """
    try:
        # fetch video metadata
        metadata = ffmpeg.probe(video_file_path)
    except Exception as e:
        stash_log(e, lvl="error")
        stash_log(f"failed to read video: {video_file_path}\n", lvl="error")
        stash_log(traceback.format_exc(), lvl="trace")
        return None
    # extract rotate info from metadata
    video_stream = next((stream for stream in metadata["streams"] if stream["codec_type"] == "video"), None)
    rotation = int(video_stream.get("tags", {}).get("rotate", 0))
    # extract rotation info from side_data_list, popular for Iphones
    if len(video_stream.get("side_data_list", [])) != 0:
        side_data = next(iter(video_stream.get("side_data_list")))
        side_data_rotation = int(side_data.get("rotation", 0))
        if side_data_rotation != 0:
            rotation -= side_data_rotation

    # If no rotation data is found, infer from display aspect ratio (DAR)
    if rotation == 0:
        dar = video_stream.get("display_aspect_ratio")
        if dar:
            width, height = map(int, dar.split(":"))
            if width > height:
                rotation = 0  # Assume landscape
            elif width < height:
                rotation = 90  # Assume portrait
            else:
                rotation = 0  # Square video, no rotation inferred

    return rotation


def normalize_frame_rotation(frame: np.ndarray, rotation: int):
    """
    The normalize_frame_rotation function is used to normalize the rotation of a frame.
    The function takes the following parameters:
        frame: np.ndarray: The frame to normalize
        rotation: int: The rotation information

    :return: The normalized frame
    """
    width = frame.shape[1]
    height = frame.shape[0]
    frame_orientation = "portrait" if height > width else "landscape"
    stash_log(f"Frame orientation: {frame_orientation}", lvl="debug")
    if frame_orientation == "landscape":
        if rotation == 90 or rotation == 270:
            frame = cv2.resize(frame, (height, width))
            stash_log(f"Frame resized to {height}x{width}", lvl="debug")
    elif frame_orientation == "portrait":
        if rotation == 0 or rotation == 180:
            frame = cv2.resize(frame, (height, width))
            stash_log(f"Frame resized to {height}x{width}", lvl="debug")
    return frame


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
