# ********** ap27 7.13.2020 **********
# Granville will filter all outgoing requests
# based on keywords
# log the request and eventually mail a report
# with TLS Passthrough Logic
# based on https://docs.mitmproxy.org/stable/addons-scripting/
# and https://github.com/mitmproxy/mitmproxy/issues/3306
# and source code https://github.com/mitmproxy/mitmproxy/blob/e92b957e3a7324d79f2ef2a7386ed21549a5cb10/test/mitmproxy/proxy/test_config.py
# ************************************

import logging
import os
import collections
import random
from enum import Enum
import mitmproxy
from mitmproxy import ctx, http, options, flowfilter
from mitmproxy.exceptions import TlsProtocolException
from mitmproxy.proxy.protocol import TlsLayer, RawTCPLayer
from typing import Sequence
import threading

def f(f_stop):
    # do something here ...
    if not f_stop.is_set():
        # call f() again in 60 seconds
        mitmproxy.ctx.log("STARTING TIMER")
        threading.Timer(5, f, [f_stop]).start()

f_stop = threading.Event()
# start calling f now and every 60 sec thereafter
f(f_stop)


# *** TLS Passthrough Code Found here: https://github.com/mitmproxy/mitmproxy/blob/ed68e0a1ba090eca5f8b841a9d06303d2b5862f3/examples/contrib/tls_passthrough.py
class InterceptionResult(Enum):
    success = True
    failure = False
    skipped = None


class _TlsStrategy:
    """
    Abstract base class for interception strategies.
    """

    def __init__(self):
        # A server_address -> interception results mapping
        self.history = collections.defaultdict(lambda: collections.deque(maxlen=200))

    def should_intercept(self, server_address):
        """
        Returns:
            True, if we should attempt to intercept the connection.
            False, if we want to employ pass-through instead.
        """
        raise NotImplementedError()

    def record_success(self, server_address):
        self.history[server_address].append(InterceptionResult.success)

    def record_failure(self, server_address):
        self.history[server_address].append(InterceptionResult.failure)

    def record_skipped(self, server_address):
        self.history[server_address].append(InterceptionResult.skipped)


class ConservativeStrategy(_TlsStrategy):
    """
    Conservative Interception Strategy - only intercept if there haven't been any failed attempts
    in the history.
    """

    def should_intercept(self, server_address):
        if InterceptionResult.failure in self.history[server_address]:
            return False
        return True


class ProbabilisticStrategy(_TlsStrategy):
    """
    Fixed probability that we intercept a given connection.
    """

    def __init__(self, p):
        self.p = p
        super(ProbabilisticStrategy, self).__init__()

    def should_intercept(self, server_address):
        return random.uniform(0, 1) < self.p


class TlsFeedback(TlsLayer):
    """
    Monkey-patch _establish_tls_with_client to get feedback if TLS could be established
    successfully on the client connection (which may fail due to cert pinning).
    """

    def _establish_tls_with_client(self):
        server_address = self.server_conn.address

        try:
            super(TlsFeedback, self)._establish_tls_with_client()
        except TlsProtocolException as e:
            tls_strategy.record_failure(server_address)
            raise e
        else:
            tls_strategy.record_success(server_address)


# inline script hooks below.

tls_strategy = None

# and look here https://github.com/mitmproxy/mitmproxy/blob/902ef59d01f45613ce33520159e157697bcc6f9f/mitmproxy/options.py
def load(l):
    l.add_option(
        "tlsstrat", int, 0, "TLS passthrough strategy (0-100)",
    )

    l.add_option("ignore_hosts", Sequence[str], ['^(?![0-9\\.]+:)(?!([^\\.:]+\\.)*google\\.com:)(?!([^\\.:]+\\.)*youtube\\.com:)'], 'Ignore host and forward all traffic without processing it.')
    


def configure(updated):
    global tls_strategy
    if ctx.options.tlsstrat > 0:
        tls_strategy = ProbabilisticStrategy(float(ctx.options.tlsstrat) / 100.0)
    else:
        tls_strategy = ConservativeStrategy()


def next_layer(next_layer):
    """
    This hook does the actual magic - if the next layer is planned to be a TLS layer,
    we check if we want to enter pass-through mode instead.
    """
    if isinstance(next_layer, TlsLayer) and next_layer._client_tls:
        server_address = next_layer.server_conn.address

        if tls_strategy.should_intercept(server_address):
            # We try to intercept.
            # Monkey-Patch the layer to get feedback from the TLSLayer if interception worked.
            next_layer.__class__ = TlsFeedback
        else:
            # We don't intercept - reply with a pass-through layer and add a "skipped" entry.
            mitmproxy.ctx.log("TLS passthrough for %s" % repr(next_layer.server_conn.address), "info")
            next_layer_replacement = RawTCPLayer(next_layer.ctx, ignore=True)
            next_layer.reply.send(next_layer_replacement)
            tls_strategy.record_skipped(server_address)

# *** End TLS Passthrough Logic ***

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~ Granville ~~~ Traffic Interception Logic (only intercepting google and youtube domain - add others as necessary)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
    #flow.request.query["mitmproxy"] = "rocks"

    if "jenna" in flow.request.pretty_url:

        logging.info(str(flow.request.pretty_url))
        flow.response = http.HTTPResponse.make(451)

def clearFlows():

    # Use the below code to clear the flows every 50
    if view.store_count() >= MAX_STORE_COUNT:
        
        view.clear() # Same as hitting 'z' on console to clear

# Flow Filter Code from https://docs.mitmproxy.org/stable/addons-examples/#example-simplefilter_flowspy
# adapt so we use View filter - https://github.com/mitmproxy/mitmproxy/blob/master/mitmproxy/addons/view.py
class Filter:

    def __init__(self):

        self.filter = flowfilter.parse("~http | ~tcp")

    def configure(self, updated):

        self.filter = flowfilter.parse(ctx.options.view_filter)

    def load(self, l):

        l.add_option(
            "view_filter", str, "~u google\\.com/search | ~u youtube.com/results", "Limit the view to matching flows."
        )

addons = [Filter()]