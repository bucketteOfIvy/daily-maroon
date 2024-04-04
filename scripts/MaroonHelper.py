### Author: Ashlynn Wimer
### Date: 4/4/2024
### About: Helper functions for a miniature content analysis
###        of Daily Maroon data.
import re

def read_text(fileloc: str, encoding: str = 'utf-8') -> str:
    '''
    Given the location of a text file, read it in and return its content
    as string.
    '''
    s = None
    with open(fileloc, encoding=encoding) as f:
        s = f.readlines()

    return ' '.join(s).strip()    

def clean_text(s: str) -> str:
    '''
    Lowercase a string, replace all punctuation with spaces, and remove duplicate
    spaces.
    '''
    return re.sub('\s+', ' ', re.sub('[^\s\w]', ' ', s.lower()))

def lemmatize_matches(s: str) -> str:
    '''
    People used to be weirdos who would write "63d" instead of "63rd". 
    This function just accounts for the ambiguity.
    '''
    if re.match('(\d{2,}d st)', s):
        return re.sub('d', 'rd', s)
    return s

def count_all_streets(s: str, cnts: dict={}) -> dict:
    '''
    Count the number of times any numbered east-west street is mentioned in a 
    given piece of text.
    '''
    streets = [lemmatize_matches(x[0]) for x in re.findall('(\d{2,}(rd|th|nd|st|d) st)', s)]
    
    # consider additional cleaning mb?

    for street in streets:
        cnts[street] = cnts.get(street, 0) + 1
    
    return cnts

def title_to_dates(title: str) -> tuple:
    '''
    Given the title of a Daily Maroon text file, 
    return the month, day, year as a str 3-tuple.
    '''
    rv = re.sub('.txt|,|Daily Maroon', '', title).strip()
    return rv.split()

def count_some_streets(s: str, to_cnt: list=[]) -> dict:
    '''
    Given a list of streets whose occurence should be counted, 
    count the number of occurrences in the text.
    '''
    all_streets = [lemmatize_matches(x[0]) for x in re.findall('(\d{2,}(rd|th|nd|st|d) st)', s)]

    cnts = {street:0 for street in to_cnt}

    for street in all_streets:
        if street in to_cnt: cnts[street] = cnts[street] + 1
    
    return cnts