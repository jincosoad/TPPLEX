import TouchPortalAPI
from plexapi.server import PlexServer
from plexapi.myplex import MyPlexAccount
import threading
import time
import sys
import logging

# Suppress TouchPortalAPI logs
logging.getLogger("TouchPortalAPI").setLevel(logging.CRITICAL)

# Plugin ID must match entry.tp
PLUGIN_ID = "TPPLEX"

# Global variables
TP_CLIENT = None
PLEX_SERVER = None
PLEX_CLIENT = None
PLEX_USERNAME = None
RUNNING = True

def connect_to_plex(settings):
    global PLEX_SERVER, PLEX_CLIENT, PLEX_USERNAME
    
    # Helper to get setting value by name
    def get_setting(name):
        for setting in settings:
            if setting.get("name") == name:
                return setting.get("value")
        return None

    server_url = None
    username = None
    password = None
    client_name = None

    # Parse settings
    print(f"Raw Settings Data Type: {type(settings)}")
    print(f"Raw Settings Data: {settings}")

    if isinstance(settings, list):
        for s in settings:
            # Check for direct key-value pair as seen in logs: {'Setting Name': 'Value'}
            if "Plex Server URL" in s: server_url = s["Plex Server URL"]
            if "Plex Username" in s: username = s["Plex Username"]
            if "Plex Password" in s: password = s["Plex Password"]
            if "Plex Client Name" in s: client_name = s["Plex Client Name"]

            # Also keep support for standard TP format {name: '...', value: '...'} just in case
            name = s.get('name') or s.get('id')
            value = s.get('value')
            if name == "Plex Server URL": server_url = value
            if name == "Plex Username": username = value
            if name == "Plex Password": password = value
            if name == "Plex Client Name": client_name = value
            
    elif isinstance(settings, dict):
        # Handle if it comes as a simple dict {name: value}
        server_url = settings.get("Plex Server URL")
        username = settings.get("Plex Username")
        password = settings.get("Plex Password")
        client_name = settings.get("Plex Client Name")
    
    print(f"Settings received: URL={server_url}, User={username}, Client={client_name}")
    
    PLEX_USERNAME = username

    if not username or not password:
        print("Credentials missing in settings.")
        return

    try:
        print(f"Connecting to Plex as {username}...")
        account = MyPlexAccount(username, password)
        
        # Smart URL handling
        if server_url:
            if "http" not in server_url and (":" in server_url or "." in server_url):
                server_url = f"http://{server_url}"
        
        if server_url and "http" in server_url:
            print(f"Connecting to server at {server_url}...")
            PLEX_SERVER = PlexServer(server_url, account.authenticationToken)
        else:
            resource_name = server_url if server_url else None
            if resource_name:
                print(f"Connecting to server resource: {resource_name}")
                PLEX_SERVER = account.resource(resource_name).connect()
            else:
                print("No Server URL or Name provided.")
                return

        print(f"Connected to Server: {PLEX_SERVER.friendlyName}")
        
        if client_name:
            print(f"Searching for client: {client_name}")
            found = False
            try:
                clients = PLEX_SERVER.clients()
                print(f"Available Clients on Server: {[c.title for c in clients]}")
                for client in clients:
                    if client.title.lower() == client_name.lower():
                        PLEX_CLIENT = client
                        print(f"Found Client: {client.title}")
                        found = True
                        break
            except Exception as e:
                print(f"Error listing clients: {e}")

            if not found:
                print(f"Client {client_name} not found. Trying to find via Account resources...")
                try:
                    resources = account.resources()
                    print(f"Available Resources: {[r.name for r in resources if r.product == 'Plex HTPC']}")
                    for resource in resources:
                        if resource.name.lower() == client_name.lower():
                             print(f"Found Resource match: {resource.name}, Product: {resource.product}")
                             pass
                except Exception as e:
                    print(f"Error listing resources: {e}")
                
                print(f"Client {client_name} not found. Ensure 'Advertise as player' is enabled in Plex HTPC settings.")
                PLEX_CLIENT = None
        
    except Exception as e:
        print(f"Error connecting to Plex: {e}")
        TP_CLIENT.showNotification(f"Plex Connection Error: {e}")

def update_now_playing():
    global RUNNING
    while RUNNING:
        if PLEX_SERVER:
            try:
                sessions = PLEX_SERVER.sessions()
                playing_text = "Nothing Playing"
                
                target_session = None
                
                if sessions:
                    for session in sessions:
                        if PLEX_CLIENT and session.player.title == PLEX_CLIENT.title:
                            target_session = session
                            break
                        
                        if PLEX_USERNAME and session.usernames:
                             if PLEX_USERNAME in session.usernames:
                                 target_session = session
                                 break
                                 
                    if not target_session and sessions:
                        if not PLEX_CLIENT:
                            target_session = sessions[0]

                if target_session:
                    title = target_session.title
                    grandparent = target_session.grandparentTitle if hasattr(target_session, 'grandparentTitle') else None
                    parent = target_session.parentTitle if hasattr(target_session, 'parentTitle') else None
                    
                    if grandparent:
                        playing_text = f"{grandparent} - {title}"
                    elif parent:
                        playing_text = f"{parent} - {title}"
                    else:
                        playing_text = title
                        
                    status = target_session.player.state
                    playing_text += f" ({status})"

                TP_CLIENT.stateUpdate("TPPLEX_NOW_PLAYING", playing_text)
                
            except Exception as e:
                print(f"Error in update loop: {e}")
        
        time.sleep(2)

def action_handler(data):
    global PLEX_CLIENT
    logging.getLogger("TouchPortalAPI").setLevel(logging.CRITICAL)
    if not PLEX_CLIENT:
        print("No Plex Client connected. Cannot execute action.")
        return

    action_id = data['actionId']
    print(f"Executing action: {action_id}")
    
    try:
        PLEX_CLIENT.proxyThroughServer()
        if action_id == "TPPLEX_TOGGLE_PLAY_PAUSE":           
            try:
                PLEX_CLIENT.playPause()
            except:                
                print("Can't use playPause")
                pass
        elif action_id == "TPPLEX_PLAY":
            PLEX_CLIENT.play()
        elif action_id == "TPPLEX_PAUSE":
            PLEX_CLIENT.pause()
        elif action_id == "TPPLEX_STOP":
            PLEX_CLIENT.stop()
        elif action_id == "TPPLEX_NEXT":
            PLEX_CLIENT.skipNext()
        elif action_id == "TPPLEX_PREV":
            PLEX_CLIENT.skipPrevious()
    except Exception as e:
        print(f"Error executing action {action_id}: {e}")

def on_settings(settings, data):
    print("Received settings. Starting connection thread...")
    t = threading.Thread(target=connect_to_plex, args=(settings,))
    t.daemon = True
    t.start()

def on_start(data):
    print("Plugin started. Loading initial settings...")
    
    if 'settings' in data:
        t_conn = threading.Thread(target=connect_to_plex, args=(data['settings'],))
        t_conn.daemon = True
        t_conn.start()
    else:
        print("No settings found in start data.")

    t_poll = threading.Thread(target=update_now_playing)
    t_poll.daemon = True
    t_poll.start()

def on_shutdown(data):
    global RUNNING
    print("Shutting down plugin...")
    RUNNING = False
    sys.exit(0)

# Setup Touch Portal Client
TP_CLIENT = TouchPortalAPI.Client(PLUGIN_ID)
TP_CLIENT.on(TouchPortalAPI.TYPES.onAction, action_handler)
TP_CLIENT.on(TouchPortalAPI.TYPES.onSettingUpdate, on_settings)
TP_CLIENT.on(TouchPortalAPI.TYPES.onConnect, on_start)
TP_CLIENT.on(TouchPortalAPI.TYPES.onShutdown, on_shutdown)

if __name__ == "__main__":
    try:
        TP_CLIENT.connect()
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, exiting.")
        RUNNING = False
    except Exception as e:
        print(f"Main loop exception: {e}")
        RUNNING = False
