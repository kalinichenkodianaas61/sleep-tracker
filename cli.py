import sys
from datetime import datetime

import storage
import logic

FILE = "data.txt"


def is_valid_date(text):
    """check that text is a date like 12-10-26"""

    try:
        datetime.strptime(text, "%d-%m-%y")
    except ValueError:
        return False
    return True


def is_valid_time(text):
    """check that text is a time like 23:30"""

    try:
        datetime.strptime(text, "%H:%M")
    except ValueError:
        return False
    return True


def print_record(number, r):
    """print one record as a line"""

    hours = logic.sleep_hours(r)
    print(f"{number:>3}  {r['date']}  {r['sleep']} -> {r['wake']}  "
          f"{hours:5.2f} h  quality {r['quality']:>3}")


def print_found(records, found):
    """print found records with their numbers from the full list"""

    if len(found) == 0:
        print("nothing found") 
        return
    for number, r in enumerate(records, start=1):
        if r in found:
            print_record(number, r)


def command_add(records):
    """add DATE SLEEP WAKE QUALITY"""

    if len(sys.argv) < 6:
        print("using: python cli.py add DD-MM-YY SLEEP WAKE QUALITY")
        print("example: python cli.py add 12-10-26 23:30 07:15 80")
        return
    date, sleep, wake = sys.argv[2], sys.argv[3], sys.argv[4]
    if not is_valid_date(date):
        print("date must be in DD-MM-YY format, for example 12-10-26")
        return
    if not is_valid_time(sleep) or not is_valid_time(wake):
        print("time must be in HH:MM format (24-hours), for example 23:30")
        return
    try:
        quality = int(sys.argv[5])
    except ValueError:
        print("quality must be an integer")
        return
    if quality < 1 or quality > 100:
        print("quality must be in range from 1 to 100")
        return
    records.append({"date": date, "sleep": sleep, "wake": wake,
                    "quality": quality})
    storage.save(FILE, records)
    print("added")


def command_list(records):
    """list: show all records"""

    if len(records) == 0:
        print("no records available")
        return
    for number, r in enumerate(records, start=1):
        print_record(number, r)


def command_find(records):
    """find quality|duration MIN MAX"""

    if len(sys.argv) < 5:
        print("using: python cli.py find quality|duration MIN MAX")
        print("example: python cli.py find quality 50 100")
        return
    kind = sys.argv[2]
    try:
        low = float(sys.argv[3])
        high = float(sys.argv[4])
    except ValueError:
        print("MIN/MAX must be a number")
        return
    if kind == "quality":
        found = logic.find_by_quality(records, low, high)
    elif kind == "duration":
        found = logic.find_by_duration(records, low, high)
    else:
        print("you can find by quality or duration")
        return
    print_found(records, found)


def command_delete(records):
    """delete NUMBER"""

    if len(sys.argv) < 3:
        print("using: python cli.py delete NUMBER")
        return
    try:
        number = int(sys.argv[2])
    except ValueError:
        print("number must be an integer")
        return
    if logic.delete_record(records, number):
        storage.save(FILE, records)
        print("deleted")
    else:
        print("list with this number does not exist")


def command_report(records):
    """report: averages, shortest and longest night"""

    if len(records) == 0:
        print("no records available")
        return
    print(f"average sleep duration: {logic.average_sleep(records):.2f} h")
    print(f"average sleep quality: {logic.average_quality(records):.1f}")
    shortest = logic.shortest_night(records)
    longest = logic.longest_night(records)
    print("shortest night:")
    print_record(records.index(shortest) + 1, shortest)
    print("longest night:")
    print_record(records.index(longest) + 1, longest)


def main():
    if len(sys.argv) < 2:
        print("using: python cli.py add|list|find|delete|report ...")
        return
    command = sys.argv[1]
    records = storage.load(FILE)  # read data on every run 

    if command == "add":
        command_add(records)
    elif command == "list":
        command_list(records)
    elif command == "find":
        command_find(records)
    elif command == "delete":
        command_delete(records)
    elif command == "report":
        command_report(records)
    else:
        print("unknown command:", command)


if __name__ == "__main__":
    main()