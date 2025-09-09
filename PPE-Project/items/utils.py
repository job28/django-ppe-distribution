from icalendar import Calendar, Event
from datetime import timedelta
from django.utils.timezone import now
from io import BytesIO

def generate_ics(order):
    cal = Calendar()
    event = Event()

    event.add('summary', f'PPE Pickup: {order.item.name}')
    event.add('dtstart', order.pickup_datetime)
    event.add('dtend', order.pickup_datetime + timedelta(minutes=30))
    event.add('dtstamp', now())
    event.add('location', order.pickup_hub.address)
    event.add('description', f"Pickup for PPE item: {order.item.name} x {order.quantity}")

    cal.add_component(event)

    ics_file = BytesIO()
    ics_file.write(cal.to_ical())
    ics_file.seek(0)
    return ics_file
