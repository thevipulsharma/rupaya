def parse_num(raw_num):
    return raw_num.replace(",", "")

def extract_num(raw_num):
    return float(parse_num(raw_num))

def get_doubling_rate(num_years):
    return 72/num_years