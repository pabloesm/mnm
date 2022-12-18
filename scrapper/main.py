import logging

from scrapper.update_queue import update_queue

logging.basicConfig(level=logging.INFO)


def main() -> None:
    logging.info("main() starting")
    update_queue()
    logging.info("main() done")


if __name__ == "__main__":
    main()
