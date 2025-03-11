from datetime import datetime, timedelta

from langchain_core.tools import tool


def generate_reservations() -> dict[str, dict[str, str]]:
    dates = [
        (datetime.today() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6)
    ]
    start_time = datetime.strptime("18:00", "%H:%M")
    times = [
        (start_time + timedelta(minutes=30 * i)).strftime("%H:%M") for i in range(8)
    ]

    times_dict = {time: None for time in times}
    book = {date: times_dict for date in dates}

    return book


BOOK = generate_reservations()


@tool
def list_empty_slots(date: str) -> dict:
    """Return available time slots for reservations

    Args:
        date (str): date to return the slots. Format YYYY-mm-dd

    Returns:
        dict: available time slots
    """
    return BOOK[date]


@tool
def book_table(date: str, time: str, name: str, number_persons: int) -> None:
    """Book a table

    Args:
        date (str): date to book the table. Format YYYY-mm-dd
        time (str): time slot. Format HH:MM
        name (str): name of the person that are booking the table
        number_persons (int): number of persons on the reservation
    """
    BOOK[date][time] = {"name": name, "number_persons": number_persons}


@tool
def cancel_reservation(date: str, time: str) -> None:
    """Cancel a reservation by date and time

    Args:
        date (str): date to cancel the reservation. Format YYYY-mm-dd
        time (str): time slot to cancel. Format HH:MM

    Returns:
        bool: True if the reservation was cancel
    """
    BOOK[date][time] = None
    return True
