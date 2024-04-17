from datetime import datetime, timedelta
from prettytable import PrettyTable

from sage_drop.client import Client


def balance(client: Client):
    balance_data = client.get_balance()
    data = balance_data[0]
    time_in_minutes = data['AmountInMinutes']
    print('Balance: '
          f'{time_in_minutes // 60:02.0f}:{time_in_minutes % 60:02.0f}')


def come(client: Client):
    date_from = client.get_current_time().date()
    date_to = date_from + timedelta(days=1)
    times = client.time_pairs(date_from, date_to)
    if len(times) > 0:
        event = times[-1]
        if event.get('To') is None:
            print('You are already clocked in')
            return
    locations = client.get_places_of_work()
    options = ', '.join([f'({index}) {item['Name']}'
                        for index, item in enumerate(locations)])
    index = input(f'Please choose location: {options}: ')
    try:
        location = locations[int(index)]
    except Exception:
        print('Invalid location')
        return
    client.stamp_time('Come', location['Id'])


def go(client: Client, is_break: bool):
    date_from = client.get_current_time().date()
    date_to = date_from + timedelta(days=1)
    times = client.time_pairs(date_from, date_to)
    if len(times) == 0:
        print('You are not clocked in')
        return
    last_event = times[-1]
    if last_event.get('Go') is not None:
        print('You are not clocked in')
        return
    location = last_event['PlaceOfWork']
    if is_break:
        client.stamp_time('Go', location['Id'], 1)
    else:
        client.stamp_time('Go', location['Id'])


def times(client: Client, date_from, date_to):
    if date_from is None:
        date_from = client.get_current_time().date()
    if date_to is None:
        date_to = client.get_current_time().date() + timedelta(days=1)
    times = client.time_pairs(date_from, date_to)
    table = PrettyTable(['Date', 'Come', 'Go', 'Location', 'Info'])
    for item in times:
        row = []
        event_from = item['From']
        event_date = datetime.fromisoformat(event_from['Time'])
        row.append(event_date.strftime('%d %b'))
        row.append(event_date.strftime('%H:%M'))
        event_to = item.get('To')
        go_time = ''
        info = ''
        if event_to:
            go_time = datetime.fromisoformat(
                event_to['Time']).strftime('%H:%M')
            additinal_input = event_to.get('AdditionalInput')
            if additinal_input:
                info = additinal_input['Description']
        location = event_from.get('PlaceOfWork')
        location_name = ''
        if location:
            location_name = location['Name']
        row.append(go_time)
        row.append(location_name)
        row.append(info)
        table.add_row(row)
    print(table)
