import typing
import config
import requests
import sys
import datetime
import enum
import argparse

TEXT_SEARCH: str = "tech"

# Cambridge, MA
LAT: float = 42.38
LON: float = -71.13

# measured in miles
RADIUS: float = 3

# minimum number of days before the start of event
START_DAY: int = 1
# maximum number of days before start of event
END_DAY: int = 8

# earliest time of day that the event can start
START_TIME: datetime.time = datetime.time(17, 00, 00)
# latest time of day that the evnet can start
END_TIME: datetime.time = datetime.time(20, 00, 00)

# total number of results to print
MAX_DISPLAYED: int = 3


class SortMethod(enum.Enum):
    UNSORTED = 0
    RSVP_COUNT = 1


# how the output will be sorted
SORT_METHOD: SortMethod = SortMethod.RSVP_COUNT


def sort_rsvp_count(event_list):
    event_list.sort(key=lambda x: x['yes_rsvp_count'], reverse=True)


def sort_unsorted():
    pass


sort_method_dict: typing.Dict = {
        SortMethod.UNSORTED: sort_unsorted,
        SortMethod.RSVP_COUNT: sort_rsvp_count,
        }


def format_request_string(search_term: str) -> str:
    dt_today = datetime.datetime.now()

    dt_start: datetime.datetime = dt_today + datetime.timedelta(days=START_DAY)
    dt_start = dt_start.replace(hour=START_TIME.hour, minute=START_TIME.minute)

    dt_end: datetime.datetime = dt_today + datetime.timedelta(days=END_DAY)
    dt_end = dt_end.replace(hour=END_TIME.hour, minute=END_TIME.minute)

    request_string: str = (
            f"https://api.meetup.com/find/upcoming_events?"
            f"key={config.meetup_key}&"
            f"lon={LON}&lat={LAT}&radius={RADIUS}&"
            f"end_date_rage={dt_start.strftime('%Y-%m-%dT%H:%M:%S')}&"
            f"start_date_range={dt_end.strftime('%Y-%m-%dT%H:%M:%S')}&"
            f"fields=plain_text_no_images_description"
            )
    if search_term is not None:
        request_string += f"&text={search_term}"
    return request_string


def format_header_string(city_dict: typing.Dict) -> str:
    header_string: str = (
            f"city: {city_dict['city']}, state: {city_dict['state']}, "
            f"country: {city_dict['country']}, zip: {city_dict['zip']}, "
            f"total members: {city_dict['member_count']}"
            )
    return header_string


def dict_access(event_dict: typing.Dict, dict_key: str, def_val: str) -> str:
    try:
        return event_dict[dict_key]
    except KeyError:
        return def_val


def format_event_string(event_dict: typing.Dict) -> str:
    event_desc_key: str = 'plain_text_no_images_description'
    event_desc: str = dict_access(event_dict, event_desc_key, "None provided")
    fee_text: str = dict_access(event_dict, 'fee', "No fee")
    rsvp_limit_text: str = dict_access(event_dict, 'rsvp_limit', "-1")
    format_string: str = (
            f"\033[93mGROUP:\033[0m {event_dict['group']['name']}\n"
            f"\033[93mEVENT:\033[0m {event_dict['name']}\n"
            f"\033[93mDATE:\033[0m {event_dict['local_date']}\n"
            f"\033[93mTIME:\033[0m {event_dict['local_time']}\n"
            f"\033[93mATTENDANCE COUNT:\033[0m"
            f" {event_dict['yes_rsvp_count']}/{rsvp_limit_text}\n"
            f"\033[93mFEE:\033[0m {fee_text}\n"
            f"\033[93mDESCRIPTION:\033[0m {event_desc}\n"
            )
    return format_string


def main() -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-search", type=str, default=TEXT_SEARCH,
                        help="search term to filter events")
    parser.add_argument("-all", action='store_true',
                        help="ignores any search term")
    parser.add_argument("-max", type=int, default=MAX_DISPLAYED,
                        help="maximum number of events to display")
    parser.add_argument("-sort", type=SortMethod, default=SORT_METHOD,
                        help="sort method used to display results")
    args: argparse.Namespace = parser.parse_args()

    search_string: typing.Optional = args.search
    if args.all:
        search_string = None
    req_string: str = format_request_string(search_string)
    response: typing.Any = requests.get(req_string)
    response_dict: typing.Dict = response.json()

    header_string: str = format_header_string(response_dict['city'])
    sys.stdout.write("%s\n\n" % (header_string))

    event_list: typing.List = response_dict['events']
    sort_method_dict[args.sort](event_list)

    for count, event in enumerate(event_list):
        if count == args.max:
            break
        event_string: str = format_event_string(event)
        separator: str = "*" * 80
        sys.stdout.write("%s\n%s\n" % (event_string, separator))
    return 0


if __name__ == '__main__':
    sys.exit(main())
