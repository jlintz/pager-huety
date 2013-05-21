#!/usr/bin/env python
# Author: Justin Lintz <jlintz@gmail.com>
#
# Module to control Philips Hue light bulbs
# based on Pager Duty alerts
#

import sys
import requests
import logging
from datetime import datetime
from argparse import ArgumentParser
from time import sleep
from requests.exceptions import RequestException
from phue import Bridge

logger = logging.getLogger('pager-huety')


def is_night_time(pm=21, am=7):
    """
    Simple function to determine if it's day or night
    """
    cur_hour = datetime.now().hour
    return cur_hour >= pm or cur_hour <= am


class PagerHuety(object):

    def __init__(self, api_key, company, hue_host):
        self.api_key = api_key
        self.company = company
        self.bridge = Bridge(hue_host)
        self._hue_host = hue_host

    def fetch_incidents(self, user_ids=None):
        """
        Grab latest triggered alerts from pager duty
        optionally filtered by user_ids

        Returns:
            JSON object
        """
        incidents_url = 'https://%s.pagerduty.com/api/v1/incidents' % self.company
        headers = {'Authorization': 'Token token=%s' % self.api_key}
        args = {'status': 'triggered'}

        if user_ids:
            args['assigned_to_user'] = user_ids

        logger.info('Fetching pager duty incidents')

        try:
            response = requests.get(incidents_url, data=args, headers=headers)
        except RequestException as e:
            logger.exception('Error connecting to PagerDuty: %s' % e)
            sys.exit(1)

        return response.json()

    def flash_light(self, light_id):
        """
        Flash light_id bulb red and blue 3x, then
        turn to bright white for 10 seconds and shut off
        """
        red = 65280
        blue = 46920

        logger.info('Flashing lights')
        logger.debug('Light ID: %d', light_id)
        logger.debug('Lights: %s', self.bridge.lights_by_id)

        self.bridge.get_light_objects()
        light = self.bridge.lights_by_id[light_id]
        # turn light on
        self.bridge.set_light(light_id, 'on', True)

        # blink red and blue
        for x in range(0, 2):
            light.hue = red
            sleep(1.5)
            light.hue = blue
            sleep(1.5)

        # set to bright white
        light.xy = [.2, .2]
        sleep(10)

        # turn light off
        self.bridge.set_light(light_id, 'on', False)

        return


def main():
    parser = ArgumentParser(
        description='Trigger your Philips Hue lights via a Page Duty alert')
    parser.add_argument('--pd-api-key', type=str, required=True,
                        help='API Key for pager duty')
    parser.add_argument('--company', type=str, required=True,
                        help='Company name used with Pager Duty (for API requests)')
    parser.add_argument('--hue-host', type=str, required=True,
                        help='Hostname of your Philips Hue Bridge')
    parser.add_argument('--lamp', type=int, default=3,
                        help='Hostname of your Philips Hue Bridge')
    parser.add_argument('--night-only', action='store_true', default=False,
                        help='Will only flash lights between 9PM - 7AM')
    parser.add_argument('--user-filter', type=str,
                        help='Only trigger lights if incident is assigned to one of these user ids')
    parser.add_argument('--test', action='store_true', default=False,
                        help='Test Pager Duty connection and Flash lights')
    parser.add_argument('--log-level', type=str, default='WARN',
                        help='Set logging level')

    args = parser.parse_args()

    # Configure log level
    log_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)
    phue_logger = logging.getLogger('phue')
    logger.setLevel(level=log_level)
    phue_logger.setLevel(level=log_level)

    if args.test:
        logger.info('Running in TEST mode')

    ph = PagerHuety(args.pd_api_key, args.company, args.hue_host)

    if not is_night_time() and args.night_only and not args.test:
        logger.info('Night time only mode set, not running')
        return

    incidents = ph.fetch_incidents(args.user_filter)

    if incidents['total'] != 0 or args.test:
        logger.info('Triggering lights')
        ph.flash_light(args.lamp)


if __name__ == '__main__':
    main()
