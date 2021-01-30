# Credit Reference: https://github.com/mitmproxy/mitmproxy/issues/3306
from mitmproxy import ctx, http, options, exceptions, proxy
from mitmproxy.tools.dump import DumpMaster

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

class Granville:

    def request(self, flow):
        
        # calls function below
        clearFlows()
        
        if "jenna" in flow.request.pretty_url:

            logging.info(str(flow.request.pretty_url))
            flow.response = http.HTTPResponse.make(200,b"stop, not so fast yall...",{"Content-Type": "text/html"})

    def clearFlows():

        # Use the below code to clear the flows every 50
        if view.store_count() >= MAX_STORE_COUNT:
            
            view.clear() # Same as hitting 'z' on console to clear

def start():

    myaddon = Granville()
    opts = options.Options(ignore_hosts='^(?![0-9\\.]+:)(?!([^\\.:]+\\.)*google\\.com:)')
    pconf = proxy.config.ProxyConfig(opts)
    m = DumpMaster(opts)
    m.server = proxy.server.ProxyServer(pconf)
    m.addons.add(myaddon)

    try:
        m.run()
    except KeyboardInterrupt:
        m.shutdown()

start()
