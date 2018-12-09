# mia_syn_mia_app

This README documents the scripts for the "mia syn mia" app.

## Aims and tasks

The app performs two main functionalities:

1.  It collects the answers/comments of the participants to a particular posts.
2.  It processeses their answers, finds their score and updates the competition's table.

## System Requirements

The code has been developed and tested on a 64-bit version of Windows 10, Python 3.5.4 (64-bit) and the following Python 3 libraries

  * os
  * sys
  * datetime
  * json (version 2.0.9)
  * argparse (version 1.1)
  * re (version 2.2.1)
  * numpy (version 1.13.3)
  * pandas (version 0.23.4)
  * facebook-sdk (version 3.0.0)
  * fuzzywuzzy (version 0.14.0)

### Further Requirements

1. First, the user must register as a developer on Facebook and then have an access token. For further details, follow this [tutorial](https://towardsdatascience.com/how-to-use-facebook-graph-api-and-extract-data-using-python-1839e19d6999).
2. When registered, the user must fill in the `config.json` file with his/her token and user id.

## How to use it

There are two main files in the repository.

1. `extract_predictons.py`, which reads the comments from a post, extracts the participants' predictions and calculates their score for this round. It checks whether a post is valid, i.e. it starts with a username and the prediction (8 numbers) follow, or not. It writes these scores in an output (.csv) file. It requires three input (console) arguments (one is optional):
    * `--post_id` or `-i`, the id of the post under consideration.
    * `--day or -d`,  an integer, the round of the regular season. This is used to store the output file, in the format `predictions_day_x.csv ` where `x` is the round number (i.e. `d`).
    * `--results_file` or `-r`, the file-name of the actual results of this round. The file must be a .txt file and results must be written as a sequence of 1 and 2, with or without spaces. **This is an optional file**. If a filename is not specified the script fetches the results from the Euroleague official page. In this case, a results file is saved on the output directory (see `config/config.json`).

    To execute it, type: `python extract_predictions.py -i post_id -d round_number`
    A predictions file is produced and stored in the output directory (see `config/config.json`), under the filename `predictions_day_x.csv`, where `x` is the round number. 

2. `update_table.py`, which reads the scores files produced with the previous script and updates the table of the competition. It requires three input (console) arguments:
    * `--day` or `-d`, which is an integer representing the current round/game day.
      To execute it, type: `python update_table.py -d round_number`

    The script requires two predictions file produces by the `extract_predictons.py` and the table file of the previous round (if round is not 1).
    A new table is produced and saved in the output directory, under the filename `table_day_x.csv`, where `x` is the round numder.

Three more files are required, stored in the `config/` directory :

  * `config.json`, which includes several configuration options of the app, such as:
    + number of games
    + datetime format of the games in the post
    + output directory
  * `tokens.json`, which include the details of the Facebook graph API tokens.
  * `team_names_mapping.json`, this is a mapping between the Greek names of the teams and their official English name. This file is required to map the English names to Greek ones, when results are fetched online.

**WARNING**: For privacy reasons the `tokens.json` file is not included in this repository.