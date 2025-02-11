def convert_dict(raw: tuple):
    col_of_type_in_event = ['event_id', 'event_name', 'event_type', 'event_date', 'event_department']
    return [dict(zip(col_of_type_in_event, row)) for row in raw]
