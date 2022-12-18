from subprocess import Popen, PIPE, CalledProcessError


def run_node_script(url_full: str, url_domain: str, news_id: int) -> None:
    command = [
        "node",
        "scripts/node/commentsElconfidencial.js",
        f"--url_full={url_full}",
        f"--url_domain={url_domain}",
        f"--news_id={news_id}",
    ]
    # https://stackoverflow.com/a/28319191/3782161
    with Popen(command, stdout=PIPE, bufsize=1, universal_newlines=True) as process:
        for line in process.stdout:
            print(line, end="")  # process line here

    if process.returncode != 0:
        raise CalledProcessError(process.returncode, process.args)
