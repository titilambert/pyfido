import asyncio
import argparse
import collections
import json
import sys

from pyfido import FidoClient, REQUESTS_TIMEOUT


def _print_number(data):
    output = ("""
=====================================================

Fido data for number: {d[number]}

Fido Dollars
============

Fido Dollars : {d[fido_dollar]:.2f} $

Data plan
=========
Limit:        {d[data_limit]} Kb
Used:         {d[data_used]} Kb
Remaining:    {d[data_remaining]} Kb

Talk
====
Limit:        {d[talk_limit]} minutes
Used:         {d[talk_used]} minutes
Remaining:    {d[talk_remaining]} minutes

Texts
=====
Limit:        {d[text_limit]} messages
Used:         {d[text_used]} messages
Remaining:    {d[text_remaining]} messages

MMS
===
Limit:        {d[mms_limit]} messages
Used:         {d[mms_used]} messages
Remaining:    {d[mms_remaining]} messages

Internation texts
=================
Limit:        {d[text_int_limit]} messages
Used:         {d[text_int_used]} messages
Remaining:    {d[text_int_remaining]} messages
""")
    print(output.format(d=data))

    if 'other_talk_limit' in data:
        output = ("""
Other Talk (like international calls)
=====================================
Limit:        {d[other_talk_limit]} minutes
Used:         {d[other_talk_used]} minutes
Remaining:    {d[other_talk_remaining]} minutes
""")
        print(output.format(d=data))



def _format_output(selected_number, raw_data):
    """Format data to get a readable output"""
    tmp_data = {}
    data = collections.defaultdict(lambda: 0)
    balance = raw_data.pop('balance')
    for number in raw_data.keys():
        tmp_data = dict([(k, int(v) if v is not None else "No limit")
                         for k, v in raw_data[number].items()])
        tmp_data['number'] = number
        if selected_number is None or selected_number == number:
            data[number] = tmp_data

    output = ("""Account Balance
=======

Balance:      {:.2f} $
""")
    print(output.format(balance))
    for number_data in data.values():
        _print_number(number_data)


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username',
                        required=True, help='Fido username')
    parser.add_argument('-n', '--number', default=None,
                        required=False, help='Fido phone number')
    parser.add_argument('-p', '--password',
                        required=True, help='Password')
    parser.add_argument('-l', '--list', action='store_true',
                        default=False, help='List phone numbers')
    parser.add_argument('-j', '--json', action='store_true',
                        default=False, help='Json output')
    parser.add_argument('-t', '--timeout',
                        default=REQUESTS_TIMEOUT, help='Request timeout')
    args = parser.parse_args()
    client = FidoClient(args.username, args.password, args.timeout)
    loop = asyncio.get_event_loop()
    fut = asyncio.wait([client.fetch_data()])
    loop.run_until_complete(fut)
    if args.list:
        if not client.get_phone_numbers():
            return
        if args.json:
            print(json.dumps(client.get_phone_numbers()))
        else:
            print("Phone numbers: "
                  "{}".format(", ".join(client.get_phone_numbers())))
    else:
        if not client.get_data():
            return
        if args.json:
            print(json.dumps(client.get_data()))
        else:
            _format_output(args.number, client.get_data())


if __name__ == '__main__':
    sys.exit(main())
