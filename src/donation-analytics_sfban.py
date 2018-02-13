
import numpy as np
from collections import defaultdict
from collections import namedtuple
import sys
import re
import datetime

# check if record is valid:

def valid_record(donor):
    
    # check OTHER_ID IS EMPTY
    if donor.OTHER_ID: return False
    
    #If TRANSACTION_DT is an invalid date (e.g., empty, malformed)
    mm, dd, yy = donor.TRANSACTION_DT[:2], donor.TRANSACTION_DT[2:4], donor.TRANSACTION_DT[-4:]
    try: 
        datetime.datetime(year=int(yy),month=int(mm),day=int(dd))
    except ValueError:
        return False
    
    #If ZIP_CODE is an invalid zip code (i.e., empty, fewer than five digits/characters)
    if len(donor.ZIP_CODE) < 5 or (not donor.ZIP_CODE.isalnum()): return False
    
    #If the NAME is an invalid name (e.g., empty, malformed)
    # check if characters are in alphabet
    name_list = re.split(r'[-,.\s]\s*', donor.NAME.rstrip('.'))
    if len(name_list) < 0: return False
    
    for n in name_list:
        if not n.strip().isalpha(): return False
            
    #If any lines in the input file contains empty cells in the CMTE_ID or TRANSACTION_AMT fields
    if not (donor.CMTE_ID and donor.TRANSACTION_AMT): return False
    
    # if TRANSACTION_AMT IS NEGATIVE OR ZERO: 
    if float(donor.TRANSACTION_AMT) <= 0: return False

    return True


def gen_records(input_file):
    
    Donor = namedtuple('donor', ['CMTE_ID', 'NAME', 'ZIP_CODE', 'TRANSACTION_DT', 'TRANSACTION_AMT', 'OTHER_ID'])
    
    with open(input_file, 'r') as file:
        
        for line in file:
            
            record = line.split('|')
            #print (record)         
            
            # need to check these in function valid_record
            CMTE_ID = record[0]
            NAME = record[7]
            ZIP_CODE = record[10][:5]
            TRANSACTION_DT = record[13]
            TRANSACTION_AMT = record[14]  
            OTHER_ID = record[15]
            
            donor = Donor(CMTE_ID, NAME, ZIP_CODE, TRANSACTION_DT, TRANSACTION_AMT, OTHER_ID)
            
              # determine if want to keep the record        
            if not valid_record(donor):
                continue
            
            #print donor
            
            yield donor
                


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def gen_map(donors, percent):
    
    donor_year = defaultdict(int)    
    recipient  = defaultdict(list)
    
    for donor in donors:

        year=int(donor.TRANSACTION_DT[-4:])
        
        donor_id = donor.NAME + '_' + donor.ZIP_CODE
        recip_id = donor.CMTE_ID + '_' + donor.ZIP_CODE + '_' + str(year)
        
        # store the earliest year a donor donated.        
        
        if donor_year[donor_id] >= year or donor_year[donor_id]==0:
            donor_year[donor_id] = year
            continue
        
        # if it is repeat donor: yes - run quantile, etc and write to file 
        
        recipient[recip_id].append(num(donor.TRANSACTION_AMT))
        
        percent_amt = np.percentile(recipient[recip_id], percent, interpolation='nearest')
        percent_amt = int(round(percent_amt+1e-16))
        
        total_amt   = np.sum(recipient[recip_id])
        if isinstance(total_amt, float): 
            total_amt = "{:.2f}".format(total_amt)
        num_repeat  = len(recipient[recip_id])
        
        yield '|'.join([donor.CMTE_ID, donor.ZIP_CODE, str(year), str(percent_amt), str(total_amt), str(num_repeat)])
    


def output_record(mapped_result, output_file):
    
    with open(output_file, 'w') as f:
        
        for m in mapped_result:
            
#            print (m)
            f.write(m+'\n')
    
def read_percent(filename):
    
    with open(filename) as f:
        return int(f.readline())


def main():

    input_file, percent_file, output_file = sys.argv[1:] 
    
    # read the percentile in file percentile.txt
    percent = read_percent(percent_file)
    #print ('percent = {}'.format(percent))
    
    # generator 1 for records
    records = gen_records(input_file)

    # generator 2 to emit desired output 
    result = gen_map(records, percent)

    # print out
    output_record(result, output_file)

if __name__ == "__main__":
    main()
