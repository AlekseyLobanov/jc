"""jc - JSON Convert `INI` file parser

Parses standard `INI` files.

- Delimiter can be `=` or `:`. Missing values are supported.
- Comment prefix can be `#` or `;`. Comments must be on their own line.
- If duplicate keys are found, only the last value will be used.

> Note: If there is no top-level section identifier, then this parser will
> add a key named `_top_level_section_` with the top-level key/values
> included.

> Note: The section identifier `[DEFAULT]` is special and provides default
> values for the section keys that follow. To disable this behavior you must
> rename the `[DEFAULT]` section identifier to something else before
> parsing.

> Note: Values starting and ending with double or single quotation marks
> will have the marks removed. If you would like to keep the quotation
> marks, use the `-r` command-line argument or the `raw=True` argument in
> `parse()`.

Usage (cli):

    $ cat foo.ini | jc --ini

Usage (module):

    import jc
    result = jc.parse('ini', ini_file_output)

Schema:

INI document converted to a dictionary - see the python configparser
standard library documentation for more details.

    {
      "key1":       string,
      "key2":       string
    }

Examples:

    $ cat example.ini
    [DEFAULT]
    ServerAliveInterval = 45
    Compression = yes
    CompressionLevel = 9
    ForwardX11 = yes

    [bitbucket.org]
    User = hg

    [topsecret.server.com]
    Port = 50022
    ForwardX11 = no

    $ cat example.ini | jc --ini -p
    {
      "bitbucket.org": {
        "ServerAliveInterval": "45",
        "Compression": "yes",
        "CompressionLevel": "9",
        "ForwardX11": "yes",
        "User": "hg"
      },
      "topsecret.server.com": {
        "ServerAliveInterval": "45",
        "Compression": "yes",
        "CompressionLevel": "9",
        "ForwardX11": "no",
        "Port": "50022"
      }
    }
"""
import jc.utils
import configparser
import uuid


class info():
    """Provides parser metadata (version, author, etc.)"""
    version = '2.0'
    description = 'INI file parser'
    author = 'Kelly Brazil'
    author_email = 'kellyjonbrazil@gmail.com'
    details = 'Using configparser from the python standard library'
    compatible = ['linux', 'darwin', 'cygwin', 'win32', 'aix', 'freebsd']
    tags = ['standard', 'file', 'string']


__version__ = info.version


def _remove_quotes(value):
    if value is not None and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]

    elif value is not None and value.startswith("'") and value.endswith("'"):
        value = value[1:-1]

    elif value is None:
        value = ''

    return value


def _process(proc_data):
    """
    Final processing to conform to the schema.

    Parameters:

        proc_data:   (Dictionary) raw structured data to process

    Returns:

        Dictionary representing the INI file.
    """
    # remove quotation marks from beginning and end of values
    for k, v in proc_data.items():
        if isinstance(v, dict):
            for key, value in v.items():
                v[key] = _remove_quotes(value)
            continue

        proc_data[k] = _remove_quotes(v)

    return proc_data


def parse(data, raw=False, quiet=False):
    """
    Main text parsing function

    Parameters:

        data:        (string)  text data to parse
        raw:         (boolean) unprocessed output if True
        quiet:       (boolean) suppress warning messages if True

    Returns:

        Dictionary representing the INI file.
    """
    jc.utils.compatibility(__name__, info.compatible, quiet)
    jc.utils.input_type_check(data)

    raw_output = {}

    if jc.utils.has_data(data):

        ini_parser = configparser.ConfigParser(
            allow_no_value=True,
            interpolation=None,
            strict=False
        )

        # don't convert keys to lower-case:
        ini_parser.optionxform = lambda option: option

        try:
            ini_parser.read_string(data)
            raw_output = {s: dict(ini_parser.items(s)) for s in ini_parser.sections()}

        except configparser.MissingSectionHeaderError:
            # find a top-level section name that will not collide with any existing ones
            while True:
                my_uuid = str(uuid.uuid4())
                if my_uuid not in data:
                    break

            data = f'[{my_uuid}]\n' + data
            ini_parser.read_string(data)
            temp_dict = {s: dict(ini_parser.items(s)) for s in ini_parser.sections()}

            # move items under fake top-level sections to the root
            raw_output = temp_dict.pop(my_uuid)

            # get the rest of the sections
            raw_output.update(temp_dict)

    return raw_output if raw else _process(raw_output)

