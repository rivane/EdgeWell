import re
from datetime import datetime



def extract_num(value):
    match_obj = re.match('.*?(\d+).*',value)
    if match_obj:
        num = int(match_obj.group(1))
    else:
        num = 0
    return num





if __name__ == '__main__':
    num = extract_num('adf123dsf')
    s = datetime.now().date()
    print(s)
