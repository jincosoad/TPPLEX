# Plex Touch Portal Plugin

A Touch Portal plugin to control your Plex HTPC or client directly from your deck. This plugin allows you to view what's currently playing and control playback (Play, Pause, Stop, Next, Previous) using the Plex API.

## Features

-   **Control Playback**: Play, Pause, Stop, Next Track, Previous Track.
-   **Toggle Play/Pause**: A single button to toggle playback state.
-   **Now Playing Info**: Displays the title of the media currently playing on your Plex client.
-   **Client Discovery**: Automatically finds and connects to your specified Plex client (HTPC, Smart TV, etc.).
-   **Robust Connection**: Handles connection drops and attempts to reconnect automatically.

## Installation

### From Release (Recommended)
1.  Download the `.tpp` file from the [Releases](releases) page (if available).
2.  Open Touch Portal.
3.  Click the "Settings" (gear) icon -> "Plug-ins" -> "Import Plug-in".
4.  Select the downloaded `.tpp` file.
5.  Restart Touch Portal.

### From Source
1.  Clone this repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Build the executable using PyInstaller:
    ```bash
    pyinstaller --onefile --noconsole --name main --distpath . main.py
    ```
4.  Import the plugin into Touch Portal manually by copying the folder to `%APPDATA%\TouchPortal\plugins\TPPLEX`.

## Configuration

After installing, configure the plugin in Touch Portal settings:

1.  **Plex Server URL**: The IP address and port of your Plex Server (e.g., `192.168.1.72:32400`).
2.  **Plex Username**: Your Plex account username.
3.  **Plex Password**: Your Plex account password.
4.  **Plex Client Name**: The name of the Plex client you want to control (e.g., `Plex HTPC`, `Living Room TV`, `DESKTOP-92LLBVC`).
    *   *Tip: Ensure your client app is running and "Advertise as player" is enabled in its settings.*

## Usage

1.  Create a button in Touch Portal.
2.  On the left side, look for the **Plex** category.
3.  Add actions like **Plex: Play**, **Plex: Pause**, or **Plex: Toggle Play/Pause**.
4.  To see what's playing, add a text object to your button and set its value to the **Plex Now Playing** state (e.g., `%TPPLEX_NOW_PLAYING%`).

## Troubleshooting

-   **"No Plex Client connected"**: Ensure the "Plex Client Name" matches exactly what is shown in your Plex Dashboard. Check the plugin logs for a list of discovered clients.
-   **Connection Errors**: Verify your IP address and credentials. If using 2FA, you might need to use an authentication token instead of a password (support pending).
-   **sometimes the toggle play/pause option is not working
## Built With

-   [TouchPortal-API](https://github.com/KillerBOSS2019/TouchPortal-API) - Python SDK for Touch Portal.
-   [PlexAPI](https://github.com/pkkid/python-plexapi) - Python bindings for the Plex API.
