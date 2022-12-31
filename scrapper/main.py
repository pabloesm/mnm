import logging

from scrapper.update_queue import update_queue
from scrapper.run_node_script import run_node_script

logging.basicConfig(level=logging.INFO)

url_full = "https://www.elconfidencial.com/espana/aragon/2022-11-27/espana-vaciada-partido-politico-confederado-irrumpir-congreso_3530332/"
url_domain = "elconfidencial.com"
news_id = 3760503


def main() -> None:
    logging.info("main() starting")
    try:
        run_node_script(url_full, url_domain, news_id)
        update_queue()
    except Exception:
        logging.info("Scrapper failed.")

    logging.info("main() done")


if __name__ == "__main__":
    main()
