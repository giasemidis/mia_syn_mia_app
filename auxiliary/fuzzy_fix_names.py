from fuzzywuzzy import process
import logging


def fuzzy_fix_names(names_to_check, true_names, threshold=85):
    '''
    This functions checks the names (strs) in 'names_to_check' variable and
    finds the best (fuzzy) match against the 'true_names' list, which
    represents the true names. If the matching score is 100, no change
    is applied, if it is lower than 100 and higher than 'threshold', the
    best matching true name replaces the corresponding str, otherwise,
    a new name, with no close match, is found.
    '''
    logging.getLogger(__name__)
    new_names = names_to_check.copy()

    for n, name in enumerate(names_to_check):
        bestmatch = process.extractOne(name, true_names)
        if bestmatch[1] == 100:
            # exact match
            continue
        elif bestmatch[1] >= threshold:
            # close match, same user
            if bestmatch[0] in new_names:
                logging.info('Name %s matched to %s, which already exists',
                             name, bestmatch[0])
            else:
                new_names[n] = bestmatch[0]
                logging.warning('Altered name in list. %s - %s - %d',
                                name, bestmatch[0], bestmatch[1])
        elif bestmatch[1] < threshold:
            # possible new user
            logging.info('New name in list. %s - %s - %d',
                         name, bestmatch[0], bestmatch[1])

    return new_names
