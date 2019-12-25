import re
import numpy as np
import logging


def valid_post(message, comment_id=1, n_games=8):
    '''
    Checks the validity of a post. Valid posts must have the following format:
        1) start with the username
        2) prediction ('n_games' numbers of 1 or 2) must follow with or
            without spaces and/or dashes between the numbers.
        3) Any other comment of the user follows.
    Returns three variables:
        1) a boolean whether the post is valid or not
        2) the username, and empty string if username is not found
        3) the predictions as an numpy array, an empty list if predictions not
            found/valid.

    We allow a little room for inconsistancies, either
    if a user misses 'a few' predictions, they are replaced with 0s,
    post still valid, or
    if a user has 'a few' more predictions, it truncates them, post still
    valid, or
    if the prediction has 'a few' numbers other than 1 or 2, post still valid.
    '''
    logger = logging.getLogger(__name__)

    red_flag1 = False
    red_flag2 = False
    red_flag3 = False
    yellow_flag1 = False
    yellow_flag2 = False
    offset = len(message)
    username = ''
    preds = []

    # a valid post must start with the username.
    find_name = re.findall('^[^0-9-]+', message)

    if find_name == [] or find_name is None:
        red_flag1 = True
        logger.warning('Username not found in comment (id %s): "%s"',
                       comment_id, message)
    elif len(find_name[0].strip()) > 30:
        # Strings longer than 25 characters are *not* considered valid
        # usernames. They are probably text.
        red_flag1 = True
        logger.warning('Username not valid in comment (id %s): "%s"',
                       comment_id, message)
    else:
        username = find_name[0].strip()
        # find when the next string of non-numeric characters appears
        # after the prediction, i.e. find where the user's comment starts.
        find_strs = re.findall('[^0-9-]+', message)
        strs = [part for part in find_strs if part.strip() != '']
        offset = len(message) if len(strs) == 1 else message.find(strs[1])
        offset = len(message) if offset == -1 else offset

    # if username not found, do not process the rest of the message.
    if red_flag1:
        return False, username, preds

    # find all numeric characters (we search for all numeric and not
    # only 1 or 2), in case the user has mistyped one, e.g. 1113 1111
    # In this case, the user will miss only a single prediction, see below.
    find_pred = re.findall(r'\d', message[:offset])

    if find_pred == [] or find_pred is None:
        red_flag2 = True
        logger.warning('Prediction not found in comment (id %s): "%s"',
                       comment_id, message)
    else:
        # convert predictions to an array of integers
        preds = np.array([int(u) for u in find_pred])

        # check if predictions are either 1 or 2
        if not ((preds == 1) | (preds == 2)).all():
            yellow_flag1 = True
            logger.warning('Incorrect prediction(s) for user %s in comment '
                           '(id %s): "%s"', username, comment_id, message)

        # check if number of predictions is correct
        n_preds = preds.shape[0]
        if n_preds == n_games:
            pass
        elif n_preds > n_games and n_preds < n_games + 3:
            # if the number of predictions is more then 'n_games', keep the
            # first 'n_games'.
            # If the number of predictions is more than 'n_games'+3, then flag
            # the message as commentary.
            logger.warning('More than %d predictions are given: "%s"',
                           n_games, message)
            preds = preds[:n_games]
            yellow_flag2 = True
        elif n_preds < n_games and n_preds > n_games - 3:
            # if the number of predictions is less than 'n_games', fill in
            # the remaining ones with zeros.
            # if the number of predictions is less than 'n_games'-3, e.g. 121,
            # then flag the message as commentary.
            logger.warning('Less than %d predictions are given: "%s"',
                           n_games, message)
            preds = np.append(preds, np.zeros(n_games - preds.shape[0],
                                              dtype=int))
            yellow_flag2 = True
        else:
            red_flag3 = True
            logger.warning('This message is likely to be commentary '
                           '(id %s): %s', comment_id, message)

    # if any of the red flags is true, the post is invalid.
    # if both the prediction values and the number are wrong, then it is
    # possible the comment is a no-prediction comment, just a usual textual
    # comment.
    is_valid = ((not red_flag1) and (not red_flag2) and (not red_flag3)) and\
               ((not yellow_flag1) or (not yellow_flag2))

    return is_valid, username, preds
