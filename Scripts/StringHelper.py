"""
    Developer: Kasper Kivikataja
    Date: May 1st, 2025
    Purpose: Support methods.
"""

import unicodedata
from datetime import datetime

# Cleaning Methods
def clean_line_strip_and_unicode_normalize(line):
    cleaned_line = line.strip()
    cleaned_line = unicodedata.normalize('NFKC', cleaned_line)
    cleaned_line = cleaned_line.replace(",", ".")
    cleaned_line = cleaned_line.replace("、", ".")
    return cleaned_line

def clean_line_date_string(line):
    #Clean a date string from Japanese characters
    cleaned_line = line.replace("年", "/")
    cleaned_line = cleaned_line.replace("月", "/")
    cleaned_line = cleaned_line.replace("日", "")
    cleaned_line = clean_line_empty_spaces(cleaned_line)
    return cleaned_line

def clean_line_parenthesis(line):
    cleaned_line = line.replace("(", "")
    cleaned_line = cleaned_line.replace(")", "")
    return cleaned_line

def clean_line_empty_spaces(line):
    cleaned_line = line.replace(" ", "")
    cleaned_line = cleaned_line.replace("　", "") # Japanese space
    return cleaned_line

# With most Integers, we can just remove commas and dots. Need to be careful with this because of exception:
# Exception: Some integers like 約定価格 (ex. 5.765) are exceptions, and should not remove the dot.
def replace_commas_with_empty(line):
    cleaned_line = line.replace(",", "")
    cleaned_line = cleaned_line.replace("、", "")
    return cleaned_line

def replace_dots_with_empty(line):
    cleaned_line = line.replace(".", "")
    return cleaned_line

# --------------------------------------------------------------------------------------------- #

# Check Methods
def is_date(string):
    try:
        datetime.strptime(string, "%Y/%m/%d")
        return True
    except ValueError:
        return False