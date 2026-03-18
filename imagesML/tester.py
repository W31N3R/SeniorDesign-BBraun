import os

filelist = []

print(os.getcwd())  # Print the current working directory

currentdir = os.getcwd()  # Get the current working directory

print(os.listdir(os.getcwd()))  # Print the files in the root directory
print("")

os.chdir(f"{currentdir}\\imagesML\\22_Gauge_XYZ_Clockwise_Rotations") 
#C:\Users\herop\OneDrive\Documents\!College\!BBraunFiles\imagesML\22_Gauge_XYZ_Clockwise_Rotations
print(os.getcwd())  # Print the current working directory 
for file in os.listdir():
    filelist.append(file)  # Print the files in the current directory
print(filelist)
