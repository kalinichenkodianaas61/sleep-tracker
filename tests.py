import logic

# test data: three nights with known duration and quality
a = {"date": "01-01-26", "sleep": "23:00", "wake": "07:00", "quality": 80}  # 8 h
b = {"date": "02-01-26", "sleep": "01:00", "wake": "06:00", "quality": 40}  # 5 h
c = {"date": "03-01-26", "sleep": "22:00", "wake": "08:00", "quality": 60}  # 10 h
records = [a, b, c]

# testing sleep_hours func: one night crosses midnight, one does not
assert logic.sleep_hours(a) == 8.0
assert logic.sleep_hours(b) == 5.0

# testing find_by_quality func: normal range and range with no results
assert logic.find_by_quality(records, 50, 100) == [a, c]
assert logic.find_by_quality(records, 90, 100) == []

# testing find_by_duration func: narrow range and full range
assert logic.find_by_duration(records, 7, 9) == [a]
assert len(logic.find_by_duration(records, 0, 24)) == 3

# testing delete_record func: valid number and number that does not exist
test_list = list(records)  # copy, so the original list stays unchanged 
assert logic.delete_record(test_list, 2) is True
assert test_list == [a, c]
assert logic.delete_record(test_list, 5) is False
assert len(test_list) == 2

# testing average_sleep func: normal case and empty list
assert abs(logic.average_sleep(records) - 23 / 3) < 0.0001  # (8 + 5 + 10) / 3
assert logic.average_sleep([]) == 0

# testing average_quality func: normal case and empty list
assert logic.average_quality(records) == 60.0  # (80 + 40 + 60) / 3
assert logic.average_quality([]) == 0

# testing shortest_night func: normal case and empty list
assert logic.shortest_night(records) == b
assert logic.shortest_night([]) is None

# testing longest_night func: normal case and empty list
assert logic.longest_night(records) == c
assert logic.longest_night([]) is None

print("all tests passed")  