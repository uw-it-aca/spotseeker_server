import re


def clean_html(html_string):
    """ Takes in a string containing html and removes the html tags. """
    cleaner = re.compile('<.*?>')

    cleaned_string = re.sub(cleaner, '', html_string)

    return cleaned_string
