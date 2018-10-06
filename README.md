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

1. `extract_predictons.py`, which reads the comments of a post, extracts the participants' predictions and calculates their score for this round. It reads the token and user id from the `config.json` file. It writes these scores in an output file. It requires three input (console) arguments:
  * `--post_id` or `-i`, the id of the post of the round under consideration.
  * `--results_file` or `-r`, the file-name of the actual results of this round. The file must be a txt file and results must be written as a string of 1s or 2s.
  * `--output` or `-o`, the filename of the output file, where the scores will be stored.
  	To run it, type: `python extract_predictions.py -i 12345678 -r path/to/results_file.txt -o path/to/output_file.json`
2. `update_table.py`, which reads the scores files produced by the previous scripts and updates the table of the competition. It reads the user-names and their corresponding useri ds from the `usernames.json` file. It requires three input (console) arguments:
  * `--table_file` or `-t`, which is a `.csv` file which stores the current table.
  * `--scores_file` or `-s`, which is a `.json` file which stores the scores produced in the previous step.
  * `--output` or `-o`, which is a `.csv` file which stores the updated table.
  	To run it, type: `python update_table.py -t path/to/table.csv -s path/to/results_file.json -o path/to/updated_table.csv`

**WARNING**: For privacy reasons both the `config.json` and `usernames.json` are not filled in in this repository.