import pytest

import logic
from models import SleepRecord

# test data: three nights with known duration and quality
a = SleepRecord("01-01-26", "23:00", "07:00", 80)  # 8 h
b = SleepRecord("02-01-26", "01:00", "06:00", 40)  # 5 h
c = SleepRecord("03-01-26", "22:00", "08:00", 60)  # 10 h
records = [a, b, c]


def test_sleep_hours_crosses_midnight_and_not():
    assert logic.sleep_hours(a) == 8.0  # crosses midnight 
    assert logic.sleep_hours(b) == 5.0  # does not cross 


def test_find_by_quality_normal_and_empty_result():
    assert logic.find_by_quality(records, 50, 100) == [a, c]
    assert logic.find_by_quality(records, 90, 100) == []


def test_find_by_duration_narrow_and_full_range():
    assert logic.find_by_duration(records, 7, 9) == [a]
    assert len(logic.find_by_duration(records, 0, 24)) == 3


def test_delete_record_valid_and_missing_number():
    test_list = list(records)  # copy, original stays unchanged 
    assert logic.delete_record(test_list, 2) is True
    assert test_list == [a, c]
    assert logic.delete_record(test_list, 5) is False
    assert len(test_list) == 2


def test_average_sleep_normal_and_empty():
    assert logic.average_sleep(records) == pytest.approx(23 / 3)  # (8 + 5 + 10) / 3
    assert logic.average_sleep([]) == 0


def test_average_quality_normal_and_empty():
    assert logic.average_quality(records) == 60.0  # (80 + 40 + 60) / 3
    assert logic.average_quality([]) == 0


def test_shortest_and_longest_night():
    assert logic.shortest_night(records) == b
    assert logic.longest_night(records) == c
    assert logic.shortest_night([]) is None
    assert logic.longest_night([]) is None


def test_record_converts_quality_to_number():
    r = SleepRecord("01-01-26", "23:00", "07:00", "75")
    assert r.quality == 75
    assert isinstance(r.quality, int)


def test_record_rejects_bad_quality():
    with pytest.raises(ValueError):
        SleepRecord("01-01-26", "23:00", "07:00", "abc")
    with pytest.raises(ValueError):
        SleepRecord("01-01-26", "23:00", "07:00", 101)


def test_record_rejects_empty_factor():
    with pytest.raises(ValueError):
        SleepRecord("01-01-26", "23:00", "07:00", 80, factor="   ")


def test_record_to_dict_has_all_fields():
    r = SleepRecord("01-01-26", "23:00", "07:00", 80, "кава", 7)
    assert r.to_dict() == {"id": 7, "date": "01-01-26", "sleep": "23:00",
                           "wake": "07:00", "quality": 80, "factor": "кава"}
