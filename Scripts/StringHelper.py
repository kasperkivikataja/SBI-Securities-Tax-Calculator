def clean_date_string(line: str) -> str:
    #Clean a date string from Japanese characters
    cleaned_line = line.replace("年", "/")
    cleaned_line = cleaned_line.replace("月", "/")
    cleaned_line = cleaned_line.replace("日", "")
    cleaned_line = cleaned_line.replace("　", "")
    cleaned_line = cleaned_line.replace(" ", "")
    return cleaned_line