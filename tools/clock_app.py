# app.py
import asyncio
import contextlib
from datetime import datetime, date, time, timedelta
from typing import Dict, Optional, List, Literal, Union
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from zoneinfo import ZoneInfo

# Timezone for Düsseldorf, Germany (NRW)
TZ = ZoneInfo("Europe/Berlin")

app = FastAPI(title="Timers & Alarms API")

# Limits
MAX_CONCURRENT_TIMERS = 5

# ---- Models ----

class TimerCreate(BaseModel):
    minutes: int = 0
    seconds: int = 0
    message: Optional[str] = None

    @validator("minutes", "seconds")
    def non_negative(cls, v):
        if v < 0:
            raise ValueError("minutes/seconds must be >= 0")
        return v

    @property
    def total_seconds(self) -> float:
        return float(self.minutes * 60 + self.seconds)


class TimerInfo(BaseModel):
    id: str
    message: Optional[str] = None
    created_at: datetime
    duration_seconds: float
    remaining_seconds: float
    status: Literal["running", "cancelled", "fired"]


class AlarmCreate(BaseModel):
    # time of day, e.g. "14:30" or "14:30:00"
    time: str
    # optional: days to repeat on (names or numbers Monday=0 ... Sunday=6)
    days: Optional[List[Union[str, int]]] = None
    # optional: specific date "YYYY-MM-DD" for one-time if days not provided
    date: Optional[str] = None
    message: Optional[str] = None

    @validator("time")
    def time_format(cls, v):
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                datetime.strptime(v, fmt)
                return v
            except ValueError:
                continue
        raise ValueError('time must be "HH:MM" or "HH:MM:SS"')

    @validator("date")
    def date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError('date must be "YYYY-MM-DD"')
        return v


class AlarmInfo(BaseModel):
    id: str
    kind: Literal["one_time", "repeating"]
    time_of_day: str
    date: Optional[str] = None
    days_of_week: Optional[List[int]] = None  # 0=Mon .. 6=Sun
    next_fire_at: Optional[datetime] = None
    message: Optional[str] = None
    status: Literal["active", "cancelled"]


# ---- Registries ----

class TimerEntry:
    def __init__(self, id_: str, message: Optional[str], duration: float):
        self.id = id_
        self.message = message
        self.duration = duration
        self.created_at = datetime.now(tz=TZ)
        self.status: Literal["running", "cancelled", "fired"] = "running"
        self.task: Optional[asyncio.Task] = None

    def info(self) -> TimerInfo:
        remaining = 0.0
        if self.status == "running":
            elapsed = (datetime.now(tz=TZ) - self.created_at).total_seconds()
            remaining = max(0.0, self.duration - elapsed)
        return TimerInfo(
            id=self.id,
            message=self.message,
            created_at=self.created_at,
            duration_seconds=self.duration,
            remaining_seconds=remaining,
            status=self.status,
        )


class AlarmEntry:
    def __init__(
        self,
        id_: str,
        kind: Literal["one_time", "repeating"],
        time_of_day: time,
        message: Optional[str],
        days_of_week: Optional[List[int]] = None,
        specific_date: Optional[date] = None,
    ):
        self.id = id_
        self.kind = kind
        self.time_of_day = time_of_day
        self.message = message
        self.days_of_week = days_of_week
        self.specific_date = specific_date
        self.status: Literal["active", "cancelled"] = "active"
        self.next_fire_at: Optional[datetime] = None
        self.task: Optional[asyncio.Task] = None

    def info(self) -> AlarmInfo:
        return AlarmInfo(
            id=self.id,
            kind=self.kind,
            time_of_day=self.time_of_day.strftime("%H:%M:%S"),
            date=self.specific_date.isoformat() if self.specific_date else None,
            days_of_week=self.days_of_week,
            next_fire_at=self.next_fire_at,
            message=self.message,
            status=self.status,
        )


timers: Dict[str, TimerEntry] = {}
alarms: Dict[str, AlarmEntry] = {}

# ---- Helpers ----

WEEKDAY_NAME_TO_NUM = {
    "mon": 0, "monday": 0,
    "tue": 1, "tuesday": 1,
    "wed": 2, "wednesday": 2,
    "thu": 3, "thursday": 3,
    "fri": 4, "friday": 4,
    "sat": 5, "saturday": 5,
    "sun": 6, "sunday": 6,
}


def parse_time_of_day(s: str) -> time:
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            dt = datetime.strptime(s, fmt)
            return time(dt.hour, dt.minute, dt.second, tzinfo=TZ)
        except ValueError:
            continue
    raise ValueError("Invalid time format")


def normalize_days(days: Optional[List[Union[str, int]]]) -> Optional[List[int]]:
    if not days:
        return None
    result = []
    for d in days:
        if isinstance(d, int):
            if 0 <= d <= 6:
                result.append(d)
            else:
                raise ValueError("weekday int must be 0..6 (Mon..Sun)")
        else:
            key = d.strip().lower()
            if key not in WEEKDAY_NAME_TO_NUM:
                raise ValueError(f"invalid weekday name: {d}")
            result.append(WEEKDAY_NAME_TO_NUM[key])
    # unique, sorted by next occurrence order not necessary here
    return sorted(set(result))


def compute_next_datetime_for_time(
    now_local: datetime, tod: time, target_date: Optional[date] = None
) -> datetime:
    """Combine date and time-of-day in TZ and return next occurrence after now."""
    if target_date:
        candidate = datetime.combine(target_date, time(tod.hour, tod.minute, tod.second)).replace(tzinfo=TZ)
        return candidate
    # choose today or tomorrow based on time
    candidate = now_local.replace(hour=tod.hour, minute=tod.minute, second=tod.second, microsecond=0)
    if candidate <= now_local:
        candidate = candidate + timedelta(days=1)
    return candidate


def compute_next_for_days(now_local: datetime, tod: time, days_of_week: List[int]) -> datetime:
    """Find next datetime matching one of days_of_week at time-of-day."""
    for delta in range(0, 8):
        candidate = (now_local + timedelta(days=delta)).replace(
            hour=tod.hour, minute=tod.minute, second=tod.second, microsecond=0
        )
        if candidate.weekday() in days_of_week and candidate > now_local:
            return candidate
    # fallback: next week same first day
    delta_days = (7 - now_local.weekday() + days_of_week) % 7 or 7
    candidate = (now_local + timedelta(days=delta_days)).replace(
        hour=tod.hour, minute=tod.minute, second=tod.second, microsecond=0
    )
    return candidate


async def timer_worker(entry: TimerEntry):
    try:
        await asyncio.sleep(entry.duration)
        entry.status = "fired"
    except asyncio.CancelledError:
        entry.status = "cancelled"
        raise
    finally:
        # Remove fired or cancelled timers to free capacity
        timers.pop(entry.id, None)


async def one_time_alarm_worker(entry: AlarmEntry):
    try:
        now_local = datetime.now(tz=TZ)
        target = compute_next_datetime_for_time(now_local, entry.time_of_day, entry.specific_date)
        if target <= now_local:
            raise HTTPException(status_code=400, detail="alarm time is in the past")
        entry.next_fire_at = target
        delay = (target - now_local).total_seconds()
        await asyncio.sleep(delay)
        # ACTION: place your notification/side-effect here
        print(f"[ALARM] {entry.id} fired at {datetime.now(tz=TZ).isoformat()} message={entry.message}")
    except asyncio.CancelledError:
        entry.status = "cancelled"
        raise
    finally:
        # Remove one-time alarm after completion or cancellation
        alarms.pop(entry.id, None)


async def repeating_alarm_worker(entry: AlarmEntry):
    try:
        while True:
            now_local = datetime.now(tz=TZ)
            next_dt = compute_next_for_days(now_local, entry.time_of_day, entry.days_of_week or [])
            entry.next_fire_at = next_dt
            delay = max(0.0, (next_dt - now_local).total_seconds())
            await asyncio.sleep(delay)
            # ACTION: place your notification/side-effect here
            print(f"[ALARM:REPEAT] {entry.id} fired at {datetime.now(tz=TZ).isoformat()} message={entry.message}")
            # loop to compute next fire time
    except asyncio.CancelledError:
        entry.status = "cancelled"
        raise
    finally:
        # keep entry in dict until cancelled; remove on exit
        if entry.status == "cancelled":
            alarms.pop(entry.id, None)


# ---- API ----

@app.get("/health")
async def health():
    return {"status": "ok", "now": datetime.now(tz=TZ).isoformat()}

# Timers
@app.post("/timers", response_model=TimerInfo)
async def create_timer(payload: TimerCreate):
    # enforce capacity unless updating existing by id (creation has no id -> capacity applies)
    active = sum(1 for t in timers.values() if t.status == "running")
    if active >= MAX_CONCURRENT_TIMERS:
        raise HTTPException(status_code=409, detail="max 5 concurrent timers reached")
    total = payload.total_seconds
    if total <= 0:
        raise HTTPException(status_code=400, detail="timer duration must be > 0 seconds")
    tid = str(uuid4())
    entry = TimerEntry(tid, payload.message, total)
    task = asyncio.create_task(timer_worker(entry))
    entry.task = task
    timers[tid] = entry
    return entry.info()

@app.get("/timers", response_model=List[TimerInfo])
async def list_timers():
    return [t.info() for t in timers.values()]

@app.delete("/timers/{timer_id}", response_model=TimerInfo)
async def cancel_timer(timer_id: str):
    entry = timers.get(timer_id)
    if not entry:
        raise HTTPException(status_code=404, detail="timer not found")
    if entry.task and not entry.task.done():
        entry.task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await entry.task
    # entry removed in worker; return last known state
    return entry.info()

# Alarms
@app.post("/alarms", response_model=AlarmInfo)
async def create_alarm(payload: AlarmCreate):
    tod = parse_time_of_day(payload.time)
    days = normalize_days(payload.days)
    # Determine kind: repeating if days given, else one-time on provided date or today
    if days:
        aid = str(uuid4())
        entry = AlarmEntry(
            id_=aid,
            kind="repeating",
            time_of_day=tod,
            message=payload.message,
            days_of_week=days,
        )
        task = asyncio.create_task(repeating_alarm_worker(entry))
        entry.task = task
        alarms[aid] = entry
        return entry.info()
    else:
        # one-time: use date or today if not provided (but must be in the future)
        if payload.date:
            d = datetime.strptime(payload.date, "%Y-%m-%d").date()
        else:
            d = date.today()
        aid = str(uuid4())
        entry = AlarmEntry(
            id_=aid,
            kind="one_time",
            time_of_day=tod,
            message=payload.message,
            specific_date=d,
        )
        task = asyncio.create_task(one_time_alarm_worker(entry))
        entry.task = task
        alarms[aid] = entry
        return entry.info()

@app.get("/alarms", response_model=List[AlarmInfo])
async def list_alarms():
    return [a.info() for a in alarms.values()]

@app.delete("/alarms/{alarm_id}", response_model=AlarmInfo)
async def cancel_alarm(alarm_id: str):
    entry = alarms.get(alarm_id)
    if not entry:
        raise HTTPException(status_code=404, detail="alarm not found")
    if entry.task and not entry.task.done():
        entry.task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await entry.task
    return entry.info()

# Optional: update endpoints by cancel+recreate with same id could be added similarly.

@app.on_event("shutdown")
async def shutdown():
    # graceful cancellation
    for entry in list(timers.values()):
        if entry.task and not entry.task.done():
            entry.task.cancel()
    for entry in list(alarms.values()):
        if entry.task and not entry.task.done():
            entry.task.cancel()
