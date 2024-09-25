#init list of names
names_list=['Frank Harrelson', 'Bob Charles', 'Bob Franklin', 'Bob Brody', 'Frank Charles', 'Bob Harrelson', \
'Mack Dobson', 'John Jones', 'Rob Franklin', 'Tom Simpson', 'Rob Harrelson', 'John Brody', \
'Frank Jones', 'John Harrelson','Frank Charles', 'Tom Charles', 'Frank Franklin', 'Frank Charles', \
'John Charles', 'John Franklin', 'Frank Dobson', 'Diane Jones', 'Bob Dobson', 'Tom Harrelson', \
'Rob Simpson', 'Tom Brody', 'Rob Harrelson', 'John Charles', 'Bob Dobson', 'Bob Brody']
#creates index values to create lists
LETTER_INDEX = 1
SPACE_INDEX = 2
#sort the names using lambda, split at the space in the middle then sort alphabetically using python sort method by last name
names_list = sorted(names_list, key=lambda x:( x.split(" ")[-1]))
print(names_list)

#blank list to add usernames to
#list for the first 5 values in last name
last_username_list = []
#list for first 2 values in first name
first_username_list = []

#create usernames by last 5 characters in last name and first 2 from first name
for index, name in enumerate(names_list):

    #creates separate list of the name, sorted, with a split value at the space in the middle
    temp_name = list(map((lambda x: x.split(" ")[-1]), name))
    #creates a list of values using letter_index and space_index in order to find where first name and last name split, used to add values to the username_lists
    space_list = list(map((lambda x: SPACE_INDEX if x == '' else LETTER_INDEX), temp_name))

    #for each value in space index list, adds to the username_list based on what the index value is
    for index, value in enumerate(space_list):
        if value != 1:
            #appends the first 2 letters from the first name
            first_two = temp_name[0:2]
            first_username_list.append(first_two)
            #finds the first 5 of the last name
            last_five = temp_name[index+1:index+6]
            last_username_list.append(last_five)
            break

compressed_first_list = []
compressed_last_list = []
usernames = []

#joins the values in the last and first username lists in order to create 2 lists of each value
for value in last_username_list:
    temp = "".join(value)
    compressed_last_list.append(temp)
for value in first_username_list:
    temp = "".join(value)
    compressed_first_list.append(temp)

#for each value in last names, add the first 2 of the first names
for index, value in enumerate(compressed_last_list):
    temp = compressed_first_list[index] + value
    usernames.append(temp)
    
print(usernames)
