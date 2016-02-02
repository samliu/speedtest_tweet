#!/usr/bin/python
#
# Script to tweet when internet speeds fall below a threshold. You can set this
# up with a cron job every few minutes.
#
# */5 * * * * python speedtest.py
#
# See twitter_api_instructions folder for images showing how to get the consumer
# keys and tokens.

import os
import sys
import csv
import datetime
import time
import twitter
from settings import settings


def test_speed():
    # Run speedtest-cli.
    print 'Running speed test...'
    output = os.popen("speedtest-cli --simple").read()
    print 'Finished running speedtest-cli! Processing results...'

    # Split the 3-line result (ping, down, up).
    lines = output.split('\n')
    print output
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    # If speedtest could not connect, set speeds to 0.
    if "Cannot" in output:
        p = 100
        d = 0
        u = 0

    # Extract the values for ping down and up.
    else:
        p = str(lines[0][6:11])
        d = str(lines[1][10:14])
        u = str(lines[2][8:12])
    print date, p, d, u

    # Append the data to file for local network plotting.
    out_file = open('data.csv', 'a')
    writer = csv.writer(out_file)
    writer.writerow((ts * 1000, p, d, u))
    out_file.close()

    # Connect to twitter.
    my_auth = twitter.OAuth(settings.TOKEN, settings.TOKEN_SECRET,
                            settings.CONSUMER_KEY, settings.CONSUMER_SECRET)
    twit = twitter.Twitter(auth=my_auth)

    # Try to tweet if speedtest couldn't connect. Probably won't work if the
    # internet is down.
    if "Cannot" in output:
        try:
            tweet = ("Hey @Comcast @ComcastCares why is my internet down?" +
                     settings.EXPECTED_SPEED + "in" + settings.MY_LOCATION +
                     "??? #comcastoutage #comcast")
            twit.statuses.update(status=tweet)
        except:
            pass

    # Tweet if down speed is less than settings.
    elif float(d) < settings.DOWN_SPEED_MIN:
        print 'Attempting tweet...'
        try:
            d = str(int(round(float(d))))
            u = str(int(round(float(u))))
            tweet = ("Hey @Comcast @ComcastCares why is my internet slow?"
                     " Getting " + d + "/" + u +
                     " but paying for " + settings.EXPECTED_SPEED + " in " +
                     settings.MY_LOCATION + "??? #comcastoutage #comcast")
            twit.statuses.update(status=tweet)
        except Exception, e:
            print str(e)
            pass
    return

if __name__ == '__main__':
    test_speed()
    print 'Completed.'
