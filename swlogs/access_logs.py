#!/usr/bin/env python

# standard library imports
import gzip
import pathlib
import re
import socket
import warnings


# 3rd party library imports
import pandas as pd

# local imports
from .ua_regex import UA_REGEX_REPLACE
from .common import CommonObj

pd.options.display.float_format = '{:,.1f}'.format


def apply_regexes(s):

    first_match = next(
        filter(lambda x: x.search(s), UA_REGEX_REPLACE.keys()),
        None
    )
    return UA_REGEX_REPLACE.get(first_match, s)


class AccessLog(CommonObj):

    """
    Attributes
    ----------
    inputfile: path
        Process this apache logfile.
    useragent : str or None
        If not None, restrict log entries to this user agent
    views : bool
        If True, compute views instead of hits.
    df_ip32 : pandas.DataFrame
        The top ip addresses in the current log
    """

    def __init__(self, infile=None, useragent=None, views=False):
        super().__init__()

        self.infile = pathlib.Path(infile)
        self.useragent = useragent
        self.views = views

        self.setup_logfile_regex()
        self.setup_ua_regex()

    def __enter__(self):

        if self.infile is None:
            self.infile = pathlib.Path('/var/log/httpd/big-access-log').open()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def setup_ua_regex(self):
        """
        """
        regex_strs = [
            (
                r"""KHTML,
                \s
                like Gecko;
                \s
                compatible;
                \s
                bingbot/2.0;
                \s
                \+http://www.bing.com/bingbot.htm"""
            )
        ]
        regexes = [re.compile(s, re.X) for s in regex_strs]
        replace_strs = [
            'bingbot/2.0',
        ]
        self.ua_regex = {k: v for k, v in zip(regexes, replace_strs)}

    def setup_logfile_regex(self):

        self.regex = re.compile(
            r"""
            ^
            (?P<ip>((\d{1,3}.){3}\d{1,3})
                   |
                   (([\w-]+[.]){3,4}([\w-]+))
            )
            \s*?
            (?P<country>([A-Z]{2}|-))
            \s*?
            (-|[a-z0-9]{7})
            \s*?
            [\[]
            (?P<timestamp>\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}\s-\d{4})
            [\]]
            \s*?
            "(
                -
                |
                \\n
                |
                0
                |
                (?P<method>(DELETE|GET|HEAD|OPTIONS|PATCH|POST|PROPFIND|PUT|SSTP_DUPLEX_POST))
                \s
                (?P<url>[^\?;]+)
                ((\?|;)(?P<query_string>[^\s]+)?)?
                \s
                HTTP/[12].[01]
            )"
            \s
            (?P<status>\d+)
            \s
            (?P<bytes>\d+|-)
            \s+?
            "(?P<referer>.*?(?="\s))"
            \s
            "(?P<user_agent>.*?(?="\s))"
            (
              \s+
              "(?P<content_type>[^"]+)"
              \s
              (?P<remote_port>[0-9]+)
            )?
            """,
            re.X
        )

    def run(self):

        self.parse_input_file()

        self.df['ua'] = self.df['ua'].apply(apply_regexes)

    def parse_input_file(self):

        if str(self.infile).endswith('gz'):
            fp = gzip.open(self.infile, mode='rt')
        else:
            fp = self.infile.open()

        data = []
        for idx, line in enumerate(fp):

            if (m := self.regex.match(line)) is None:
                msg = f"Did not match line {idx} {line}"
                warnings.warn(msg)
                continue
                # raise RuntimeError(msg)

            item = (
                m.group('ip'),
                m.group('timestamp'),
                m.group('status'),
                m.group('user_agent'),
                m.group('url'),
                m.group('bytes'),
            )
            data.append(item)

        columns = ["ip", 'timestamp', "status", "ua", "url", 'bytes']
        df = pd.DataFrame(data, columns=columns)

        df['timestamp'] = pd.to_datetime(
            df['timestamp'], format='%d/%b/%Y:%H:%M:%S %z'
        )
        df['status'] = df['status'].astype(int)

        def convert_bytes(x):
            try:
                return int(x)
            except ValueError:
                return 0

        df['bytes'] = df['bytes'].apply(convert_bytes)

        def fcn(x):
            if re.search(r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}', x):
                return x
            else:
                try:
                    return socket.gethostbyname(x)
                except:  # noqa : E501
                    return x

        df.loc[:, 'ip'] = df['ip'].apply(fcn)

        self.df = df
