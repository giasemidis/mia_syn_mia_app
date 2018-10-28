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

### Further Requirements

1. First, the user must register as a developer on Facebook and then have an access token. For further details, follow this [tutorial](https://towardsdatascience.com/how-to-use-facebook-graph-api-and-extract-data-using-python-1839e19d6999).
2. When registered, the user must fill in the `config.json` file with his/her token and user id.

## How to use it

There are two main files in the repository

1. `extract_predictons.py`, which reads the comments from a post, extracts the participants' predictions and calculates their score for this round. It reads the token and user id from the `tokens.json` file. It writes these scores in an output (.csv) file. It requires three input (console) arguments:
  * `--post_id` or `-i`, the id of the post under consideration.
  * `--results_file` or `-r`, the file-name of the actual results of this round. The file must be a .txt file and results must be written as a string of 1 and 2.
  * `--day or -d`,  an integer, the round of the regular season. This is used to store the output file, in the format `predictions_day_%d.csv `.
    	To run it, type: `python extract_predictions.py -i post_id -r path/to/results_file.txt -d round_number` 
2. `update_table.py`, which reads the scores files produced with the previous script and updates the table of the competition. It requires three input (console) arguments:
  * `--table_file` or `-t`, which is a `.csv` file which stores the current table.
  * `--scores_file` or `-s`, which is a `.csv` file which stores the scores produced in the previous step.
  * `--output` or `-o`, which is a `.csv` file which stores the updated table.
       To run it, type: `python update_table.py -t path/to/table.csv -s path/to/results_file.csv -o path/to/updated_table.csv`

Two more files are required:

  * `config.json`, which includes several configuration options of the app, such as:
    + number of games
    + datetime format of the games in the post
    + output directory
  * `tokens.json`, which include the details of the Facebook graph API tokens.

**WARNING**: For privacy reasons the `tokens.json` file is not included in this repository.