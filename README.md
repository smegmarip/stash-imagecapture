# Stash Image Capture

Creates images in stash from a scene screenshot.

## Description

This plugin creates a new stash image from the frame at the current playhead position of a scene video.

## Getting Started

### Dependencies

- [Python](https://www.python.org/downloads/) Version 3.7+
- [StashUserscriptLibrary](https://github.com/stashapp/CommunityScripts/tree/a3d00d4455dae00fbe9648173b252643f8ae287f/plugins/stashUserscriptLibrary)

_Note_: StashUserscriptLibrary has been deprecated and removed. This plugin uses the old stashUserscriptLibrary.js library which is not available through the plugin interface and has been added as a local dependency.

### Installing

1. Clone and copy the `stash-imagecapture` folder to the `config/plugins` directory.
2. Run `sudo apt-get install python3-opencv` on debian distros or the equivalent for your OS.
3. Run `pip install -r requirements.txt` inside the `stash-imagecapture/python` folder.
4. Optionally, for file-based logging, create a `config.py` file inside the `python` folder and copy the contents of `imagecapture_defaults.py`. Change the `stash_logfile` value to the path of your log file.

### Running the plugin

- In Stash, go to `Settings > Plugin`
- Under Plugins, click `Reload Plugins` to detect the plugin.
- Play or scrub a scene and pause at the desired frame.
- Click the camera icon above the tabbed interface to create the captured image.

## Help

TBA

## Authors

Contributors names and contact info

Smegmarip

## Version History

- 0.0.3
  - Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.

- [Stash](https://github.com/stashapp/stash)
