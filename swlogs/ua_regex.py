import re


_ua_pairs = [
    (
        # AcademicBotRTU (https://academicbot.rtu.lv; mailto:caps@rtu.lv)
        r"""
        AcademicBotRTU
        \s
        \(https://academicbot.rtu.lv;\smailto:caps@rtu.lv\)""",
        'AcademicBotRTU',
    ),
    (
        # Mozilla/5.0
        # (Macintosh; Intel Mac OS X 10_10_1)
        # AppleWebKit/600.2.5
        # (KHTML, like Gecko)
        # Version/8.0.2
        # Safari/600.2.5
        # (Amazonbot/0.1; +https://developer.amazon.com/support/amazonbot)
        r"""
        Mozilla/5.0
        \s
        \(Macintosh;\sIntel\sMac\sOS\sX\s\d{2}_\d{2}_\d\)
        \s
        AppleWebKit/\d+.\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Version/\d+.\d+.\d+
        \s
        Safari/\d+.\d+.\d+
        \s
        \(Amazonbot/0.1;\s\+https://developer.amazon.com/support/amazonbot\)
        """,
        "Amazonbot",
    ),
    (
        # Mozilla/5.0
        # AppleWebKit/537.36
        # (
        #   KHTML, like Gecko;
        #   compatible;
        #   Amazonbot/0.1;
        #   +https://developer.amazon.com/support/amazonbot
        # )
        # Chrome/119.0.6045.214
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        AppleWebKit/\d+.\d+.\d+
        \s
        \(
            KHTML,\slike\sGecko;
            \s
            compatible;
            \s
            Amazonbot/0.1;
            \s
            \+https://developer.amazon.com/support/amazonbot
        \)
        \s
        Chrome/\d+(.\d+)+
        \s
        Safari/\d+.\d+.\d+
        """,
        "Amazonbot",
    ),
    (
        # AppleCoreMedia/1.0.0.18J411
        # (Apple TV; U; CPU OS 14_0_2 like Mac OS X; en_us)
        r"""
        AppleCoreMedia/1.0.0.18J411
        \s
        \(Apple\sTV;\sU;\sCPU\sOS\s14_0_2\slike\sMac\sOS\sX;\sen_us\)""",
        'Apple/ATV OS X/WebKit on AppleTV',
    ),
    (
        # Mozilla/5.0
        # (Macintosh; Intel Mac OS X 10_15_7)
        # AppleWebKit/605.1.15
        # (KHTML, like Gecko)
        # Version/17.4
        # Safari/605.1.15
        # (Applebot/0.1; +http://www.apple.com/go/applebot)
        r"""
        Mozilla/5.0
        \s
        \(Macintosh;\sIntel\sMac\sOS\sX\s10_15_7\)
        \s
        AppleWebKit/605.1.15
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Version/\d{2}.\d
        \s
        Safari/605.1.15
        \s
        \(Applebot/0.1;\s\+http://www.apple.com/go/applebot\)""",
        'Applebot/0.1',
    ),
    (
        # Mozilla/5.0
        # (Macintosh; Intel Mac OS X 10_15_7)
        # AppleWebKit/605.1.15
        # (KHTML, like Gecko)
        r"""
        ^Mozilla/5.0
        \s
        \(Macintosh;\sIntel\sMac\sOS\sX\s10_15_7\)
        \s
        AppleWebKit/605.1.15
        \s
        \(KHTML,\slike\sGecko\)$""",
        'AppleMail/MacOS/Webkit',
    ),
    (
        # Mozilla/5.0
        # (compatible; AwarioBot/1.0; +https://awario.com/bots.html)
        r"""
        Mozilla/5.0
        \s
        \(compatible;\sAwarioBot/1.0;\s\+https://awario.com/bots.html\)
        """,
        'AwarioBot',
    ),
    (
        # Mozilla/5.0
        # (compatible; Barkrowler/0.9; +https://babbar.tech/crawler)
        r"""
        Mozilla/5.0
        \s
        \(compatible;\sBarkrowler/0.9;\s\+https://babbar.tech/crawler\)""",
        'Barkrowler',
    ),
    (
        # Mozilla/5.0
        # (iPhone; CPU iPhone OS 7_0 like Mac OS X)
        # AppleWebKit/537.51.1
        # (KHTML, like Gecko)
        # Version/7.0
        # Mobile/11A465 Safari/9537.53
        # (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)
        r"""
        Mozilla/5.0
        \s
        \(iPhone;\sCPU\siPhone\sOS\s\d{1,2}_0\slike\sMac\sOS\sX\)
        \s
        AppleWebKit/\d+.\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Version/7.0\sMobile/11A465
        \s
        Safari/9537.53
        \s
        \(compatible;\sbingbot/2.0;\s\+http://www.bing.com/bingbot.htm\)""",
        'bingbot/iOS/WebKit/iPhone/2.0',
    ),
    (
        # Mozilla/5.0
        # AppleWebKit/537.36
        # (KHTML, like Gecko; compatible; bingbot/2.0;
        #  +http://www.bing.com/bingbot.htm)
        # Chrome/116.0.1938.76
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        AppleWebKit/\d+.\d+
        \s
        \(
            KHTML,
            \s
            like\sGecko;
            \s
            compatible;
            \s
            bingbot/2.0;
            \s
            \+http://www.bing.com/bingbot.htm
        \)
        \s
        Chrome/\d+.\d+.\d+.\d+
        \s
        Safari/537.36""",
        'bingbot/2.0',
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 6.0.1; Nexus 5X Build/MMB29P)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/112.0.0.0
        # Mobile Safari/537.36
        # (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s\d.\d.\d;\sNexus\s5X\sBuild/\w+\)
        \s
        AppleWebKit/\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+.\d+.\d+.\d+
        \s
        Mobile\sSafari/\d+.\d+
        \s
        \(compatible;\sbingbot/2.0;\s\+http://www.bing.com/bingbot.htm\)
        """,
        'bingbot/2.0',
    ),
    (
        # Mozilla/5.0
        # (iPhone; CPU iPhone OS 7_0 like Mac OS X)
        # AppleWebKit/537.51.1
        # (KHTML, like Gecko)
        # Version/7.0
        # Mobile/11A465 Safari/9537.53
        # BingPreview/1.0b
        r"""
        Mozilla/5.0
        \s
        \(iPhone;\sCPU\siPhone\sOS\s\d{1,2}_0\slike\sMac\sOS\sX\)
        \s
        AppleWebKit/537.51.1
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Version/\d.\d\sMobile/11A465
        \s
        Safari/\d{4}.\d{2}
        \s
        BingPreview\/\d.\d\w""",
        'BingPreview'
    ),
    (
        # Mozilla/5.0
        # (compatible; Bytespider; spider-feedback@bytedance.com)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/70.0.0.0
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(compatible;\sBytespider;\sspider-feedback@bytedance.com\)
        \s
        AppleWebKit/\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+(.\d+)+
        \s
        Safari/\d+.\d+""",
        'Bytespider',
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 5.0)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Mobile Safari/537.36
        # (compatible; Bytespider; spider-feedback@bytedance.com)
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s5.0\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Mobile\sSafari/537.36
        \s
        \(compatible;\sBytespider;\sspider-feedback@bytedance.com\)""",
        'ByteSpider',
    ),
    (
        # Cabin-Size/0.1 withcabin.com
        r"""Cabin-Size/0.1\swithcabin.com""",
        "Cabin-Size/0.1",
    ),
    (
        # CCBot/2.0 (https://commoncrawl.org/faq/)
        r"""CCBot/2.0\s\(https://commoncrawl.org/faq/\)""",
        "CCBot/2.0",
    ),
    (
        # Mozilla/5.0
        # AppleWebKit/537.36
        # (KHTML, like Gecko);
        # compatible; ChatGPT-User/1.0;
        # +https://openai.com/bot
        r"""
        Mozilla/5.0
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\);
        \s
        compatible;
        \s
        ChatGPT-User/\d.\d;
        \s
        \+https://openai.com/(gpt)?bot
        """,
        'ChatGPT-User/1.0',
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 12; Pixel 6)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/99.0.4844.58
        # Mobile Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s12;\sPixel\s6\)
        \s
        AppleWebKit/\d{3}.\d{2}
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+(.\d+){3}
        \s
        Mobile\sSafari/\d+.\d+""",
        "Chrome/Android/Blink on Pixel",
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 10; K)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/125.0.0.0
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s10;\sK\)
        \s
        AppleWebKit/\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+(.\d+)+
        \s
        Safari/\d+.\d+""",
        "Chrome/Android/Blink on tablet",
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 10; SM-G965U)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/102.0.0.0
        # Mobile Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s10;\s(K|SM-G965U)\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+(.\d+){3}
        \s
        Mobile\sSafari/537.36""",
        "Chrome/Android/WebKit",
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 10; K)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/126.0.0.0
        # Mobile Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s10;\sK\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d{2,3}(.\d+){3}
        \s
        Mobile\sSafari/537.36""",
        "Chrome/Android/WebKit",
    ),
    (
        # Mozilla/5.0
        # (X11; CrOS x86_64 14541.0.0)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/124.0.0.0
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(X11;\sCrOS\sx86_64\s14541.0.0\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+(.\d+)+
        \s
        Safari/537.36""",
        "Chrome/ChromeOS/Blink",
    ),
    (
        # Mozilla/5.0
        # (iPad; CPU OS 17_2 like Mac OS X)
        # AppleWebKit/605.1.15
        # (KHTML, like Gecko)
        # CriOS/120.0.6099.119
        # Mobile/15E148
        # Safari/604.1
        r"""
        Mozilla/5.0
        \s
        \(iPad;\sCPU\sOS\s\d+(_\d)+\slike\sMac\sOS\sX\)
        \s
        AppleWebKit/\d+(.\d+)+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        CriOS/\d+(.\d+)+
        \s
        Mobile/15E148
        \s
        Safari/\d+.\d""",
        "Chrome/iOS/WebKit on iPad",
    ),
    (
        # Mozilla/5.0
        # (iPhone; CPU iPhone OS 17_5 like Mac OS X)
        # AppleWebKit/605.1.15
        # (KHTML, like Gecko)
        # CriOS/126.0.6478.153
        # Mobile/15E148
        # Safari/604.1
        r"""
        Mozilla/5.0
        \s
        \(iPhone;\sCPU\siPhone\sOS\s\d+(_\d+)+\slike\sMac\sOS\sX\)
        \s
        AppleWebKit/\d+(.\d+)+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        CriOS/\d+.\d+.\d+.\d+
        \s
        Mobile/15E148
        \s
        Safari/\d+.\d+""",
        "Chrome/iOS/WebKit/iPhone",
    ),
    (
        # Mozilla/5.0
        # (X11; Linux x86_64)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/126.0.0.0
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(X11;\sLinux\sx86_64\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+.\d+.\d+.\d+
        \s
        Safari/537.36""",
        "Chrome/Linux/Blink",
    ),
    (
        # Mozilla/5.0
        # (X11; Linux x86_64)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # HeadlessChrome/123.0.6312.86
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(X11;\sLinux\sx86_64\)
        \s
        AppleWebKit/\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        HeadlessChrome/\d+.\d+.\d+.\d+
        \s
        Safari/\d+.\d+""",
        "HeadlessChrome/Linux/Blink",
    ),
    (
        # Mozilla/5.0
        # (Macintosh; Intel Mac OS X 10_15_4)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/83.0.4103.97 Safari/537.36
        #
        # Mozilla/5.0
        # (Macintosh; Intel Mac OS X 10.15; rv:109.0)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/108.0.0.0
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Macintosh;\sIntel\sMac\sOS\sX\s1\d(_\d+)+\)
        \s
        AppleWebKit/\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+.\d+.\d+.\d+
        \s
        Safari/\d+.\d+""",
        "Chrome/Mactel32/Blink",
    ),
    (
        # Mozilla/5.0
        # (Windows NT 6.1; WOW64)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/50.0.2661.102 Safari/537.36
        #
        # Mozilla/5.0
        # (Windows NT 6.1; Win64; x64)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/61.0.3163.79 Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Windows\sNT\s6.1;\s(WOW64|Win64;\sx64)\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+.\d+.\d+.\d+
        \s
        Safari/\d+.\d+""",
        "Chrome/Win7/Blink",
    ),
    (
        # Mozilla/5.0
        # (Windows NT 6.2; Win64; x64)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/59.0.3071.86
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Windows\sNT\s6.2;\sWin64;\sx64\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+.\d+.\d+.\d+
        \s
        Safari/\d+.\d+""",
        "Chrome/Win8/Blink",
    ),
    (
        # Mozilla/5.0
        # (Windows NT 10.0; Win64; x64)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/125.0.0.0 Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Windows\sNT\s10.0;\sWin64;\sx64\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d{2,3}.\d+.\d+.\d+
        \s
        Safari/537.36""",
        "Chrome/Win10/Blink",
    ),
    (
        # Mozilla/5.0 (Windows NT 10.0; WOW64)
        # AppleWebKit/537.36
        # (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Windows\sNT\s10.0;\sWOW64\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+(.\d+)+
        \s
        Safari/\d+.\d+""",
        "Chrome/Win10/WebKit",
    ),
    (
        # Mozilla/5.0
        # AppleWebKit/537.36
        # (KHTML, like Gecko;
        #   compatible; ClaudeBot/1.0; +claudebot@anthropic.com)
        r"""
        Mozilla/5.0
        \s
        AppleWebKit/\d{3}.\d{2}
        \s
        \(KHTML,\slike\sGecko;\s
        compatible;
        \s
        ClaudeBot/1.0;
        \s
        \+claudebot@anthropic.com\)
        """,
        "ClaudeBot",
    ),
    (
        r"""
        Mozilla/5.0
        \s
        \(Windows;\sU;\sWindows\sNT\s5.1;\sen-US\)
        \s
        AppleWebKit/525.13
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/0.2.149.27
        \s
        Safari/525.13""",
        "Chrome/WinXP/WebKit",
    ),
    (
        # Mozilla/5.0
        # (
        #   compatible;
        #   DataForSeoBot/1.0; +https://dataforseo.com/dataforseo-bot
        # )
        r"""
        Mozilla/5.0
        \s
        \(compatible;
        \s
        DataForSeoBot/1.0;
        \s
        \+https://dataforseo.com/dataforseo-bot\)""",
        "DataForSEOBot",
    ),
    (
        # Mozilla/5.0 (Linux x64) node.js/20.16.0 v8/11.3.244.8-node.23
        r"""
            Mozilla\/5.0
            \s
            \(Linux\sx64\)
            \s
            node.js\/20.\d{2}.0
            \s
            v8\/11.3.244.8-node.23
        """,
        "dspace-internal",
    ),
    (
        # DuckDuckBot-Https/1.1; (+https://duckduckgo.com/duckduckbot)
        r"""
        DuckDuckBot-Https/1.1;
        \s
        \(\+https://duckduckgo.com/duckduckbot\)""",
        "DuckDuckBot",
    ),
    (
        # Mozilla/5.0
        # (Macintosh; Intel Mac OS X 10_15_7)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/126.0.0.0
        # Safari/537.36
        # Edg/126.0.0.0
        r"""
        Mozilla/5.0
        \s
        \(Macintosh;
        \s
        Intel\sMac\sOS\sX\s10_15_7\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+.\d+.\d+.\d+
        \s
        Safari/537.36 Edg/\d+.\d+.\d+.\d+""",
        "Edge/Mactel32/Blink",
    ),
    (
        # Mozilla/5.0
        # (Macintosh; Intel Mac OS X 10_15_7)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Papers/4.37.2394
        # Chrome/114.0.5735.289
        # Electron/25.9.0
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Macintosh;\sIntel\sMac\sOS\sX\s10_15_7\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Papers/4.37.2394
        \s
        Chrome/114.0.5735.289
        \s
        Electron/25.9.0
        \s
        Safari/537.36""",
        "Electron/MacOS/Blink",
    ),
    (
        # EZID (EZID link checker; https://ezid.cdlib.org/)
        r"""
        EZID
        \s
        \(EZID\slink\schecker;\shttps://ezid.cdlib.org/\)""",
        "EZID link checker",
    ),
    (
        # facebookexternalhit/1.1
        #
        # facebookexternalhit/1.1
        # (+http://www.facebook.com/externalhit_uatext.php)
        r"""
        facebookexternalhit/1.1
        (\s\(\+http://www.facebook.com/externalhit_uatext.php\))?""",
        "Facebook/1.1",
    ),
    (
        # meta-externalagent/1.1
        # (+https://developers.facebook.com/docs/sharing/webmasters/crawler)
        r"""
        meta-externalagent/1.1
        \s
        \(\+https://developers.facebook.com/docs/sharing/webmasters/crawler\)""",  # noqa : E501
        "Facebook/meta-externalagent/1.1",
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 11; SM-A125F Build/RP1A.200720.012; wv)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Version/4.0
        # Chrome/117.0.0.0
        # Mobile Safari/537.36
        # [FB_IAB/FB4A;FBAV/474.1.0.47.109;]
        #
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s\d+;\s[\w-]+\sBuild/\w{4}.\d{6}.\d{3};\swv\)
        \s
        AppleWebKit/\d+.\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Version/\d+(.\d+)+
        \s
        Chrome/\d+(.\d+)+
        \s
        (Mobile\s)?
        Safari/\d+.\d+
        \s
        \[
            FB_IAB/FB4A;
            FBAV/\d+(.\d+)+;
        \]
        """,
        "Facebook/Android/Blink",
    ),
    (
        # Mozilla/5.0
        # (iPhone; CPU iPhone OS 17_4_1 like Mac OS X)
        # AppleWebKit/605.1.15
        # (KHTML, like Gecko)
        # Mobile/21E236
        # [
        #   FBAN/FBIOS;
        #   FBAV/441.0.0.23.105;
        #   FBBV/537255468;
        #   FBDV/iPhone12,1;
        #   FBMD/iPhone;
        #   FBSN/iOS;
        #   FBSV/17.4.1;
        #   FBSS/2;
        #   FBID/phone;
        #   FBLC/en_US;
        #   FBOP/5;
        #   FBRV/539748107
        # ]
        r"""
        Mozilla/5.0
        \s
        \(iPhone;\sCPU\siPhone\sOS\s17_4_1\slike\sMac\sOS\sX\)
        \s
        AppleWebKit/605.1.15
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Mobile/21E236
        \s
        \[
            FBAN/FBIOS;
            FBAV/441.0.0.23.105;
            FBBV/537255468;
            FBDV/iPhone12,1;
            FBMD/iPhone;
            FBSN/iOS;
            FBSV/17.4.1;
            FBSS/2;
            FBID/phone;
            FBLC/en_US;
            FBOP/5;
            FBRV/539748107
        \]
        """,
        "Facebook/iOS/WebKit/iPhone",
    ),
    (
        # Mozilla/5.0
        # (Android 14; Mobile; rv:133.0)
        # Gecko/133.0 Firefox/133.0
        r"""
        Mozilla/5.0
        \s
        \(
            Android\s\d+;
            \s
            Mobile;
            \s
            rv:\d+.\d
        \)
        \s
        Gecko/\d+.\d\sFirefox/\d+.\d
        """,
        "Firefox/Android/Gecko",
    ),
    (
        # Mozilla/5.0
        # (iPhone; CPU iPhone OS 17_5_1 like Mac OS X)
        # AppleWebKit/605.1.15
        # (KHTML, like Gecko)
        # FxiOS/127.1  Mobile/15E148 Safari/605.1.15
        r"""
        Mozilla/5.0
        \s
        \(iPhone;\sCPU\siPhone\sOS\s\d+(_\d+)+\slike\sMac\sOS\sX\)
        \s
        AppleWebKit/\d+(.\d+)+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        (FxiOS|GSA)/\d+(.\d)+
        \s+
        Mobile/15E148
        \s
        Safari/\d+(.\d+)+
        """,
        "Firefox/iOS/WebKit/iPhone",
    ),
    (
        # Mozilla/5.0
        # (X11; Linux x86_64; rv:132.0)
        # Gecko/20100101 Firefox/132.0
        r"""
        Mozilla/5.0
        \s
        \(X11;\sLinux\sx86_64;\srv:\d+.\d\)
        \s
        Gecko/\d+\sFirefox/\d+.\d
        """,
        "Firefox/Linux/Gecko",
    ),
    (
        # Mozilla/5.0
        # (Macintosh; Intel Mac OS X 10.15; rv:128.0)
        # Gecko/20100101
        # Firefox/128.0
        r"""
        Mozilla/5.0
        \s
        \(
            Macintosh;
            \s
            Intel
            \s
            Mac
            \s
            OS
            \s
            X
            \s
            10.15;
            \s
            rv:\d{3}.\d
        \)
        \s
        Gecko/20100101
        \s
        Firefox/\d{2,3}
        """,
        "Firefox/Mactel15/Gecko",
    ),
    (
        # Mozilla/5.0
        # (X11; Ubuntu; Linux x86_64; rv:72.0)
        # Gecko/20100101 Firefox/72.0
        r"""
        Mozilla/5.0
        \s
        \(X11;\sUbuntu;\sLinux\sx86_64;\srv:\d+.\d\)
        \s
        Gecko/\d+\sFirefox/\d+.\d
        """,
        "Firefox/Ubuntu/Gecko",
    ),
    (
        # Mozilla/5.0
        # (Windows NT 6.1; Win64; x64; rv:102.0)
        # Gecko/20100101 Firefox/102.0
        #
        # Mozilla/5.0
        # (Windows NT 6.1; rv:57.0)
        # Gecko/20100101 Firefox/57.0
        #
        # Mozilla/5.0
        # (Windows NT 6.1; WOW64; rv:22.0)
        # Gecko/20100101 Firefox/22.0
        r"""
        Mozilla/5.0
        \s
        \(
          Windows\sNT\s\d.\d;
          \s
          (
            (Win64;\sx64;|WOW64;)
            \s
          )?
          rv:\d+.\d
        \)
        \s
        Gecko/\d+\sFirefox/\d+.\d
        """,
        "Firefox/Win7/Gecko",
    ),
    (
        # Mozilla/5.0
        # (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5)
        # Gecko/20091102
        # Firefox/3.5.5
        # (.NET CLR 3.5.30729)
        r"""
        Mozilla/5.0
        \s
        \(Windows;\sU;\sWindows\sNT\s6.1;\sen-US;\srv:\d.\d.\d.\d\)
        \s
        Gecko/\d+
        \s
        Firefox/\d+.\d+.\d+
        \s
        \(.NET\sCLR\s\d+.\d+.\d+\)
        """,
        "Firefox/Win7/Gecko",
    ),
    (
        # Mozilla/5.0
        # (Windows NT 10.0; Win64; x64; rv:127.0)
        # Gecko/20100101 Firefox/127.0
        #
        # Mozilla/5.0
        # (Windows NT 10.0; rv:128.0)
        # Gecko/20100101 Firefox/128.0
        #
        # Mozilla/5.0
        # (Windows NT 10.0; WOW64; rv:60.0)
        # Gecko/20100101 Firefox/60.0
        r"""
        Mozilla/5.0
        \s
        \(Windows\sNT\s10.0;
        \s
        ((Win64;\sx64;\s)|(WOW64;\s))?rv:\d+.\d\)
        \s
        Gecko/20100101
        \s
        Firefox/\d+.\d""",
        "Firefox/Win10/Gecko",
    ),
    (
        # Go-http-client/1.1
        r"""Go-http-client/1.1""",
        "Go-http-client",
    ),
    (
        # Mozilla/5.0
        # (iPad; CPU OS 17_5 like Mac OS X)
        # AppleWebKit/605.1.15
        # (KHTML, like Gecko)
        # GSA/323.0.647062479 Mobile/15E148 Safari/604.1
        r"""
        Mozilla/5.0
        \s
        \(iPad;\sCPU\sOS\s17_5\slike\sMac\sOS\sX\)
        \s
        AppleWebKit/\d+(.\d+)+
        \s
        \(KHTML, like Gecko\)
        \s
        GSA/\d+(.\d+)+
        \s
        Mobile/15E148
        \s
        Safari/\d+.\d+""",
        'Google/iOS/WebKit on iPad',
    ),
    (
        # Googlebot/2.1 (+http://www.google.com/bot.html)
        r"""
        Googlebot/2.1
        \s
        \(\+http://www.google.com/bot.html\)
        """,
        "Googlebot/2.1",
    ),
    (
        # Mozilla/5.0
        # (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
        r"""
        Mozilla/5.0
        \s
        \(
            compatible;
            \s
            Googlebot/2.1;
            \s
            \+http://www.google.com/bot.html
        \)
        """,
        "Googlebot/2.1",
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 6.0.1; Nexus 5X Build/MMB29P)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/126.0.6478.126 Mobile Safari/537.36
        # (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s\d.\d.\d;\sNexus\s5X\sBuild/MMB29P\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+(.\d+)+\sMobile\sSafari/537.36
        \s
        \(compatible;\sGooglebot/2.1;\s\+http://www.google.com/bot.html\)""",
        "Googlebot/Android/Blink",
    ),
    (
        # Mozilla/5.0 AppleWebKit/537.36
        # (KHTML, like Gecko; compatible; Googlebot/2.1;
        # +http://www.google.com/bot.html)
        # Chrome/125.0.6422.154 Safari/537.36
        r"""
        Mozilla/5.0
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko;\scompatible;\sGooglebot/2.1;
        \s
        \+http://www.google.com/bot.html\)
        \s
        Chrome/\d{3}.\d.\d{4}.\d{2,3}\sSafari/537.36""",
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
        # Mozilla/5.0
        # (Linux; Android 6.0.1; Nexus 5X Build/MMB29P)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/125.0.6422.175 Mobile Safari/537.36 (compatible; GoogleOther)
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s6.0.1;\sNexus\s5X\sBuild/MMB29P\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike Gecko\)
        \s
        Chrome/125.0.6422.175\sMobile\sSafari/537.36
        \s
        \(compatible;\sGoogleOther\)""",
        "GoogleOther/Android/Blink on Nexus5X",
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 6.0.1; Nexus 5X Build/MMB29P)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/126.0.6478.126
        # Mobile Safari/537.36
        # (compatible; GoogleOther)
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s6.0.1;\sNexus\s5X\sBuild/MMB29P\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+(.\d+)+
        \s
        Mobile\sSafari/537.36
        \s
        \(compatible;\sGoogleOther\)""",
        "GoogleOther/Chrome/Android/WebKit",
    ),
    (
        # Mozilla/5.0 (Linux; # Android 6.0.1; Nexus 5X Build/MMB29P)
        # AppleWebKit/537.36 (KHTML, like Gecko)
        # Chrome/125.0.6422.175 Mobile Safari/537.36
        # (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s6.0.1;\sNexus\s5X\sBuild/MMB29P\)
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+(.\d+){3}
        \s
        Mobile\sSafari/537.36
        \s
        \(compatible;\sGooglebot/2.1;\s\+http://www.google.com/bot.html\)
        """,
        "Googlebot/2.1/Android/Blink on Nexus5X",
    ),
    (
        # Mozilla/5.0
        # AppleWebKit/537.36
        # (KHTML, like Gecko; compatible; GPTBot/1.2;
        #  +https://openai.com/gptbot)
        #
        # Mozilla/5.0
        # AppleWebKit/537.36
        # (KHTML, like Gecko);
        # compatible; ChatGPT-User/1.0;
        # +https://openai.com/bot
        r"""
        Mozilla/5.0
        \s
        AppleWebKit/537.36
        \s
        \(KHTML,\slike\sGecko;
        \s
        compatible;
        \s
        GPTBot/1.[02];
        \s
        \+https://openai.com/gptbot\)
        """,
        'GPTBot/1.x',
    ),
    (
        # Grammarly/1.0 (http://www.grammarly.com)
        r"""
        Grammarly/1.0
        \s
        \(http://www.grammarly.com\)
        """,
        "Grammarly",
    ),
    (
        # Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko
        r"""
        Mozilla/5.0
        \s
        \(Windows\sNT\s10.0;\sWOW64;\sTrident/7.0;\srv:11.0\)\slike\sGecko
        """,
        "IE/Win10/Trident",
    ),
    (
        # Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)
        # Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)
        r"""
        Mozilla/\d.0
        \s
        \(compatible;\sMSIE\s9.0;\sWindows\sNT\s6.1(;\sTrident/5.0)?\)
        """,
        "IE/Win7/Trident",
    ),
    (
        # Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)
        r"""
        Mozilla/\d.0
        \s
        \(compatible;\sMSIE\s8.0;\sWindows\sNT\s5.1;\sTrident/4.0\)
        """,
        "IE/WinXP/Trident",
    ),
    (
        # Mozilla/5.0 (compatible; ImagesiftBot; +imagesift.com)
        r"""
        Mozilla/\d.0
        \s
        \(compatible;\sImagesiftBot;\s\+imagesift.com\)
        """,
        "ImagesiftBot",
    ),
    (
        # Mozilla/5.0 (compatible; U; Koha checkurl)
        r"""
        Mozilla/\d.0
        \s
        \(compatible;\sU;\sKoha\scheckurl\)
        """,
        "Koha checkurl",
    ),
    (
        # netEstate NE Crawler (+http://www.website-datenbank.de/)
        r"""
        netEstate\sNE\sCrawler
        \s
        \(\+http://www.website-datenbank.de/\)
        """,
        "netEstate NE Crawler",
    ),
    (
        # david frank
        # node-fetch/1.0
        r"""node-fetch/1.0\s\(\+https://github.com/bitinn/node-fetch\)""",
        "node-fetch",
    ),
    (
        # check_http/v2.4.12 (nagios-plugins 2.4.12)
        r"""check_http/v\d.\d.\d+\s\(nagios-plugins\s\d.\d.\d+\)""",
        "nagios/check_http",
    ),
    (
        r"""
            Mozilla/5.0
            \s
            AppleWebKit/537.36
            \s
            \(KHTML,\slike\sGecko\);
            \s
            compatible;
            \s
            OAI-SearchBot/1.0;
            \s
            \+https://openai.com/searchbot""",
        "OAI-SearchBot/1.0",
    ),
    (
        # Opera/9.80
        # (Windows NT 6.1; WOW64; MRA 6.0 (build 6080))
        # Presto/2.12.388
        # Version/12.14
        r"""
        Opera/\d+.\d+
        \s
        \(Windows\sNT\s6.1;\sWOW64;\sMRA\s\d.\d\s\(build\s\d+\)\)""",
        "Opera/Win7/Presto",
    ),
    (
        # Owler (ows.eu/owler)
        r"""
        Owler
        \s
        \(ows.eu/owler\)""",
        "Owler",
    ),
    (
        # Seems to be an AI bot
        #
        # Mozilla/5.0
        # AppleWebKit/537.36
        # (KHTML, like Gecko;
        #  compatible;
        #  PerplexityBot/1.0;
        #  +https://docs.perplexity.ai/docs/perplexity-bot)
        r"""
        Mozilla/5.0
        \s
        AppleWebKit/\d+.\d+.\d+
        \s
        \(
            KHTML,\slike\sGecko;
            \s
            compatible;
            \s
            PerplexityBot/1.0;
            \s
            \+https://docs.perplexity.ai/docs/perplexity-bot
        \)
        """,
        "Perplexity",
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 7.0;)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Mobile Safari/537.36
        # (compatible;
        #  PetalBot;+https://webmaster.petalsearch.com/site/petalbot)
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s\d.\d;\)
        \s
        AppleWebKit/\d+.\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Mobile\sSafari/\d+.\d+
        \s
        \(
          compatible;
          \s
          PetalBot;
          \+https://webmaster.petalsearch.com/site/petalbot
        \)
        """,
        "PetalBot/Aspiegel/Android",
    ),
    (
        # Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X)
        # AppleWebKit/605.1.15
        # (KHTML, like Gecko) Mobile/15E148 [Pinterest/iOS]
        r"""
            Mozilla/5.0
            \s
            \(iPhone;\sCPU\siPhone\sOS\s17_5_1\slike\sMac\sOS\sX\)
            \s
            AppleWebKit/605.1.15\s\(KHTML,\slike\sGecko\)
            \s
            Mobile/15E148
            \s
            \[Pinterest/iOS\]""",
        "Pinterest/iOS/WebKit/iPhone",
    ),
    (
        # Mozilla/5.0
        # (Macintosh; Intel Mac OS X 10_15_7)
        # AppleWebKit/605.1.15
        # (KHTML, like Gecko)
        # Mobile/15E148
        r"""
        Mozilla/5.0
        \s
        \(Macintosh;\sIntel\sMac\sOS\sX\s10_15_7\)
        \s
        AppleWebKit/\d+.\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Mobile/15E148
        """,
        "PulseMobileClient/MacOS",
    ),
    (
        # Mozilla/5.0
        # (iPhone; CPU iPhone OS 11_0 like Mac OS X)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/57.0.2534.1416
        # Mobile
        # Safari/537.36
        #
        # Mozilla/5.0
        # (iPhone; CPU iPhone OS 17_5_1 like Mac OS X)
        # AppleWebKit/605.1.15
        # (KHTML, like Gecko)
        # Version/17.5
        # Mobile/15E148
        # Safari/604.1
        r"""
        Mozilla/5.0
        \s
        \(iPhone;\sCPU\siPhone\sOS\s\d+(_\d+)+\slike\sMac\sOS\sX\)
        \s
        AppleWebKit/\d+(.\d+)+
        \s
        \(KHTML,\slike\sGecko\)
        \s+
        ((Chrome|Version)/\d+(.\d+)+\s)?
        Mobile(\/15E148)?
        \s
        Safari/\d+.\d+""",
        "Safari/iOS/WebKit/iPhone",
    ),
    (
        # Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)
        r"""Mozilla/5.0\s\(Macintosh;\sIntel\sMac\sOS\sX\s10_12_6\)""",
        "Safari/Mactel/Sierra/Webkit (bad)",
    ),
    (
        # Safari/20619.2.8.11.12 CFNetwork/1568.200.51 Darwin/24.1.0
        r"""
        Safari/\d+(.\d+)+
        \s
        CFNetwork/\d+(.\d+)+
        \s
        Darwin/\d+(.\d+)+
        """,
        "Safari/MacOS/Webkit",
    ),
    (
        r"""Mozilla/5.0
            \s
            \(Macintosh;\sIntel\sMac\sOS\sX\s10(_\d+)+\)
            \s
            AppleWebKit/605.1.15
            \s
            \(KHTML,\slike\sGecko\)
            \s
            Version/\d+(.\d+)+
            \s
            Safari/\d+(.\d+)+""",
        "Safari/Mactel/Webkit",
    ),
    (
        r"""serpstatbot/2.1
            \s
            \(advanced\sbacklink\stracking\sbot;
            \s
            https://serpstatbot.com/;
            \s
            abuse@serpstatbot.com\)""",
        "Serpstatbot",
    ),
    (
        r"""Mozilla/5.0
            \s
            \(iPhone;\sCPU\siPhone\sOS\s17_3_1\slike\sMac\sOS\sX\)
            \s
            AppleWebKit/605.1.15
            \s
            \(KHTML,\slike\sGecko\)
            \s
            Version/17.3.1\sMobile/15E148\sSnapchat/12.92.0.46
            \s
            \(like\sSafari/8617.2.4.10.8,\spanda\)""",
        "Snapchat/iOS/Webkit/iPhone",
    ),
    (
        # Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36
        # (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0
        # Mobile Safari/537.36
        r"""
            Mozilla/5.0
            \s
            \(Linux;\sAndroid\s10;\sK\)
            \s
            AppleWebKit/537.36
            \s
            \(KHTML,\slike\sGecko\)
            \s
            SamsungBrowser""",
        "Samsung/Android/WebKit",
    ),
    (
        # Mozilla/5.0 (compatible)
        # SemanticScholarBot (+https://www.semanticscholar.org/crawler)
        r"""
            Mozilla/5.0
            \s
            \(compatible\)
            \s
            SemanticScholarBot
            \s
            \(\+https://www.semanticscholar.org/crawler\)
        """,
        "SemanticScholarBot",
    ),
    (
        # Mozilla/5.0
        # (compatible; SemrushBot/7~bl; +http://www.semrush.com/bot.html)
        r"""
            Mozilla/5.0
            \s
            \(compatible;
            \s
            SemrushBot/7~bl;
            \s
            \+http://www.semrush.com/bot.html\)
        """,
        "SemrushBot",
    ),
    (
        # Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)
        # LinkCheck by Siteimprove.com
        r"""
            Mozilla/5.0
            \s
            \(compatible;\sMSIE\s10.0;\sWindows\sNT\s6.1;\sTrident/6.0\)
            \s
            LinkCheck\sby\sSiteimprove.com
        """,
        "Siteimprove",
    ),
    (
        # trafilatura/1.10.0 (+https://github.com/adbar/trafilatura)
        r"""
            trafilatura/1.1\d.\d
            \s
            \(\+https://github.com/adbar/trafilatura\)
        """,
        "trafilatura/1.x.y",
    ),
    (
        # Unpaywall (http://unpaywall.org/; mailto:team@impactstory.org)
        r"""
            Unpaywall
            \s
            \(http://unpaywall.org/;\smailto:team@impactstory.org\)
        """,
        "Unpaywall",
    ),
    (
        # Mozilla/5.0
        # (Linux; Android 12; vivo 1920)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Version/4.0
        # Chrome/87.0.4280.141
        # Mobile Safari/537.36
        # VivoBrowser/13.2.3.0
        r"""
        Mozilla/5.0
        \s
        \(Linux;\sAndroid\s\d+;\svivo\s\d+\)
        \s
        AppleWebKit/\d+(.\d+)+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Version/\d+(.\d+)+
        \s
        Chrome/\d+.\d+.\d+.\d+
        \s
        Mobile\sSafari/\d+.\d+
        \s
        VivoBrowser/\d+.\d+.\d+.\d+
        """,
        "Vivo/Android/Blink",
    ),
    (
        # Mozilla/5.0
        # (Linux; U; Android 7.1; HUAWEI MT7-TL10 Build/HuaweiMT7-TL10; wv)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Version/4.0
        # Chrome/95.0.4638.74
        # Mobile Safari/537.36
        # OPR/84.0.2254.73823
        r"""
        Mozilla/5.0
        \s
        \(
            Linux;
            \s
            U;
            \s
            Android\s\d+(.\d+)?;
            \s
            HUAWEI\sMT7-TL10
            \s
            Build/HuaweiMT7-TL10;
            \s
            wv
        \)
        \s
        AppleWebKit/\d+.\d+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Version/\d.\d
        \s
        Chrome/\d+.\d+.\d+.\d+
        \s
        Mobile\sSafari/\d+.\d+
        \d
        OPR/\d+.\d+.\d+.\d+
        """,
        "Webview/Android/Blink",
    ),
    (
        # Mozilla/5.0 (Linux; Android 10; LIO-AN00 Build/HUAWEILIO-AN00; wv)
        # MicroMessenger Weixin QQ AppleWebKit/537.36 (KHTML, like Gecko)
        # Version/4.0 Chrome/78.0.3904.62 XWEB/2692 MMWEBSDK/200901
        # Mobile Safari/537.36
        r"""
            Mozilla/5.0
            \s
            \(Linux;\sAndroid\s10;\sLIO-AN00\sBuild/HUAWEILIO-AN00;\swv\)
            \s
            MicroMessenger\sWeixin\sQQ\sAppleWebKit/537.36
            \s
            \(KHTML,\slike\sGecko\)
            \s
            Version/4.0\sChrome/78.0.3904.62\sXWEB/2692\sMMWEBSDK/200901
            \s
            Mobile\sSafari/537.36""",
        "Webview/Android/WebKit",
    ),
    (
        # Mozilla/5.0
        # (compatible; wpbot/1.1; +https://forms.gle/ajBaxygz9jSR8p8G9)
        r"""
            Mozilla/5.0
            \s
            \(compatible;\swpbot/1.1;\s\+https://forms.gle/ajBaxygz9jSR8p8G9\)
        """,
        "WPBOT",
    ),
    (
        # Mozilla/5.0
        # (Windows NT 10.0; Win64; x64)
        # AppleWebKit/537.36
        # (KHTML, like Gecko)
        # Chrome/126.0.0.0
        # YaBrowser/24.7.0.0
        # Safari/537.36
        r"""
        Mozilla/5.0
        \s
        \(Windows\sNT\s10.0;\sWin64;\sx64\)
        \s
        AppleWebKit/\d{3}(.\d+)+
        \s
        \(KHTML,\slike\sGecko\)
        \s
        Chrome/\d+.\d+.\d+.\d+
        \s
        YaBrowser\/\d+.\d+.\d+.\d+
        \s
        Safari/\d{3}.(\d+)+""",
        "Yandex/Win10/Blink",
    ),
    (
        # Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)
        r"""
            Mozilla/5.0
            \s
            \(compatible;\sYandexBot/3.0;\s\+http://yandex.com/bots\)
        """,
        "YandexBot",
    ),
    (
        # Mozilla/5.0 (compatible; YandexImages/3.0; +http://yandex.com/bots)
        r"""
        Mozilla/5.0
        \s
        \(compatible;\sYandexImages/\d.\d;\s\+http://yandex.com/bots\)
        """,
        "YandexImages",
    ),
]


UA_REGEX_REPLACE = {
    re.compile(pair[0], re.VERBOSE): pair[1] for pair in _ua_pairs
}
