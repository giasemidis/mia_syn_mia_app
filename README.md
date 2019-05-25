# mia_syn_mia_app

This README documents the scripts for the "mia syn mia" app.

## Aims and tasks

The app performs three main functionalities:

1. It collects the answers/comments of the participants to a particular posts.
2. It processes their answers, finds their score and updates the competition's table.
3. The processed info (scores, tables, etc.) is written to a flat file with the option of being posted to Facebook.

## Basic Requirements

1. First, the user must register as a developer on Facebook and then have an access token. For further details, follow this [tutorial](https://towardsdatascience.com/how-to-use-facebook-graph-api-and-extract-data-using-python-1839e19d6999).
2. When registered, the user must fill in the `config.json` file with his/her token and user id.

## Scripts and Functionality

There are two main files in the repository.

1. `extract_predictions.py`, which reads the comments from a post, extracts the participants' predictions and calculates their score for this round. It checks whether a post is valid, i.e. it starts with a username and the prediction (8 numbers) follow, or not. It writes these scores in an output (.csv) file. It requires three input (console) arguments (one is optional):
    * `--post_id` or `-i`, the id of the post under consideration.
    * `--day` or `-d`,  an integer, the round of the regular season. This is used to store the output file, in the format `predictions_day_x.csv ` where `x` is the round number (i.e. `d`).
    * `--results_file` or `-r`, (**optional**) the file-name of the actual results of this round. The file must be a .txt file and results must be written as a sequence of 1 and 2, with or without spaces. If a filename is not specified the script fetches the results from the Euroleague official page. In this case, a results file is saved on the output directory (see `config/config.json`).

  A predictions file is produced and stored in the output directory (see `config/config.json`), under the filename `predictions_day_x.csv`, where `x` is the round number.

  To execute it, type:

  `python extract_predictions.py -i <post id> -d <round number>`

2. `update_table.py`, which reads the scores files produced with the previous script and updates the table of the competition. It requires one input (console) arguments:
    * `--day` or `-d`, which is an integer representing the current round/game day.

  The script requires two predictions files produced by the `extract_predictons.py` and the table file of the previous round (if round is not 1).

  A new table is produced and saved in the output directory, under the filename `table_day_x.csv`, where `x` is the round number.

  To execute it, type:

  `python update_table.py -d <round number>`d

3. `post_table.py`, which shapes all the results produces from the previous scripts into a Facebook post. It requires one input argument:
    * `--day` or `-d`, which is an integer representing the current round/game day.

    * `--post` or `-p`, (**optional**) which is a boolean variable indicating whether the message will be posted on Facebook or not.

  It prompts the user to write an additional message. It reads the required information from files produced with the previous scripts and are stored on the output directory (see `config/config.json`). It produces a file called `temp_table.txt.`, which includes all the announcement post of the round.

  To execute it, type:

  `python post_table.py -d <round number>`

Three more files are required, stored in the `config/` directory :

  * `config.json`, which includes several configuration options of the app, such as:
    + number of games
    + datetime format of the games in the post
    + output directory
  * `tokens.json`, which include the details of the Facebook graph API tokens.
  * `team_names_mapping.json`, this is a mapping between the Greek names of the teams and their official English names. This file is required to map the English names to Greek ones, when results are fetched online.

**WARNING**: For privacy reasons the `tokens.json` file is not included in this repository.

All auxiliary files are in the `auxiliary\` directory.

## How to use it

1. Obtain access tokens for the Facebook graph API. Store them in the `config/tokens.json` file.
2. Update the `config/config.json` file with the preferred settings (e.g. output directory).
3. Run the script `extract_predictions.py` to collect the predictions/answers. To do so, first identify the Facebook post id.
4. Run the script `update_table.py` to update the Championship table.
5. If necessary, run the `post_table.py` script to form the message that will be posted on Facebook.
