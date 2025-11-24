from datetime import datetime, timedelta
from itertools import groupby
from prettytable import PrettyTable
from math import copysign

from sage_drop.client import Client


def format_minutes(time_in_minutes):
    abs_time = abs(time_in_minutes)
    return (f'{copysign(abs_time // 60, time_in_minutes):02.0f}'
            f':{abs_time % 60:02.0f}')


def balance(client: Client):
    balance_data = client.get_balance()
    data = balance_data[0]
    time_in_minutes = data['AmountInMinutes']
    # abs_time = abs(time_in_minutes)
    print(f'Balance: {format_minutes(time_in_minutes)}')


def come(client: Client, come_back: bool):
    date_from = client.get_current_time().date()
    date_to = date_from + timedelta(days=1)
    times = client.time_pairs(date_from, date_to)
    prefered_location = None
    if len(times) > 0:
        event = times[-1]
        if event.get('To') is None:
            print('You are already clocked in')
            return
        elif come_back:
            prefered_location = event['From']['PlaceOfWork']['Id']

    if prefered_location is None:
        locations = client.get_places_of_work()
        options = ', '.join([f'({index}) {item['Name']}'
                            for index, item in enumerate(locations)])
        index = input(f'Please choose location: {options}: ')
        try:
            location = locations[int(index)]
            prefered_location = location['Id']
        except Exception:
            print('Invalid location')
            return
    client.stamp_time('Come', prefered_location)


def go(client: Client, is_break: bool):
    date_from = client.get_current_time().date()
    date_to = date_from + timedelta(days=1)
    times = client.time_pairs(date_from, date_to)
    if len(times) == 0:
        print('You are not clocked in')
        return
    last_event = times[-1]
    if last_event.get('To') is not None:
        print('You are not clocked in')
        return
    location = last_event['From']['PlaceOfWork']
    if is_break:
        client.stamp_time('Go', location['Id'], 1)
    else:
        client.stamp_time('Go', location['Id'])


def map_event(item, now):
    event_from = item.get('From')
    event_to = item.get('To')
    event = {}

    if event_from:
        from_date = datetime.fromisoformat(event_from['Time'])
        location = event_from.get('PlaceOfWork')
        event['from_time'] = from_date.strftime('%H:%M')
    else:
        from_date = None
        location = None

    if event_to:
        to_date = datetime.fromisoformat(event_to['Time'])
        event['to_time'] = to_date.strftime('%H:%M')
        additinal_input = event_to.get('AdditionalInput')

        if additinal_input:
            event['info'] = additinal_input['Description']
    else:
        to_date = None

    event_date = from_date or to_date
    event['event_date'] = event_date.date()

    if to_date is None and event['event_date'] == now.date():
        print('hello')
        to_date = now
        event['info'] = 'in progress'

    if from_date and to_date:
        event['duration'] = (to_date - from_date).seconds // 60

    if location:
        event['location_name'] = location['Name']

    return event


def times(client: Client, date_from, date_to, range_days):
    now = client.get_current_time().replace(tzinfo=None)
    if date_from is None:
        date_from = now.date() - timedelta(
            days=range_days if range_days else now.weekday())
    if date_to is None:
        date_to = now.date() + timedelta(days=1)
    times = client.time_pairs(date_from, date_to)
    table = PrettyTable(['Date', 'Come', 'Go', 'Duration', 'Total', 'Location',
                         'Info'])
    events = list(map(lambda obj: map_event(obj, now), times))
    for date, group in groupby(events, lambda x: x['event_date']):
        date_events = list(group)
        date_time = 0
        for index, event in enumerate(date_events):
            duration = event.get('duration', 0)
            date_time += duration
            is_last_row = index == len(date_events) - 1
            table.add_row(
                    row=[
                        date if index == 0 else '',
                        event.get('from_time', ''),
                        event.get('to_time', ''),
                        format_minutes(duration) if duration else '',
                        format_minutes(date_time),
                        event.get('location_name', ''),
                        event.get('info', ''),
                        ],
                    divider=is_last_row)
    print(table)
