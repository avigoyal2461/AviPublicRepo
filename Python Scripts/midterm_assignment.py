import pandas as pd
import os
import random
import dataframe_image as dfi
from PIL import Image

#init random variables, and students to create a df table
data={
'Student_Name' : ['Tom', 'Joe', 'Pat', 'Avi', 'Tony', 'Mary', 'Henry', 'Bob', 'Ben', 'Jacob'],
'Grade_Recieved':[random.randint(0,100) for z in range(10)],
'Hours_Studied':[random.randint(0,5) for i in range(10)],
#this placeholder is to show an example of usecols below
'Random_Numbers' : [random.randint(0,20) for j in range(10)]
}

#placeholder value for my columns to avoid retyping later
cols = ['Student_Name', 'Grade_Recieved', 'Hours_Studied', 'Random_Numbers']
cols_less = ['Student_Name', 'Grade_Recieved', 'Hours_Studied']

#create a df, this will be used to create a csv file for demonstration
study_table = pd.DataFrame(data, columns = cols)
print(study_table)

#get the directory of the csv file i will be creating
directory = os.path.join(os.getcwd(), "hours_studied.csv")

# if the csv file already exists, delete it, this method is not really required, but this will ensure that there is no "spam" and ensures a single file only
#THIS IS NOT PART OF THE PANDAS METHODS, BUT A HELPER FOR ME TO KEEP EVERYTHING CLEAN
if os.path.exists(directory):
    print("Deleting Extra File...")
    os.remove(directory)

print("Creating CSV File...")
#creates a csv file holding the table i created above
study_table.to_csv("hours_studied.csv")

#creates a dataframe using pandas method to read a csv, using column designators in order to pull the specific columns i want to use.
#this example, i selected 3/4 of the columns, the placeholder was made to examplify this method
read_study_table = pd.read_csv(directory, usecols=cols_less)
print(read_study_table)

#get the sum of all of the grades
#this works by looking through the locator from pandas to find the column , Grade_Recieved, if the value is greater than -1, then it goes to
#the grade recieved column and adds each number together
total_grades = read_study_table.loc[((read_study_table["Grade_Recieved"] > -1)), "Grade_Recieved"].sum()

#find the total amount of hours studied, using the same method as above
total_hours_studied = read_study_table.loc[((read_study_table["Hours_Studied"] > -1)), "Hours_Studied"].sum()
#determine how many students are in the list, and recieve the names of each, also keeps a count of the amount of students seen in the table
student_counter = 0
student_list = []
for name in read_study_table.loc[((read_study_table['Student_Name'])) != "NaN", 'Student_Name']:
    if name != "NaN":
        student_counter +=1
        student_list.append(name)

#finds the average grade
average_grade = total_grades / student_counter
print(f"The average grade of all of the {student_counter}, with names: {student_list} is: {average_grade}, with a total of {total_hours_studied} hours studied.")

#creates another df that holds the random number col that i omitted in the previous step
#creates a temp list because the usecol method needs a list value.
temp = ['Random_Numbers']
study_table_random_numbers = pd.read_csv(directory, usecols=temp)
print(study_table_random_numbers)

#another method, this one combines tables, in this case for demonstration, the final product will be what i started with, without removing the extra cols
#the axis is required in order to keep the new values in the same line as the original, ex:

#without axis:
# 0 NAME, GRADE NaN
# NAN, NAN, NANE, RANDOM NUMBER

#with axis:
#0 NAME GRADE RANDOMNUMBER

final_df = pd.concat([read_study_table, study_table_random_numbers], axis = 1)
print(final_df)


#this method is good, but here i will also exemplify the use of pd merger, which does similar actions, but with a little more control
#first, i init all my tables, each will have the student name then another value, such as hours and grade
#these methods are not going to print because this was already shown in an example, the usecols ensures that these are the only columns being read
name_and_grade = {'Student_Name', 'Grade_Recieved'}
name_grade = pd.read_csv(directory, usecols=name_and_grade)

name_and_hours = {'Student_Name', 'Hours_Studied'}
name_hours = pd.read_csv(directory, usecols=name_and_hours)

#merge the tables on the student name, the name column will not be input a second time, but it will order each value based on the name,
#one possible merge style deliminator would be : how='left', but this does not ensure that the order of the columns will remain the same
merge_df = pd.merge(left=name_grade, right=name_hours, on='Student_Name', how='left')

#in order to ensure the order of the columns, this method is used to reorder the table using columns set before
merge_df = merge_df.reindex(columns=cols_less)
print(merge_df)

#create an image, this will use the pandas style method to add styling to the dataframe, then i will use dataframe image from another package in order to print an image to show the result
#first, set the values that will be used to find the directory of the picture, this is to export the final picture
#NOTE - the dataframe image will print in its own file and I will have to open this file in order to show the results, THIS METHOD STYLES USING PANDAS, BUT PRINTING MUST BE DONE THROUGH OTHER PACKAGES
file_name = "styled_df.png"
image_path = os.path.join(os.getcwd(), file_name)
if os.path.exists(image_path):
    os.remove(image_path)

#first, add a background gradient for style, then add a border around each table value. Then, if the name is Avi, the value, Avi is highlighted in yellow
#the gradient colors based on how large the values are, largest value in the column gets the darkest color
df_styled = merge_df.style.background_gradient()
df_styled.apply(lambda x: ['border: 2px solid black' if value != " " else ' ' for value in x], axis=1)
df_styled.apply(lambda x: ['background: yellow' if value == "Avi" else 'border: 2px solid black' for value in x], axis=1)
#use dataframe image to export the image, creating a png file that can be viewed
dfi.export(df_styled, image_path)

#To keep everything clean, the image will be opened using the OS method, then removed
img = Image.open(image_path)
img.show()


#finishes the code, deletes the csv and png files
print("Removing CSV File... Comment me out to keep!")
os.remove(directory) #csv file
print("Removing IMG File... Comment me out to keep!")
os.remove(image_path) #png file
