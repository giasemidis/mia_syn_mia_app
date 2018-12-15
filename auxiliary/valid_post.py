# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 01:22:05 2018

@author: Georgios
"""
import re
import numpy as np


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
        print('\nWarning: Username not found')
        print(message)
    elif len(find_name[0].strip()) > 25:
        # Strings longer than 25 characters are *not* considered valid 
        # usernames. They are probably text.
        red_flag1 = True
        print('\nWarning: Username not valid in comment id %s' % comment_id)
        print(message)
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
    find_pred = re.findall('\d', message[:offset])

    if find_pred == [] or find_pred is None:
        red_flag2 = True
        print('\nWarning: Prediction not found in comment id %s' % comment_id)
        print(message)
    else:
        # convert predictions to an array of integers
        preds = np.array([int(u) for u in find_pred])

        # check if predictions are either 1 or 2
        if not ((preds == 1) | (preds == 2)).all():
            yellow_flag1 = True
            print('\nWarning: Incorrect prediction(s) for user %s in comment_id %s.' 
                  % (username, comment_id))
            print(message)
#            preds[~((preds == 1) | (preds == 2))] = 0

        # check if number of predictions is correct
        n_preds = preds.shape[0]
        if n_preds == n_games:
            pass
        elif n_preds > n_games and n_preds < n_games+3:
            # if the number of predictions is more then 'n_games', keep the 
            # first 'n_games'.
            # If the number of predictions is more than 'n_games'+3, then flag
            # the message as commentary.
            print('\nWarning: More than %d predictions are given' % n_games)
            preds = preds[:n_games]
            print(message)
            yellow_flag2 = True
        elif n_preds < n_games and n_preds > n_games-3:
            # if the number of predictions is less than 'n_games', fill in 
            # the remaining ones with zeros.
            # if the number of predictions is less than 'n_games'-3, e.g. 121, 
            # then flag the message as commentary.
            print('\nWarning: Less than %d predictions are given' % n_games)
            preds = np.append(preds, np.zeros(n_games-preds.shape[0], 
                                                    dtype=int))
            print(message)
            yellow_flag2 = True
        else:
            red_flag3 = True
            print('\nWarning: This message is likely to be commentary (comment id %s)'
                                                            % comment_id)
            print(message)
        
    # if any of the red flags is true, the post is invalid. 
    # if both the prediction values and the number are wrong, then it is 
    # possible the comment is a no-prediction comment, just a usual textual
    # comment.
    is_valid = ((not red_flag1) and (not red_flag2) and (not red_flag3)) and\
               ((not yellow_flag1) or (not yellow_flag2))

    return is_valid, username, preds

if __name__ == "__main__":
    # For testing
    c1 = 'Πρώτο Μεσαίο Όνομα 1212 1212'
    c2 = 'First Middle Name 12121212'
    c3 = 'First Middle Name 1-2-1-2 1-2-1-2'
    c4 = 'First Middle Name 1-2-1-2-1-2-1-2'
    c5 = 'First Middle Name1212 1212'
    c6 = 'First Middle Name 1 2 1 2 1 2 1 2'
    c7 = 'First Middle Name12121212'
    c8 = 'First Middle Name1-2-1-2-1-2-1-2'
    c9 = 'First Middle Name-1-2-1-2-1-2-1-2'
    c10 = '1212 1212'
    c11 = '1-2-2-1 1-2-2-1'
    c12 = '1212 121'
    c13 = 'First Middle Name 1221 121'
    c14 = 'First Middle Name 1221 12121'
    c15 = 'First Middle Name'
    c16 = 'Random 121'
    c17 = 'First Middle Name 121 more text comment'
    c18 = 'First Middle Name 1211-1231'
    c19 = 'this is a very random string with-some 12 numeric characters'
    extra_message = ' more text after the prediction 12 ασσιστς'
    cs = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, 
          c15, c16, c17, c18, c19]
    for comment in cs:
        print()
        print(comment)
        a, b, c = valid_post(comment)
        print(a, b, c)
        a, b, c = valid_post(comment + extra_message)
        print(a, b, c)
    
