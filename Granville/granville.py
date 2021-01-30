"""
# ********** ap27 7.22.2020 **********
# Granville will filter all outgoing requests
# based on keywords
# log the request and eventually mail a report
# with TLS Passthrough Logic - Credit to below folks and mhils from mitmproxy in particular - Berkeley Genius
# based on https://docs.mitmproxy.org/stable/addons-scripting/
# and https://github.com/mitmproxy/mitmproxy/issues/3306
# and source code https://github.com/mitmproxy/mitmproxy/blob/e92b957e3a7324d79f2ef2a7386ed21549a5cb10/test/mitmproxy/proxy/test_config.py
# Notes: 
# filtering is done here - log and send http error responce code 451, blocked due to legal reasons
# an error code rarely seen, so we can easily tell that Granville is indeed working
# "def request(flow: http.HTTPFlow) -> None:" means this function returns nothing (perhaps similar to void in Java)
"""

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~ Granville ~~~ Traffic Interception Logic (only intercepting google and youtube domain - add others as necessary)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from passthroughWithIgnore import * # local script
from deathlist import death # keyword deathlist
import logging
import os

from enum import Enum
import mitmproxy
from mitmproxy import ctx, http, options
from mitmproxy.exceptions import TlsProtocolException
from mitmproxy.proxy.protocol import TlsLayer, RawTCPLayer
from viewFilter import * # local script addon

# Logging
my_path = os.path.abspath(os.path.dirname(__file__))
alertlog = os.path.join(my_path, './logs/alert.log')
date_strftime_format = '%m-%d-%Y %I:%M%p'
logging.basicConfig(filename=alertlog, format='%(asctime)s : %(message)s', datefmt= date_strftime_format, level=logging.INFO)

def request(flow: http.HTTPFlow) -> None:

	p_url = flow.request.pretty_url
	intercept = (p_url.startswith('https://www.google.com/search') or p_url.startswith('https://www.youtube.com/results'))

	if intercept:

		q = p_url[30:]

		if 'q' in flow.request.query: # 'oq' also valid key

			q = flow.request.query['q'].replace(' ', '')

		elif 'search_query' in flow.request.query:

			q = flow.request.query['search_query'].replace(' ', '')

		logging.info(q)

		for x in death:

			if x in q:

				logging.info('!!! DEATH KEY !!!: ' + x + ' found in ' + q)
				# flow.response = http.HTTPResponse.make(451) # Prod Response
				flow.response = http.HTTPResponse.make(200,x,{"Content-Type": "text/html"}) # for testing
				break