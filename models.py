DEFAULT_FACTOR = "без фактора"


class SleepRecord:
    """One night of sleep."""

    def __init__(self, date, sleep, wake, quality, factor=DEFAULT_FACTOR, record_id=None):
        self.id = record_id
        self.date = date
        self.sleep = sleep
        self.wake = wake
        # here, and only here, text becomes a number 
        self.quality = int(quality)
        if not 1 <= self.quality <= 100:
            raise ValueError("quality must be in range 1-100")
        # day factor: coffee, sport, stress... 
        if not isinstance(factor, str) or not 1 <= len(factor.strip()) <= 50:
            raise ValueError("factor must be a text of 1-50 characters")
        self.factor = factor.strip()

    def to_dict(self):
        """For jsonify and API answers."""
        return {"id": self.id, "date": self.date, "sleep": self.sleep,
                "wake": self.wake, "quality": self.quality, "factor": self.factor}

    @staticmethod
    def from_row(row):
        """From sqlite3.Row to object (З рядка sqlite3.Row в об'єкт)."""
        return SleepRecord(row["date"], row["sleep"], row["wake"],
                           row["quality"], row["factor"], row["id"])

    def is_good(self, limit):
        """True if quality is at least limit."""
        return self.quality >= limit
