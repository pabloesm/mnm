from subprocess import Popen, PIPE

from scraper.logger import get_logger

log = get_logger()


def comment_story(
    username: str,
    password: str,
    story_id: int,
    proxy_config: str,
    comment: str,
) -> int:
    script_name = "mnm.js"

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
        log.warning(f"Return code: {process.returncode}")
        log.warning(f"Args used: {process.args}")

    return process.returncode
