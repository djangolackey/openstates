import datetime

metadata = dict(
    name='Arkansas',
    abbreviation='ar',
    legislature_name='Arkansas General Assembly',
    upper_chamber_name='Senate',
    lower_chamber_name='House of Representatives',
    upper_chamber_title='Senator',
    lower_chamber_title='Representative',
    upper_chamber_term=4,
    lower_chamber_term=2,
    terms=[
        {'name': '2011-2012',
         'start_year': 2011,
         'end_year': 2012,
         'sessions': ['2011R']}
        ],
    session_details={
        '2011R': {'start_date': datetime.date(2011, 1, 10),
                 'end_date': None,
                 'type': 'primary'}
        },
    )
