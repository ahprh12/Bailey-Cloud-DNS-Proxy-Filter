# ********** ap27 6.24.2020 **********
# Granville will filter all outgoing requests
# based on keywords
# log the request and eventually mail a report
# based on https://docs.mitmproxy.org/stable/addons-scripting/
# ************************************

from mitmproxy import ctx
from mitmproxy import http
import logging
import os

# initiate logging
my_path = os.path.abspath(os.path.dirname(__file__))
alertlog = os.path.join(my_path, './logs/alert.log')
logging.basicConfig(filename=alertlog, format='%(asctime)s : %(message)s', level=logging.INFO)

# https://github.com/mitmproxy/mitmproxy/issues/237
# We don't want console to explode with flows, set max to 50 and code below clears flows
view = ctx.master.addons.get("view")
MAX_STORE_COUNT = 50

# filtering is done here - log and send artificial response back
# -> None means this function returns nothing (perhaps similar to void in Java)
def request(flow: http.HTTPFlow) -> None:

	# calls function below
	clearFlows()
	
	if "jenna" in flow.request.pretty_url:

		logging.info(str(flow.request.pretty_url))
		#flow.request.host = "0.0.0.0"
		#flow.kill()
		# This sends a reply from the proxy immediately
		flow.response = http.HTTPResponse.make(200,b"stop, not so fast yall...",{"Content-Type": "text/html"})

def clearFlows():

	# Use the below code to clear the flows every 50
	if view.store_count() >= MAX_STORE_COUNT:
		
		view.clear() # Same as hitting 'z' on console to clear