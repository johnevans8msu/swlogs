#!/usr/bin/env python

# standard library imports
import argparse
import datetime as dt
import ipaddress
import pathlib
import re
import socket
import sys
import warnings


# 3rd party library imports
import pandas as pd

# local imports
from .ua_regex import UA_REGEX_REPLACE

pd.options.display.float_format = '{:,.1f}'.format


def apply_regexes(s):

    first_match = next(
        filter(lambda x: x.search(s), UA_REGEX_REPLACE.keys()),
        None
    )
    return UA_REGEX_REPLACE.get(first_match, s)


class AccessLog(object):

    """
    Attributes
    ----------
    inputfile: path
        Process this apache logfile.
    useragent : str or None
        If not None, restrict log entries to this user agent
    views : bool
        If True, compute views instead of hits.
    """

    def __init__(self, infile=None, useragent=None, views=False):

        self.infile = infile
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

        self.regex = re.compile(r"""
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

        # exclude cases of 153.90.170.2 / ua has "node.js".  this is the
        # scholarworks frontend making follow-up requests.  unfortunately
        # the referer doesn't reflect that
        # self.df = self.df.query('ip != "153.90.6.244" and "node.js" not in ua')

        if self.useragent is not None:
            self.df = self.df.query('ua == @self.useragent')

        self.summarize_user_agents()
        self.process_top_20_network_addresses_netmask_16()
        self.process_top_20_network_addresses_netmask_24()
        self.process_top_20_network_addresses_netmask_32()

    def summarize_user_agents(self):

        if self.views:

            # drop all log records that have the host IP address as the source
            # IP.  
            breakpoint()
            host_ip = socket.gethostbyname(socket.gethostname())
            df20 = (
                self.df.query('ip != @host_ip')
                       .groupby('ua')
                       .size()
                       .sort_values(ascending=False)
                       .head(n=20)
                       .to_frame()
            )

            # ok, so that gives us views
            df20.columns = ['views']

            # get the ratio of hits to views for those top 20 user agents
            df20['hits-views-ratio'] = (
                self.df.groupby('ua')
                       .size()
                       .sort_values()
                       .to_frame()
                       .reindex(df20.index)
            )
            df20['hits-views-ratio'] /= df20['views']

        else:

            # just compute hits by user-agent
            df20 = (
                self.df.groupby('ua')
                       .size()
                       .sort_values()
                       .tail(n=20)
                       .to_frame()
            )
            df20.columns = ['hits']

        top_useragents = df20.index.to_list()

        # what is the error percentage for each user agent?
        for ua in df20.index:
            b = self.df.query('ua == @ua')
            df20.loc[ua, 'error_pct'] = len(b.query('status >= 400')) / len(b) * 100

        # how many 429s for each user agent?
        df20['429'] = 0
        for ua in df20.index:
            b = self.df.query('ua == @ua and status == 429')
            df20.loc[ua, '429'] = len(b)

        # which of those user agents actually consulted /robots.txt?
        df_robots = (
            self.df.loc[(~self.df['url'].isnull()) & (self.df['url'].str.startswith("/robots.txt")), :]
                   .query('ua == @df20.index.to_list()')
                   .groupby('ua')
                   .size()
                   .to_frame()
        )
        df_robots.columns = ['robots']
        df_robots['robots'] = True
        df20 = df20.merge(df_robots, how='left', left_index=True, right_index=True)
        df20.loc[df20['robots'].isnull(), 'robots'] = False

        # which of those user agents accessed /xmlui?
        df_xmlui = (
            self.df.loc[(~self.df['url'].isnull()) & (self.df['url'].str.startswith("/xmlui")), :]
                   .query('ua == @df20.index.to_list()')
                   .groupby('ua')
                   .size()
                   .to_frame()
        )
        df_xmlui.columns = ['xmlui']
        df_xmlui['xmlui'] = True
        df20 = df20.merge(df_xmlui, how='left', left_index=True, right_index=True)
        df20.loc[df20['xmlui'].isnull(), 'xmlui'] = False

        # which of those user agents accessed sitemaps?
        df_sitemaps = (
            self.df.query('~url.isnull()')
                   .query('url.str.contains("/sitemap")')
                   .groupby('ua')
                   .size()
                   .to_frame()
        )
        df_sitemaps.columns = ['sitemaps']
        df_sitemaps['sitemaps'] = True
        df20 = df20.merge(df_sitemaps, how='left', left_index=True, right_index=True)
        df20.loc[df20['sitemaps'].isnull(), 'sitemaps'] = False

        df20 = df20.sort_values(by='hits', ascending=False)
        self.top20 = df20

    def process_top_20_network_addresses_netmask_32(self):

        # Get the top 20 network addresses / 16
        df20 = self.df.groupby('ip').size().sort_values().tail(n=20).to_frame()
        df20.columns = ['hits']
        df20['error_pct'] = 0.0

        s_errors = self.df.query('status > 399').groupby('ip').size()

        for ip in df20.index:
            try:
                df20.loc[ip, 'error_pct'] = s_errors[ip] / df20.loc[ip, 'hits'] * 100
            except KeyError:
                continue

    def process_top_20_network_addresses_netmask_16(self):

        # Get the top 20 network addresses / 16
        self.df['ip16'] = self.df['ip'].apply(lambda x: '.'.join(x.split('.')[:2]))
        df20 = self.df.groupby('ip16').size().sort_values().tail(n=20).to_frame()
        df20.columns = ['hits']
        df20['error_pct'] = 0.0

        s_errors = self.df.query('status > 399').groupby('ip16').size()

        for ip in df20.index:
            try:
                df20.loc[ip, 'error_pct'] = s_errors[ip] / df20.loc[ip, 'hits'] * 100
            except KeyError:
                continue

    def process_top_20_network_addresses_netmask_24(self):

        # Get the top 20 network addresses / 24
        self.df['ip24'] = self.df['ip'].apply(lambda x: '.'.join(x.split('.')[:3]))
        df20 = self.df.groupby('ip24').size().sort_values().tail(n=20).to_frame()
        df20.columns = ['hits']

        df20['error_pct'] = 0.0

        s_errors = self.df.query('status > 399').groupby('ip24').size()
        for ip in df20.index:
            try:
                df20.loc[ip, 'error_pct'] = s_errors[ip] / df20.loc[ip, 'hits'] * 100
            except KeyError:
                continue


    def get_top_ten(self):
        """
        Log the top ten user agents.
        """

        # Get the 10 ten user agents for the day, match against user agents
        # that we know about.
        sql = """
            select
                bots.id,
                bots.shortname as shortname,
                daily.ua as longname,
                count(*) as n
            from daily left join bots on daily.ua = bots.useragent
            group by id, shortname, longname
            order by n desc
            limit 10
        """
        df = pd.read_sql(sql, self.engine)

        # find any user agents that we don't know about, need to make up names
        # for them.
        unknowns = df.loc[df.shortname.isnull(), :]
        for idx, row in unknowns.iterrows():
            shortname = self.process_ua_to_shortname(idx, row['longname'])
            df.loc[idx, 'shortname'] = shortname
            unknowns.loc[idx, 'shortname'] = shortname

        return df

    def process_ua_to_shortname(self, idx, longname):
        """
        Come up with a short name by which to refer to this user agent quickly.
        """
        # is it easy, i.e. is there a part of the user agent longname that has
        # something like 
        #
        # (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)
        # 
        # in which case just use 'bingbot/2.0'
        m = re.search(r'(compatible; (?P<shortname>[\w./]+); .*?)', longname)
        if m is not None:
            shortname = self.process_shortname_to_database(m.group('shortname'), longname)
        if len(longname) < 20:
            shortname = longname
        else:
            shortname = f"{dt.date.today().strftime('%F')}-{idx}"
            msg = f"Need a custom name for '{longname}', using '{shortname}'"
            print(msg)

        return shortname

    def process_shortname_to_database(self, shortname, longname):
        breakpoint()
        pass



    def push_to_daily(self):

        self.df.to_sql('daily', self.engine, if_exists='append', index=False)
        return

        with self.conn.cursor() as cursor:

            tuples = [tuple(x) for x in self.df.to_numpy()]
            columns = ','.join(list(self.df.columns))
            sql = "insert into daily(%s) values %%s" % columns

            try:
                extras.execute_values(cursor, sql, tuples)
            except Exception as e:
                self.conn.rollback()
                raise

        self.conn.commit()

    def parse_input_file(self):

        data = []

        for idx, line in enumerate(self.infile.open()):

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

        #df['ip'] = df['ip'].astype(ipaddress.ip_address)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%b/%Y:%H:%M:%S %z')
        df['status'] = df['status'].astype(int)

        def fcn(x):
            if re.search(r'\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}', x):
                return x
            else:
                try:
                    return socket.gethostbyname(x)
                except:
                    return x

        df.loc[:, 'ip'] = df['ip'].apply(fcn)

        self.df = df


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)

    help = "Restrict to this user agent"
    parser.add_argument('--useragent', help=help)

    help = "Compute views instead of hits."
    parser.add_argument('--views', help=help, action='store_true')

    args = parser.parse_args()

    with BotLog(args.infile, useragent=args.useragent, views=args.views) as o:
        o.run()

            