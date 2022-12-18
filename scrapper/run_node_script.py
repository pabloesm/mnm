from subprocess import Popen, PIPE, CalledProcessError

command = [
    "node",
    "scripts/node/commentsElconfidencial.js",
    "--url_full=https://www.elconfidencial.com/espana/aragon/2022-11-27/espana-vaciada-partido-politico-confederado-irrumpir-congreso_3530332/",
    "--url_domain=elconfidencial.com",
    "--news_id=3760503",
]

# https://stackoverflow.com/a/28319191/3782161
with Popen(command, stdout=PIPE, bufsize=1, universal_newlines=True) as process:
    for line in process.stdout:
        print(line, end="")  # process line here

if process.returncode != 0:
    raise CalledProcessError(process.returncode, process.args)
