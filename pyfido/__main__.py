import argparse
import collections
import json
import sys

from pyfido import FidoClient, REQUESTS_TIMEOUT


def _format_output(number, data):
    """Format data to get a readable output"""
    raw_data = dict([(k, int(v) if v is not None else "No limit")
                 for k, v in data.items()])
    raw_data['number'] = number
    data = collections.defaultdict(lambda: 0)
    data.update(raw_data)
    output = ("""Fido data for number: {d[number]}

Balance
=======
Balance:      {d[balance]:.2f} $
Fido Dollars: {d[balance]:.2f} $

Talk
====
Limit:        {d[talk_limit]} minutes
Used:         {d[talk_used]} minutes
Remaining:    {d[talk_remaining]} minutes

Other Talk (like international calls)
=====================================
Limit:        {d[other_talk_limit]} minutes
Used:         {d[other_talk_used]} minutes
Remaining:    {d[other_talk_remaining]} minutes

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

Data plan
=========
Limit:        {d[data_limit]} Kb
Used:         {d[data_used]} Kb
Remaining:    {d[data_remaining]} Kb
""")
    print(output.format(d=data))


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username',
                        required=True, help='Fido username')
    parser.add_argument('-n', '--number', default=None,
                        required=False, help='Fido phone number')
    parser.add_argument('-p', '--password',
                        required=True, help='Password')
    parser.add_argument('-j', '--json', action='store_true',
                        default=False, help='Json output')
    parser.add_argument('-t', '--timeout',
                        default=REQUESTS_TIMEOUT, help='Request timeout')
    args = parser.parse_args()
    client = FidoClient(args.username, args.password, args.number, args.timeout)
    client.fetch_data()
    if not client.get_data():
        return
    if args.json:
        print(json.dumps(client.get_data()))
    else:
        _format_output(args.number, client.get_data())


if __name__ == '__main__':
    sys.exit(main())
