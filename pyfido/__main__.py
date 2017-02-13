import argparse
import json
import sys

from pyfido import FidoClient, REQUESTS_TIMEOUT


def _format_output(number, data):
    """Format data to get a readable output"""
    data = dict([(k, int(v) if v is not None else "No limit")
                 for k, v in data.items()])
    data['number'] = number
    output = ("""Fido data for number: {d[number]}

Balance
=======
Balance:      {d[balance]:.2f} $
Fido Dollars: {d[balance]:.2f} $

Talk
====
Limit:        {d[talk_limit]} minutes
Used:         {d[talk_remaining]} minutes
Remaining:    {d[talk_used]} minutes

Texts
=====
Limit:        {d[text_limit]} messages
Used:         {d[text_remaining]} messages
Remaining:    {d[text_used]} messages

MMS
===
Limit:        {d[mms_limit]} messages
Used:         {d[mms_remaining]} messages
Remaining:    {d[mms_used]} messages

Internation texts
=================
Limit:        {d[text_int_limit]} messages
Used:         {d[text_int_remaining]} messages
Remaining:    {d[text_int_used]} messages

Data plan
=========
Limit:        {d[data_limit]} Kb
Used:         {d[data_remaining]} Kb
Remaining:    {d[data_used]} Kb
""")
    print(output.format(d=data))


def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number',
                        required=True, help='Fido phone number')
    parser.add_argument('-p', '--password',
                        required=True, help='Password')
    parser.add_argument('-j', '--json', action='store_true',
                        default=False, help='Json output')
    parser.add_argument('-t', '--timeout',
                        default=REQUESTS_TIMEOUT, help='Request timeout')
    args = parser.parse_args()
    client = FidoClient(args.number, args.password, args.timeout)
    client.fetch_data()
    if not client.get_data():
        return
    if args.json:
        print(json.dumps(client.get_data()))
    else:
        _format_output(args.number, client.get_data())


if __name__ == '__main__':
    sys.exit(main())
