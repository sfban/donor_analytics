### This is the report of Insight DataEngineer Code Challenge by Shufang Ban.

The code was written in Python, version 3.6.0.

Following modules were used
   1) numpy 1.11.3
   2) collections (defaultdict and namedtuple)
   3) sys
   4) re
   5) datetime
   
When the input data is huge or streaming in, generator is a good way to implement processing pipelines (fast, less memory and space).
Using generator, the code could read-in and process the donation records one by one (function gen-records). 
For each record, the code first identifies if it is valid (function valid_record).
If it is a valid record, the code begina to process (function gen_map).
First it builds a map to save the donor informaton (donor name and zip code) as key, and saves the earliest donation calender year as value(int type).
This map can be used to identify the repeat donor.
When a repeat donor is found, it is saved to the second map.
In the second map, recipient, zip code, and calendar year are combined as key, the donation amount is saved as value(list type).
The value (list) of this map can be used to calculate the donation percentile, sum and the donator number.
After one repeat donor is found and the reqired values are calculated, genrator yeild is used at the end of function gen_map. 
For each repeat donor record, the code output(function output_record).

There are 7 functions intotal, including the main function. I will explain them one by one in the following.
 

### 1. function valid_record

   This function is to identify if the record is valid. 
   Input is a named tuple called donor; Output is logical Ture or False.
   
   There are six variables need to be checked, as discussed in the code challenge README.
   1) CMTE_ID: identifies the flier, which for our purposes is the recipient of this contribution
   2) NAME: name of the donor
   3) ZIP_CODE: zip code of the contributor (we only want the first five digits/characters)
   4) TRANSACTION_DT: date of the transaction
   5) TRANSACTION_AMT: amount of the transaction
   6) OTHER_ID: a field that denotes whether contribution came from a person or an entity. 
   
   For "OTHER_ID", as described in the code challenge README we only want records that have the field, OTHER_ID, set to empty. If the OTHER_ID field contains any other value, it was considered to be invalid.
   
   For "ZIP_CODE", the data dictionary has the ZIP_CODE occupying nine characters, for the purposes of the challenge, we only consider the first five characters of the field as the zip code. it will be considered invalid if it is empty or fewer than five digits. I was thinking to limit the ZIP_CODE only to be digits, but in th code challenge readme, "we only want the first five gidits/characters", whih means it is possible to be characters. So I did not impose the limit.
   
   For "TRANSACTION_DT",  it will be consider invalid if it is empty or malformed. In the code, first I copied and saved year, month, and day, then I use the python module "datetime" to identify its validity. 
   
   For "TRANSACTION_AMT", it should be numarical type and should be positive number. It will be invalid if it is empty, or zero, or negative.
   
   For "CMTE_ID", it will be invalid if it is empty.
   
   For "NAME", it is the most complicated variable to identify. I searched the "Naming in the United States" on wikipedia. It says a few restrictions do exist, but vary by state. Some states ban the use of numerical digits or pictogrames. A few states ban the use of obscenity. There are also a few states, Kentucky for instance, that have no naming laws whatsoever. There are also Spanish or German names, which are with diacritical marks or accents. For this code, I simply limited the name to be 26 alphabetical characters of English language, and there could be space, '-', '.', or ',' inside the names. The 're' module is used to split the parts of name and each part is checked separately if it is alphabet. 


### 2. function gen_records

   This function uses the genertor to process donation records one by one.
   Input is the input file; Output is the valid records by generator via yield. 
   
   First we define a namedtuple class to save the six variables for each records. 
   It is read-only, faster than list, and more readable.
   Then, I use the function valid_record to identify if the record is valid. 
   If it is not valid, skip it and read-in the next record. 
   If it is valid, yield for next step (goes to function gen_map) 
    
### 3. function num

   This function is to change the variable type from string to numarical type int or float.
   Input is a string type of a donation amount; Output is a numerical type(int or float) of the donation amount.
   
   This function will be called in function gen_map. 
   It is used for donation amount variable "TRANSACTION_AMT", the type is NUMBER(14,2) as described on FEC website. 
   As shown in the example, most of the donation amount is a integer type. 
   When the code read-in the donation record, it is a string type. 
   The code changes the type to int if the donation amount is integer and changes the type to float if the donation amount is decimal number.

### 4. function gen_map
   
   This function identifies repeat donors, calculate three values (donation amount percentile, donation amount sum, and donor nubmer) for contributions coming from repeat donors for each recipient, zip code and calendar year.
   Input is the valid donation records from function gen_records and percent value; Output is a output record by generator via yield.
   
   Define two defalut dictionaries(maps). 
   The first one, donor_year, with int type value (to save calender year).
   The second one, recipient, with list type value (to save donation amounts) 
   
   For each valid record, 
   define the year = the last 4 digits of "TRANSACTION_DT". 
   define the donor_id = donor names + zip code (first five digits) as the key of the first map. 
   define the recip_id = recipient + zip code + calender year as the key of the second map. 
   
   We put the year as the key value of the first map (the default value is 0 before we put in any value). 
   As described in the code challenge readme, for the same donor_id,  if a donor had previously contributed to any recipient listed in the itcont.txt file in any prior calendar year, that donor is considered a repeat donor. But the data is not necessarily in order, we may find a smaller year later. If we find a smaller year after the first value, he/she will not be consider a repeat donor; if we find a bigger year, this will be a repeat donor record. 
   So if we find the year== 0 or the new value of year is smaller than the corrent year, we update the year value and skip to next record(i.e., we save the smallest year we can found from the recoder for this map). If we found a bigger year, this record will be repeat donor. 
   
   For any repeat doner, recip_id as key of second map, the numerical donation amount "TRANSACTION_AMT"(called function num) as value for second map (list type, can hold more than one amount).
   The Numpy function percentile is used to calculate the requied percentile, chosing 'nearest' method and round to integer.
   The Numpy function sum is used to calculate the total amount.
   The number of repeat donor is calculated by the lenth of list.
   
   After one repeat donor is found and the reqired values are calculated, genrator yeild is used for next step (goes to function output_record)

### 5. function output_record

   This function takes in the desired output record (in generator) from function gen_map, and write the desired repeat donor information to the output file.

### 6. function read_percent

   This function reads the percentile.txt file and returns the percentile number.

### 7. function main

   Main function takes in the arguments from commdand lines, calls the functions read_percent, gen_records, gen_map, output_record.


   
### My Test cases

   1) 1st record: invalid CMTE_ID (empty)
   2) 2nd record: invalid NAME (digit)
   3) 3rd record: invalid ZIP_CODE (fever than 5)
   4) 4th record: invalid TRANSACTION_DT (02302018)
   5) 5th record: invalid TRANSACTION_AMT (-300)
   6) 6th record: invalid OTHER_ID (not empty)
   7) 7~9th record: calender years in order of 2016 2015 2017, other informations are same
   8) 10-11th record: donor and repeat donor with interger donation amount
   9) 12-13th record: donor and repear donor(different name from 10th record) with float donation amount(same recipient, zip code and calender year as 10th)
   10) 14-15th record: donor and repear donor(different name from 10th record) with int donation amount(same recipient and zip code, different calender year)
   11) 16-17th record: donor and repear donor(different name from 10th record) with int donation amount(same recipient and calender year, different zip code)
   12) 18th record:              repear donor of 14-15th record with int donation amount(same recipient, zip code and calender year as 10th)
   13) 19-20th record: donor and repear donor(different name from 10th record) with int donation amount(same recipient, zip code and calender year as 10th)
   14) 21-22th record: donor and repear donor(different name from 10th record) with int donation amount(same recipient, zip code and calender year as 10th)
   
   

