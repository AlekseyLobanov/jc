"""jc - JSON CLI output utility uptime Parser

Usage:
    specify --uptime as the first argument if the piped input is coming from uptime

Example:

$ uptime | jc --uptime -p
{
  "time": "16:52",
  "uptime": "3 days, 4:49",
  "users": "5",
  "load_1m": "1.85",
  "load_5m": "1.90",
  "load_15m": "1.91"
}
"""


def parse(data):
    output = {}

    cleandata = data.splitlines()

    if cleandata:
        parsed_line = cleandata[0].split()

        output['time'] = parsed_line[0]
        output['uptime'] = ' '.join(parsed_line[2:5]).rstrip(',')
        output['users'] = parsed_line[5]
        output['load_1m'] = parsed_line[9]
        output['load_5m'] = parsed_line[10]
        output['load_15m'] = parsed_line[11]

    return output
