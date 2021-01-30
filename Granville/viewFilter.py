# Flow Filter Code from https://docs.mitmproxy.org/stable/addons-examples/#example-simplefilter_flowspy
# adapt so we use View filter - https://github.com/mitmproxy/mitmproxy/blob/master/mitmproxy/addons/view.py

# https://github.com/mitmproxy/mitmproxy/issues/237
# only used if view-filter addon disabled

"""
### USE BELOW CODE SNIPPET IF THIS ADDON IS NOT BEING IMPORTED INTO GRANVILLE ###

view = ctx.master.addons.get("view")
MAX_STORE_COUNT = 50 # We don't want console to explode with flows, set max to 50 and code below clears flows

# Only use when running without addons (view-filter)
def clearFlows():

    # Use the below code to clear the flows every 50
    if view.store_count() >= MAX_STORE_COUNT:
        
        view.clear() # Same as hitting 'z' on console to clear

"""

from mitmproxy import flowfilter, ctx, options

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