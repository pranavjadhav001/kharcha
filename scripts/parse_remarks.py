

bank_keywords = ['bank','hdfc','icici','axis','yes']

def check_bank_keywords(string):
    substr = string.split(' ')
    for j in substr:
        if j.lower() in bank_keywords:
            return True
    return False

def hdfc_remark_parse(remark,sep='-',joiner='|'):
    all_str = []
    #if single text remark
    if not sep in remark:
        return remark
    subremark_list = remark.split(sep)
    #check if UPI or not
    if subremark_list[0] == "UPI":
        #remove numeric strings
        #remove strings containing @
        for substring in subremark_list[1:-3]:
            if not (substring.isnumeric()\
               or '@' in substring):
                all_str.append(substring)
        all_str.append(subremark_list[-1])
    else:
        #for other transcation types
        for substring in subremark_list:
            #only remove numeric strings
            if not substring.isnumeric():
                all_str.append(substring)
    return joiner.join(all_str) 

def icici_remark_parse(remark,sep='/',joiner=' '):
    #some transcations dont have /
    if sep not in remark:
        return remark
    subremark_list = remark.split(sep)
    all_str = []
    #check if transcation is upi or not
    if subremark_list[0].lower() == 'upi':
        #dont consider substring if all digits
        #or if bank names are present
        for substring in subremark_list[1:-1]:
            if not(substring.isnumeric() or \
               check_bank_keywords(substring)):
                all_str.append(substring)
    else:
        # if other transcation only remove all
        # digit substring
        for substring in subremark_list:
            if not(substring.isnumeric()):
                all_str.append(substring)
    return joiner.join(all_str)
