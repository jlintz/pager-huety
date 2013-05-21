Pager-Huety
===============================
A script to trigger Philip Hue lightbulbs based on triggered incidents from PageDuty.

Dependencies
------------
 * requests (http://python-requests.org)
 * phue (https://github.com/studioimaginaire/phue) (bundled)

Usage
-----
    -h, --help            show this help message and exit
    --pd-api-key PD_API_KEY
                        API Key for pager duty
    --company COMPANY     Company name used with Pager Duty (for API requests)
    --hue-host HUE_HOST   Hostname of your Philips Hue Bridge
    --lamp LAMP           Hostname of your Philips Hue Bridge
    --night-only NIGHT_ONLY
                        Will only flash lights between 9PM - 7AM
    --user-filter USER_FILTER
                        Only trigger lights if incident is assigned to one of
                        these user ids
    --log-level LOG_LEVEL
                        Set logging level

Example
-----
    ./pager-huety.py --pd-api-key=asdfgh --company=chartbeat --hue-host=Philips-hue.home
