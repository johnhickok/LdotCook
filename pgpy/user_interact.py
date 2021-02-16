#code snippet user interaction
usr_coordinates = input("Copy/Paste coordinates:")
print(usr_coordinates)

lat = usr_coordinates.split(',')[0].strip()
lon = usr_coordinates.split(',')[1].strip()

print("lat =", lat)
print("lon =", lon)

