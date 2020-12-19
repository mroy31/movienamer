#!/usr/bin/python3

import argparse
import os
import sys
import logging

from movienamer.identify import identify
from movienamer.confirm import confirm
from movienamer.keywords import video_extensions


def movienamer(movie, lang):
    directory = os.path.dirname(movie)
    filename, extension = os.path.splitext(os.path.basename(movie))

    results = identify(filename, lang, directory)
    if len(results) == 0:
        logging.info("No results found. Skipping movie {}".format(os.path.basename(movie)))
        return False

    action = confirm(results, filename, extension)

    if action == "SKIP":
        logging.info("Skipping movie file")
        return False
    elif action == "QUIT":
        logging.info("Exiting movienamer")
        sys.exit()
    else:
        i = int(action)
        result = results[i - 1]

        if directory == "":
            directory = "."

        dest = (
            directory + "/" + result["title"] + " [" + result["year"] + "]" + extension
        )

        if os.path.isfile(dest):
            print("File '{}' already exists: ".format(dest))
            print("Overwrite?")
            final_confirmation = input("([y]/n/q)").lower()
            if final_confirmation == "":
                final_confirmation = "y"

            if final_confirmation not in ["y", "n", "q"]:
                final_confirmation = input("([y]/n/q)".encode("utf-8")).lower()
                if final_confirmation == "":
                    final_confirmation = "y"

            if final_confirmation == "n":
                logging.info("Skipping movie file")
                return False
            elif final_confirmation == "q":
                logging.info("Exiting movienamer")
                sys.exit()

        return movie, dest


def main():
    parser = argparse.ArgumentParser(
        description="Command-line utlity to organize movies."
    )

    parser.add_argument("movie", nargs="+", help="movie files to rename")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="recursively rename movies in directories",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        default=False,
        help="Show debug messages"
    )

    parser.add_argument(
        "-l",
        "--language",
        type=str,
        dest="language",
        default=None,
        help="Language to use for moviedb search",
    )

    args = vars(parser.parse_args())

    if len(args) == 0:
        raise Exception

    log_level = args["debug"] and logging.DEBUG or logging.INFO
    logging.basicConfig(
        format='%(levelname)s - %(message)s',
        level=log_level)
    movies = []
    errors = []

    if args["recursive"]:
        for movie in args["movie"]:
            if os.path.isfile(movie):
                movies.append(movie)
                continue
            elif not os.path.isdir(movie):
                errors.append(movie)
                continue

            for root, _, files in os.walk(movie):
                for filename in files:
                    _, extension = os.path.splitext(filename)
                    if extension in video_extensions:
                        movies.append(root + "/" + filename)

    else:
        for filename in args["movie"]:
            _, extension = os.path.splitext(filename)
            if extension in video_extensions:
                movies.append(filename)
            else:
                errors.append(filename)

    for i, movie in enumerate(movies):
        result = movienamer(movie, args["language"])
        if result is False:
            errors.append(movie)
        else:
            os.rename(*result)
            logging.info("Movie succesfully renamed")

    if len(errors) > 0:
        logging.info("Unable to rename the following movie files:")
        for i, filename in enumerate(errors):
            logging.error("%d: %s" % (i + 1, filename))


if __name__ == "__main__":
    main()
