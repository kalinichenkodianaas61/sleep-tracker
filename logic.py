from datetime import datetime


def sleep_hours(record):
    """return sleep duration of one record (in hours)"""

    start = datetime.strptime(record["sleep"], "%H:%M")
    end = datetime.strptime(record["wake"], "%H:%M")
    seconds = (end - start).total_seconds()
    if seconds < 0: # went to bed before mignight, so add 24 hours
        seconds = seconds + 24 * 3600
    return seconds / 3600


def find_by_quality(records, min_quality, max_quality):
    """return records with quality between min and max (inclusive)"""

    result = []
    for r in records:
        if min_quality <= r["quality"] <= max_quality:
            result.append(r)
    return result


def find_by_duration(records, min_hours, max_hours):
    """return records with sleep duration between min and max hours"""

    result = []
    for r in records:
        if min_hours <= sleep_hours(r) <= max_hours:
            result.append(r)
    return result


def delete_record(records, number):
    """delete record by its number (1 is the first). Return True if deleted"""

    if number < 1 or number > len(records):
        return False  # no such number 
    records.pop(number - 1)
    return True


def average_sleep(records):
    """return average sleep duration in hours, 0 if no records"""

    if len(records) == 0:
        return 0  # avoid division by zero 
    total = 0
    for r in records:
        total = total + sleep_hours(r)
    return total / len(records)


def average_quality(records):
    """return average quality, 0 if no records"""

    if len(records) == 0:
        return 0  # avoid division by zero 
    total = 0
    for r in records:
        total = total + r["quality"]
    return total / len(records)


def shortest_night(records):
    """return the record with the shortest sleep, None if no records"""

    if len(records) == 0:
        return None
    shortest = records[0]
    for r in records:
        if sleep_hours(r) < sleep_hours(shortest):
            shortest = r
    return shortest


def longest_night(records):
    """return the record with the longest sleep, None if no records"""

    if len(records) == 0:
        return None
    longest = records[0]
    for r in records:
        if sleep_hours(r) > sleep_hours(longest):
            longest = r
    return longest