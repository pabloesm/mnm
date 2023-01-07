import logging
from subprocess import Popen, PIPE


def comment_story() -> int:
    script_name = "mnm.js"
    username = "flavs"
    password = "3dC600!deJok"
    story_id = 3766164
    proxy_config = '{"server": "188.74.183.10:8279", "username": "tahdrccj", "password": "phyn15nz0j3m"}'
    comment = "De lo que se deduce que se puede ser un inteligente intelectual y un bobo social. \nMucho ha durado, que ella tiene los tiempos controlados."

    command = [
        "node",
        f"scripts/node/{script_name}",
        f"--username={username}",
        f"--password={password}",
        f"--story_id={story_id}",
        f"--proxy_config={proxy_config}",
        f"--comment={comment}",
    ]
    # https://stackoverflow.com/a/28319191/3782161
    with Popen(command, stdout=PIPE, bufsize=1, universal_newlines=True) as process:
        for line in process.stdout:
            print(line, end="")  # process line here

    if process.returncode != 0:
        logging.warning(f"Return code: {process.returncode}")
        logging.warning(f"Args used: {process.args}")

    return process.returncode
