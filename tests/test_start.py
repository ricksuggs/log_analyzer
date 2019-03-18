from app import start


def test_parse_line():
    parsed_line = start.parse_line(
        '208.115.111.72 - - [16/Mar/2019:16:16:40 +0000] "GET /robots.txt HTTP/1.1" 200 - "-" "Mozilla/5.0 (compatible; Ezooms/1.0; help@moz.com)"'
    )

    assert parsed_line

    parsed_line = start.parse_line(
        '46.105.14.53 - - [16/Mar/2019:16:49:31 +0000] "GET /blog/tags/puppet?flav=rss20 HTTP/1.1" 200 14872 "-" "UniversalFeedParser/4.2-pre-314-svn +http://feedparser.org/"'
    )

    assert parsed_line

    parsed_line = start.parse_line(
        '127.0.0.1 - james [09/May/2018:16:00:39 +0000] "GET /report HTTP/1.0" 200 123'
    )

    assert parsed_line
