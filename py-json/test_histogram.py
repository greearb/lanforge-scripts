#!/usr/bin/env python3
""" ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
    internal test driving LFUtils.expand_endp_histogram
----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- """
from LANforge import LFUtils

distrib_load = {
    "histo_category_width" : 3,
    "histogram" : [
          221,
          113,
          266,
          615,
          16309,
          56853,
          7954,
          1894,
          29246,
          118,
          12,
          2,
          0,
          0,
          0,
          0
       ],
    "time window ms" : 300000,
    "window avg" : 210.285,
    "window max" : 228,
    "window min" : 193
}

if __name__ == '__main__':
    LFUtils.expand_endp_histogram(distrib_load)


