def load(filename):
    """return a list of dicts from the file. Skip broken lines"""

    records = [] # empty list for the result
    try:
        f = open(filename, "r", encoding="utf-8")
    except FileNotFoundError:
        return records # no file yet, so return an empty list
    with f: 
        for line in f:
            line = line.strip() # removes spaces and new lines
            if line == "":
                continue # skip empty lines
            parts = line.split(";") # split the line by ";"
            try:
                record = {
                    "date": parts[0],
                    "sleep": parts[1],
                    "wake": parts[2],
                    "quality": int(parts[3]),
                }
            except (IndexError, ValueError): # IndexError - too few fields, ValueError - quality is not a number
                print("the damaged line was skipped", line)
                continue
            records.append(record)
    return records        


def save(filename, records):
    """write all records to the file, replacing the old content"""

    with open(filename, "w", encoding="utf-8") as f:
        for r in records:
            f.write(f"{r['date']};{r['sleep']};{r['wake']};{r['quality']}\n")