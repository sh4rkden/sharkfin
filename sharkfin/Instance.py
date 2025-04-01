import re
import asyncio
from glob import glob
from os import getenv, path

class Sharkfin:
    def __init__(self):
        self._event_handlers = {}
        self.cookie_consent = False

    def event(self, function):
        event_name = function.__name__
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(function)
        return function

    async def dispatch_event(self, event_name, *args, **kwargs):
        handlers = self._event_handlers.get(event_name, [])
        for handler in handlers:
            await handler(*args, **kwargs)
            print(f"DEBUG: {handler.__name__} has been called with args:{args} and kwargs:{kwargs}")

    async def _run(self):
        print("INFO: Sharkfin (instance) has been started.")
        await LogShark.event_monitor(self)

    def run(self):
        asyncio.run(self._run())

class LogShark(Sharkfin):
    async def event_monitor(self):
        print("INFO: LogShark has been Started.")
        log_directory = path.join(getenv("LOCALAPPDATA"), "Roblox", "logs")
        log_files = glob(path.join(log_directory, "*.log"))

        if not log_files:
            print("ERROR: No log files found.")
            return

        latest_log = max(log_files, key=path.getctime)
        read_pos = path.getsize(latest_log)
        print(f"INFO: Monitoring current log: {latest_log}")
        while True:
            current_files = glob(path.join(log_directory, "*.log"))
            if current_files:
                current_log = max(current_files, key=path.getctime)
            else:
                current_log = None

            if current_log and current_log != latest_log:
                latest_log = current_log
                read_pos = 0
                print(f"INFO: Monitoring new log: {latest_log}")

            with open(latest_log, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(read_pos)
                new_lines = f.readlines()
                read_pos = f.tell()

                for line in new_lines:
                    message_sent = re.search(r"Sending Text: (.*)", line)
                    message_received = re.search(r"Success Text: (.*)", line)
                    player_joiend = re.search(r"Player added: (.*)", line)
                    player_left = re.search(r"Player removed: (.*)", line)
                    player_spawned = re.search(r"Local character loaded: (.*)", line)
                    game_joining = re.search(r"! Joining game (.*)", line)
                    game_joined = re.search(r"placeid:(\d+).*?universeid:(\d+).*?referral_page:([^,]*).*?sid:([\w-]+).*?userid:(\d+)", line)
                    game_leave = re.search(r"leaveUGCGameInternal", line)

                    if message_sent:
                        message = message_sent.group(1)
                        await self.dispatch_event("message_send", message)
                    elif message_received:
                        message = message_received.group(1)
                        await self.dispatch_event("message_receive", message)

                    if player_joiend:
                        player = player_joiend.group(1).split(" ")
                        if len(player) >= 2:
                            user, id = player[0], player[1]
                            await self.dispatch_event("player_joined", user, int(id))
                        else:
                            print("ERROR: Player joined log format unexpected.")
                    elif player_spawned:
                        player = player_spawned.group(1)
                        await self.dispatch_event("player_spawned", player)
                    elif player_left:
                        player = player_left.group(1).split(" ")
                        if len(player) >= 2:
                            user, id = player[0], player[1]
                            await self.dispatch_event("player_left", user, int(id))
                        else:
                            print("ERROR: Player left log format unexpected.")
                    
                    if game_joining:
                        game = game_joining.group(1)
                        game_match = re.search(r"'([a-f0-9\-]+)'\s+place\s+(\d+)\s+at\s+([\d\.]+)", game)
                        if game_match:
                            instance_id, game_id = game_match.group(1), game_match.group(2)
                            await self.dispatch_event("game_joining", instance_id, game_id)
                        else:
                            print("ERROR: Game info did not match expected format.")
                    elif game_joined:
                        game_match = game_joined
                        if game_match:
                            place_id, universe_id, referral_page, instance_id, user_id = game_match.groups()
                            await self.dispatch_event("game_joined", place_id, universe_id, referral_page, instance_id, user_id)
                        else:
                            print("ERROR: Joined info did not match expected format.")
                    elif game_leave:
                        await self.dispatch_event("game_leave")

            await asyncio.sleep(0.01)

class SharkfinTools(Sharkfin):
    ...
    
class Exceptions:
    class NoCookieConsent(Exception):
        def __init__(self, message: str = "No consent was given to use the Roblox Cookie of the User."):
            super().__init__(message)
