import os

def table_map_read( table_map_file ):
    "function to read tomogram table map file which relates tomogram id to reconstruction path in dynamo"
    if type(table_map_file) == str and os.path.isfile(table_map_file):
        with open(table_map_file,'r') as file:
            # read file line by line into list
            data = file.readlines()
            
            # remove newlines, split strings, convert keys/values to tuples and insert info into dictionary
            entry_idx = 0
            data_out = []
            while entry_idx < len(data):
                data[entry_idx] = data[entry_idx].replace('\n','')
                data[entry_idx] = data[entry_idx].split()
                try:
                    data_out.append((int(data[entry_idx][0]), data[entry_idx][1]))
                except:
                    print("Couldn't split entry in table map file, probably due to empty line...")
                finally:
                    entry_idx += 1
            data_out = dict(data_out)
        return data_out
        
    else:
        print("Error reading table map file '{}'".format(table_map_file))
        

