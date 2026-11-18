import sqlite3

import pytest

import storage
from models import SleepRecord


@pytest.fixture
def db(tmp_path, monkeypatch):
    # empty database for every test 
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.db"))
    storage.init()


def test_add_and_load_returns_objects(db):
    new_id = storage.add(SleepRecord("01-10-26", "23:00", "07:00", 80, "кава"))
    records = storage.load()
    assert len(records) == 1
    assert isinstance(records[0], SleepRecord)
    assert records[0].id == new_id
    assert records[0].factor == "кава"


def test_same_factor_is_stored_once(db):
    storage.add(SleepRecord("01-10-26", "23:00", "07:00", 80, "кава"))
    storage.add(SleepRecord("02-10-26", "23:00", "07:00", 70, "кава"))
    with storage.connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM factors WHERE name = 'кава'").fetchone()[0]
    assert count == 1


def test_foreign_key_is_enforced(db):
    # record with a factor that does not exist must be rejected
    with pytest.raises(sqlite3.IntegrityError):
        with storage.connect() as conn:
            conn.execute("INSERT INTO records (date, sleep, wake, quality, factor_id) "
                         "VALUES ('01-10-26', '23:00', '07:00', 80, 999)")


def test_audit_log_gets_add_and_delete(db):
    new_id = storage.add(SleepRecord("01-10-26", "23:00", "07:00", 80))
    assert storage.delete(new_id) is True
    log = storage.load_log()
    assert [row["action"] for row in log] == ["delete", "add"]  # newest first 
    assert log[0]["item_id"] == new_id
    assert log[0]["ts"]


def test_delete_missing_is_not_logged(db):
    assert storage.delete(999) is False
    assert storage.load_log() == []


def test_factor_report_uses_join(db):
    storage.add(SleepRecord("01-10-26", "23:00", "07:00", 40, "кава"))
    storage.add(SleepRecord("02-10-26", "23:00", "07:00", 60, "кава"))
    storage.add(SleepRecord("03-10-26", "23:00", "07:00", 90, "спорт"))
    assert storage.factor_report() == [
        {"factor": "спорт", "nights": 1, "avg_quality": 90.0},
        {"factor": "кава", "nights": 2, "avg_quality": 50.0},
    ]
