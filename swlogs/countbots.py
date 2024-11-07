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

pd.options.display.float_format = '{:,.1f}'.format


UA_REGEX_STRS = [
    (
        # AcademicBotRTU (https://academicbot.rtu.lv; mailto:caps@rtu.lv)
        r"""AcademicBotRTU \(https://academicbot.rtu.lv; mailto:caps@rtu.lv\)""",
        'AcademicBotRTU',
    ),
    (
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 (Applebot/0.1; +http://www.apple.com/go/applebot)
        r"""Mozilla/5.0 \(Macintosh; Intel Mac OS X 10_15_7\) AppleWebKit/605.1.15 \(KHTML, like Gecko\) Version/17.4 Safari/605.1.15 \(Applebot/0.1; \+http://www.apple.com/go/applebot\)""",
        'Applebot/0.1',
    ),
    (
        # AppleCoreMedia/1.0.0.18J411 (Apple TV; U; CPU OS 14_0_2 like Mac OS X; en_us)
        r"""AppleCoreMedia/1.0.0.18J411 \(Apple TV; U; CPU OS 14_0_2 like Mac OS X; en_us\)""",
        'Apple/ATV OS X/WebKit on AppleTV',
    ),
    (
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko)
        r"""^Mozilla/5.0 \(Macintosh; Intel Mac OS X 10_15_7\) AppleWebKit/605.1.15 \(KHTML, like Gecko\)$""",
        'AppleMail/MacOS/Webkit',
    ),
    (
        # Mozilla/5.0 (compatible; Barkrowler/0.9; +https://babbar.tech/crawler)
        r"""Mozilla/5.0 \(compatible; Barkrowler/0.9; \+https://babbar.tech/crawler\)""",
        'Barkrowler',
    ),
    (
        # Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)
        r"""Mozilla/5.0 \(iPhone; CPU iPhone OS \d{1,2}_0 like Mac OS X\) AppleWebKit/537.51.1 \(KHTML, like Gecko\) Version/7.0 Mobile/11A465 Safari/9537.53 \(compatible; bingbot/2.0; \+http://www.bing.com/bingbot.htm\)""",
        'bingbot-2.0/iOS/WebKit on iPhone', 
    ),
    (
        # Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/116.0.1938.76 Safari/537.36
        r"""Mozilla/5.0 AppleWebKit/537.36 \(KHTML, like Gecko; compatible; bingbot/2.0; \+http://www.bing.com/bingbot.htm\) Chrome/\d+.\d+.\d+.\d+ Safari/537.36""",
        'bingbot/2.0', 
    ),
    (
        # Mozilla/5.0 (compatible; Bytespider; spider-feedback@bytedance.com) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.0.0 Safari/537.36
        r"""Mozilla/5.0 \(compatible; Bytespider; spider-feedback@bytedance.com\) AppleWebKit/\d+.\d+ \(KHTML, like Gecko\) Chrome/\d+(.\d+)+ Safari/\d+.\d+""",
        'Bytespider', 
    ),
    (
        # Mozilla/5.0 (Linux; Android 5.0) AppleWebKit/537.36 (KHTML, like Gecko) Mobile Safari/537.36 (compatible; Bytespider; spider-feedback@bytedance.com)
        r"""Mozilla/5.0 \(Linux; Android 5.0\) AppleWebKit/537.36 \(KHTML, like Gecko\) Mobile Safari/537.36 \(compatible; Bytespider; spider-feedback@bytedance.com\)""",
        'ByteSpider', 
    ),
    (
        # Cabin-Size/0.1 withcabin.com
        r"""Cabin-Size/0.1\swithcabin.com""",
        "Cabin-Size/0.1",
    ),
    (
        # CCBot/2.0 (https://commoncrawl.org/faq/)
        r"""CCBot/2.0 \(https://commoncrawl.org/faq/\)""",
        "CCBot/2.0",
    ),
    (
        # Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.58 Mobile Safari/537.36
        r"""Mozilla/5.0 \(Linux; Android 12; Pixel 6\) AppleWebKit/\d{3}.\d{2} \(KHTML, like Gecko\) Chrome/\d+(.\d+){3} Mobile Safari/\d+.\d+""",
        "Chrome/Android/Blink on Pixel",
    ),
    (
        # Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36
        r"""Mozilla/5.0 \(Linux; Android 10; K\) AppleWebKit/\d+.\d+ \(KHTML, like Gecko\) Chrome/\d+(.\d+)+ Safari/\d+.\d+""",
        "Chrome/Android/Blink on tablet",
    ),
    (
        # Mozilla/5.0 (Linux; Android 10; SM-G965U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Mobile Safari/537.36
        r"""Mozilla/5.0 \(Linux; Android 10; (K|SM-G965U)\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d+(.\d+){3} Mobile Safari/537.36""",
        "Chrome/Android/WebKit",
    ),
    (
        # Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36
        r"""Mozilla/5.0 \(Linux; Android 10; K\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d{2,3}(.\d+){3} Mobile Safari/537.36""",
        "Chrome/Android/WebKit",
    ),
    (
        # Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.126 Mobile Safari/537.36 (compatible; GoogleOther)
        r"""Mozilla/5.0 \(Linux; Android 6.0.1; Nexus 5X Build/MMB29P\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d+(.\d+)+ Mobile Safari/537.36 \(compatible; GoogleOther\)""",
        "GoogleOther/Chrome/Android/WebKit",
    ),
    (
        # Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36
        # Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36
        r"""Mozilla/5.0 \(X11; CrOS x86_64 14541.0.0\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d+(.\d+)+ Safari/537.36""",
        "Chrome/ChromeOS/Blink",
    ),
    (
        # Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1
        r"""Mozilla/5.0 \(iPad; CPU OS 17_\d like Mac OS X\) AppleWebKit/605.1.15 \(KHTML, like Gecko\) CriOS/\d+(.\d+)+ Mobile/15E148 Safari/604.1""",
        "Chrome/iOS/WebKit on iPad",
    ),
    (
        # Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/126.0.6478.153 Mobile/15E148 Safari/604.1
        r"""Mozilla/5.0 \(iPhone; CPU iPhone OS \d+(_\d+)+ like Mac OS X\) AppleWebKit/\d+(.\d+)+ \(KHTML, like Gecko\) CriOS/\d+.\d+.\d+.\d+ Mobile/15E148 Safari/\d+.\d+""",
        "Chrome/iOS/WebKit on iPhone",
    ),
    (
        # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36
        r"""Mozilla/5.0 \(X11; Linux x86_64\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d+.\d+.\d+.\d+ Safari/537.36""",
        "Chrome/Linux/Blink",
    ),
    (
        # Mozilla/5.0 (Linux x64) node.js/20.16.0 v8/11.3.244.8-node.23
        r"""Mozilla\/5.0 \(Linux x64\) node.js\/20.16.0 v8\/11.3.244.8-node.23""",
        "dspace-internal",
    ),
    (
        # Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/123.0.6312.86 Safari/537.36
        r"""Mozilla/5.0 \(X11; Linux x86_64\) AppleWebKit/\d+.\d+ \(KHTML, like Gecko\) HeadlessChrome/\d+.\d+.\d+.\d+ Safari/\d+.\d+""",
        "HeadlessChrome/Linux/Blink",
    ),
    (
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
        r"""Mozilla/5.0 \(Macintosh; Intel Mac OS X 10.15; rv:\d{2,3}.0\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d+.\d+.\d+.\d+ Safari/537.36""",
        "Chrome/Mactel/Blink",
    ),
    (
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36
        r"""Mozilla/5.0 \(Macintosh; Intel Mac OS X 1\d(_\d+)+\) AppleWebKit/\d+.\d+ \(KHTML, like Gecko\) Chrome/\d+.\d+.\d+.\d+ Safari/\d+.\d+""",
        "Chrome/Mactel32/Blink",
    ),
    (
        # Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36
        r"""Mozilla/5.0 \(Windows NT 6.1; WOW64\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d+.\d+.\d+.\d+ Safari/\d+.\d+""",
        "Chrome/Win7/Blink",
    ),
    (
        # Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36
        # Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36
        r"""Mozilla/5.0 \(Windows NT 10.0; Win64; x64\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d{2,3}.\d+.\d+.\d+ Safari/537.36""",
        "Chrome/Win10/Blink",
    ),
    (
        # Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/537.36
        r"""Mozilla/5.0 \(Windows NT 10.0; WOW64\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d+(.\d+)+ Safari/\d+.\d+""",
        "Chrome/Win10/WebKit",
    ),
    (
        r"""Mozilla/5.0 \(Windows; U; Windows NT 5.1; en-US\) AppleWebKit/525.13\(KHTML, like Gecko\) Chrome/0.2.149.27 Safari/525.13""",
        "Chrome/WinXP/WebKit",
    ),
    (
        # Mozilla/5.0 (compatible; DataForSeoBot/1.0; +https://dataforseo.com/dataforseo-bot)
        r"""Mozilla/5.0 \(compatible; DataForSeoBot/1.0; \+https://dataforseo.com/dataforseo-bot\)""",
        "DataForSEOBot",
    ),
    (
        # DuckDuckBot-Https/1.1; (+https://duckduckgo.com/duckduckbot)
        r"""DuckDuckBot-Https/1.1; \(\+https://duckduckgo.com/duckduckbot\)""",
        "DuckDuckBot",
    ),
    (
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0
        r"""Mozilla/5.0 \(Macintosh; Intel Mac OS X 10_15_7\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d+.\d+.\d+.\d+ Safari/537.36 Edg/\d+.\d+.\d+.\d+""",
        "Edge/Mactel32/Blink",
    ),
    (
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Papers/4.37.2394 Chrome/114.0.5735.289 Electron/25.9.0 Safari/537.36
        r"""Mozilla/5.0 \(Macintosh; Intel Mac OS X 10_15_7\) AppleWebKit/537.36 \(KHTML, like Gecko\) Papers/4.37.2394 Chrome/114.0.5735.289 Electron/25.9.0 Safari/537.36""",
        "Electron/MacOS/Blink",
    ),
    (
        # EZID (EZID link checker; https://ezid.cdlib.org/)
        r"""EZID \(EZID link checker; https://ezid.cdlib.org/\)""",
        "EZID link checker",
    ),
    (
        # facebookexternalhit/1.1
        # facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)
        r"""facebookexternalhit/1.1( \(\+http://www.facebook.com/externalhit_uatext.php\))?""",
        "Facebook/1.1",
    ),
    (
        # meta-externalagent/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/crawler)
        r"""meta-externalagent/1.1 \(\+https://developers.facebook.com/docs/sharing/webmasters/crawler\)""",
        "Facebook/meta-externalagent/1.1",
    ),
    (
        # Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/21E236 [FBAN/FBIOS;FBAV/441.0.0.23.105;FBBV/537255468;FBDV/iPhone12,1;FBMD/iPhone;FBSN/iOS;FBSV/17.4.1;FBSS/2;FBID/phone;FBLC/en_US;FBOP/5;FBRV/539748107]
        r"""ozilla/5.0 \(iPhone; CPU iPhone OS 17_4_1 like Mac OS X\) AppleWebKit/605.1.15 \(KHTML, like Gecko\) Mobile/21E236 \[FBAN/FBIOS;FBAV/441.0.0.23.105;FBBV/537255468;FBDV/iPhone12,1;FBMD/iPhone;FBSN/iOS;FBSV/17.4.1;FBSS/2;FBID/phone;FBLC/en_US;FBOP/5;FBRV/539748107\]""",
        "Facebook/iOS/WebKit on iPhone",
    ),
    (
        # Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/127.1  Mobile/15E148 Safari/605.1.15
        # Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/320.0.639621854 Mobile/15E148 Safari/604.1
        r"""Mozilla/5.0 \(iPhone; CPU iPhone OS \d+(_\d+)+ like Mac OS X\) AppleWebKit/\d+(.\d+)+ \(KHTML, like Gecko\) (FxiOS|GSA)/\d+(.\d)+\s+Mobile/15E148 Safari/\d+(.\d+)+""",
        "Firefox/iOS/WebKit on iPhone",
    ),
    (
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:128.0) Gecko/20100101 Firefox/128.0
        r"""Mozilla/5.0 \(Macintosh; Intel Mac OS X 10.15; rv:\d{3}.\d\) Gecko/20100101 Firefox/\d{2,3}""",
        "Firefox/Mactel15/Gecko",
    ),
    (
        # Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0 (compatible; img2dataset; +https://github.com/rom1504/img2dataset)
        r"""Mozilla/5.0 \(X11; Ubuntu; Linux x86_64; rv:72.0\) Gecko/20100101 Firefox/72.0( \(compatible; img2dataset; \+https://github.com/rom1504/img2dataset\))?""",
        "img2dataset",
    ),
    (
        # Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0
        r"""Mozilla/5.0 \(X11; Ubuntu; Linux x86_64; rv:72.0\) Gecko/20100101 Firefox/72.0""",
        "Firefox/Ubuntu/Gecko",
    ),
    (
        # Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0
        # Mozilla/5.0 (Windows NT 6.1; rv:57.0) Gecko/20100101 Firefox/57.0
        r"""Mozilla/5.0 \(Windows NT \d.\d; (Win64; x64; )?rv:\d+.\d\) Gecko/\d+ Firefox/\d+.\d""",
        "Firefox/Win7/Gecko",
    ),
    (
        # Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0
        # Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0
        # Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0
        # Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0
        r"""Mozilla/5.0 \(Windows NT 10.0; ((Win64; x64; )|(WOW64; ))?rv:\d+.\d\) Gecko/20100101 Firefox/\d+.\d""",
        "Firefox/Win10/Gecko",
    ),
    (
        # Go-http-client/1.1
        r"""Go-http-client/1.1""",
        "Go-http-client",
    ),
    (
        # Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) GSA/323.0.647062479 Mobile/15E148 Safari/604.1
        r"""Mozilla/5.0 \(iPad; CPU OS 17_5 like Mac OS X\) AppleWebKit/\d+(.\d+)+ \(KHTML, like Gecko\) GSA/\d+(.\d+)+ Mobile/15E148 Safari/\d+.\d+""",
        'Google/iOS/WebKit on iPad',
    ),
    (
        # Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
        r"""^Googlebot/2.1 \(\+http://www.google.com/bot.html\)$""",
        "Googlebot/2.1",
    ),
    (
        # Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.126 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
        r"""Mozilla/5.0 \(Linux; Android \d.\d.\d; Nexus 5X Build/MMB29P\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d+(.\d+)+ Mobile Safari/537.36 \(compatible; Googlebot/2.1; \+http://www.google.com/bot.html\)""",
        "Googlebot/Android/Blink",
    ),
    (
        # Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/125.0.6422.154 Safari/537.36
        r"""Mozilla/5.0 AppleWebKit/537.36 \(KHTML, like Gecko; compatible; Googlebot/2.1; \+http://www.google.com/bot.html\) Chrome/125.0.6422.154 Safari/537.36""",
        "Googlebot/2.1",
    ),
    (
        # Googlebot-Image/1.0
        r"""Googlebot-Image/1.0""",
        "Googlebot-Image/1.0",
    ),
    (
        # Googlebot-Video/1.0
        r"""Googlebot-Video/1.0""",
        "Googlebot-Video",
    ),
    (
        # Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.175 Mobile Safari/537.36 (compatible; GoogleOther)
        r"""Mozilla/5.0 \(Linux; Android 6.0.1; Nexus 5X Build/MMB29P\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/125.0.6422.175 Mobile Safari/537.36 \(compatible; GoogleOther\)""",
        "GoogleOther/Android/Blink on Nexus5X",
    ),
    (
        # Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.175 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
        r"""Mozilla/5.0 \(Linux; Android 6.0.1; Nexus 5X Build/MMB29P\) AppleWebKit/537.36 \(KHTML, like Gecko\) Chrome/\d+(.\d+){3} Mobile Safari/537.36 \(compatible; Googlebot/2.1; \+http://www.google.com/bot.html\)""",
        "Googlebot/2.1/Android/Blink on Nexus5X",
    ),
    (
        # Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)
        r"""Mozilla/5.0 AppleWebKit/537.36 \(KHTML, like Gecko; compatible; GPTBot/1.[02]; \+https://openai.com/gptbot\)""",
        'GPTBot/1.x',
    ),
    (
        # Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko
        r"""Mozilla/5.0 \(Windows NT 10.0; WOW64; Trident/7.0; rv:11.0\) like Gecko""",
        "IE/Win10/Trident",
    ),
    (
        # Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)
        # Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)
        r"""Mozilla/\d.0 \(compatible; MSIE 9.0; Windows NT 6.1(; Trident/5.0)?\)""",
        "IE/Win7/Trident",
    ),
    (
        # david frank
        # node-fetch/1.0
        r"""node-fetch/1.0 \(\+https://github.com/bitinn/node-fetch\)""",
        "node-fetch",
    ),
    (
        r"""Mozilla/5.0 AppleWebKit/537.36 \(KHTML, like Gecko\); compatible; OAI-SearchBot/1.0; \+https://openai.com/searchbot""",
        "OAI-SearchBot/1.0",
    ),
    (
        # Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [Pinterest/iOS]
        r"""Mozilla/5.0 \(iPhone; CPU iPhone OS 17_5_1 like Mac OS X\) AppleWebKit/605.1.15 \(KHTML, like Gecko\) Mobile/15E148 \[Pinterest/iOS\]""",
        "Pinterest/iOS/WebKit on iPhone",
    ),
    (
        # Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1
        # Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1
        # Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2534.1416 Mobile Safari/537.36
        r"""Mozilla/5.0 \(iPhone; CPU iPhone OS \d+(_\d+)+ like Mac OS X\) AppleWebKit/\d+(.\d+)+ \(KHTML, like Gecko\) (Chrome\/\d+.\d.\d+.\d+|Version/\d+(.\d)+) Mobile(\/15E148)? Safari/\d+.\d+""",
        "Safari/iOS/WebKit on iPhone",
    ),
    (
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)
        r"""Mozilla/5.0 \(Macintosh; Intel Mac OS X 10_12_6\)""",
        "Safari/Mactel/Sierra/Webkit (bad)",
    ),
    (
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15
        r"""Mozilla/5.0 \(Macintosh; Intel Mac OS X 10(_\d+)+\) AppleWebKit/605.1.15 \(KHTML, like Gecko\) Version/\d+(.\d+)+ Safari/\d+(.\d+)+""",
        "Safari/Mactel/Webkit",
    ),
    (
        r"""serpstatbot/2.1 \(advanced backlink tracking bot; https://serpstatbot.com/; abuse@serpstatbot.com\)""",
        "Serpstatbot",
    ),
    (
        r"""Mozilla/5.0 \(iPhone; CPU iPhone OS 17_3_1 like Mac OS X\) AppleWebKit/605.1.15 \(KHTML, like Gecko\) Version/17.3.1 Mobile/15E148 Snapchat/12.92.0.46 \(like Safari/8617.2.4.10.8, panda\)""",
        "Snapchat/iOS/Webkit on iPhone",
    ),
    (
        # Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0 Mobile Safari/537.36
        r"""Mozilla/5.0 \(Linux; Android 10; K\) AppleWebKit/537.36 \(KHTML, like Gecko\) SamsungBrowser""",
        "Samsung/Android/WebKit",
    ),
    (
        # Mozilla/5.0 (compatible) SemanticScholarBot (+https://www.semanticscholar.org/crawler)
        r"""Mozilla/5.0 \(compatible\) SemanticScholarBot \(\+https://www.semanticscholar.org/crawler\)""",
        "SemanticScholarBot",
    ),
    (
        # Mozilla/5.0 (compatible; SemrushBot/7~bl; +http://www.semrush.com/bot.html)
        r"""Mozilla/5.0 \(compatible; SemrushBot/7~bl; \+http://www.semrush.com/bot.html\)""",
        "SemrushBot",
    ),
    (
        # Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0) LinkCheck by Siteimprove.com
        r"""Mozilla/5.0 \(compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0\) LinkCheck by Siteimprove.com""",
        "Siteimprove",
    ),
    (
        # trafilatura/1.10.0 (+https://github.com/adbar/trafilatura)
        r"""trafilatura/1.1\d.\d \(\+https://github.com/adbar/trafilatura\)""",
        "trafilatura/1.x.y",
    ),
    (
        # Unpaywall (http://unpaywall.org/; mailto:team@impactstory.org)
        r"""Unpaywall \(http://unpaywall.org/; mailto:team@impactstory.org\)""",
        "Unpaywall",
    ),
    (
        # Mozilla/5.0 (Linux; Android 10; LIO-AN00 Build/HUAWEILIO-AN00; wv) MicroMessenger Weixin QQ AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.62 XWEB/2692 MMWEBSDK/200901 Mobile Safari/537.36
        r"""Mozilla/5.0 \(Linux; Android 10; LIO-AN00 Build/HUAWEILIO-AN00; wv\) MicroMessenger Weixin QQ AppleWebKit/537.36 \(KHTML, like Gecko\) Version/4.0 Chrome/78.0.3904.62 XWEB/2692 MMWEBSDK/200901 Mobile Safari/537.36""",
        "Webview/Android/WebKit",
    ),
    (
        # Mozilla/5.0 (compatible; wpbot/1.1; +https://forms.gle/ajBaxygz9jSR8p8G9)
        r"""Mozilla/5.0 \(compatible; wpbot/1.1; \+https://forms.gle/ajBaxygz9jSR8p8G9\)""",
        "WPBOT",
    ),
    (
        # Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)
        r"""Mozilla/5.0 \(compatible; YandexBot/3.0; \+http://yandex.com/bots\)""",
        "YandexBox",
    ),




]
UA_REGEX_REPLACE = {re.compile(pair[0]): pair[1] for pair in UA_REGEX_STRS}

def apply_regexes(s):

    first_match = next(filter(lambda x: x.search(s), UA_REGEX_REPLACE.keys()), None)
    return UA_REGEX_REPLACE.get(first_match, s)


class CountBots(object):

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

        print('\n')
        print('Top IPs with netmask/32')
        print(df20)
        print('\n')

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

        print('\n')
        print('Top IPs with netmask/16')
        print(df20)
        print('\n')

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


        print('\n')
        print('Top IPs with netmask/24')
        print(df20)
        print('\n')

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
            
            
            if (idx % 100000) == 0:
                print(idx)

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

            
