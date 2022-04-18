import json
import random
import subprocess
import sys

from utils import fuzz_command, load_blocklists

payload_id = sys.argv[1]
actions_to_fuzz = sys.argv[2]
plugin_slug = sys.argv[3]

if actions_to_fuzz == "ALL":
    actions_to_fuzz = subprocess.check_output(
        [
            "php.orig",
            "/fuzzer/get_fuzzable_entrypoints/get_menu_actions_to_fuzz.php",
        ]
    )

    actions_to_fuzz = [
        action.strip().replace("MENU: ", "")
        for action in actions_to_fuzz.decode("ascii", errors="ignore").split("\n")
        if action.startswith("MENU: ")
    ]

    random.shuffle(actions_to_fuzz)
else:
    actions_to_fuzz = actions_to_fuzz.split(",")

actions_to_skip = load_blocklists("menu", plugin_slug)

command_results = []
for action in actions_to_fuzz:
    if action in actions_to_skip:
        continue

    sys.stderr.write(f"Fuzzing: {action}\n")
    sys.stderr.flush()

    object_name = "menu: " + action
    command_results += fuzz_command(
        f"TOP_LEVEL_NAVIGATION_ONLY=1 php /fuzzer/execute/do_menu_action.php '{action}'",
        payload_id,
        object_name,
    )
print(json.dumps(command_results))