import logging
from subprocess import Popen, PIPE

DOMAIN_TO_SCRIPT = {
    "elconfidencial.com": "commentsElconfidencial.js",
}


def extract_comments(url_full: str, url_domain: str, news_id: int) -> int:
    script_name = DOMAIN_TO_SCRIPT[url_domain]
    command = [
        "node",
        f"scripts/node/{script_name}",
        f"--url_full={url_full}",
        f"--url_domain={url_domain}",
        f"--news_id={news_id}",
    ]
    # https://stackoverflow.com/a/28319191/3782161
    with Popen(command, stdout=PIPE, bufsize=1, universal_newlines=True) as process:
        for line in process.stdout:
            print(line, end="")  # process line here

    if process.returncode != 0:
        logging.warning(f"Return code: {process.returncode}")
        logging.warning(f"Args used: {process.args}")

    return process.returncode
