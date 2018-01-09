#!/user/bin/env python
# -*- coding: utf-8 -*-
import re

def extract_num(value):
    num = 0
    match_obj = re.match('.*?(\d+).*',value)
    if match_obj:
        num = match_obj.group(1)
    return num