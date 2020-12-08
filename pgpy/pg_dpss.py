# script for debugging, isoate dpss tables only
# enter script, lat, lon from Google Maps
# python pg_dpss.py 33.876381, -118.102511 (inside L.A. County only)
import psycopg2
from sys import argv

mylat = argv[1].replace(',', '')
mylon = argv[2]

# Use lat/lon inputs to create a binary geom value in Zone 5 coordinates.
myloc = "ST_Transform(ST_GeomFromText('POINT(" + mylon + " " + mylat + ")',4326),2229)"

# Connect to database
conn = psycopg2.connect("host=localhost dbname=ravs_data user=postgres password=postgres") 

# Open a cursor to perform database operations
cur = conn.cursor()

# Print header
print("")
print("Results for coordinates " + mylat + ", " + mylon)


# Query and display services offered by DPSS
  
print("")
print("DPSS Office(s)")

# 21 tables for each service
dpss_tables = [
'DPSS_CalFresh_Approved_Adult',
'DPSS_CalFresh_Approved_Family',
'DPSS_CalFresh_Intake_Adult',
'DPSS_CalFresh_Intake_Family',
'DPSS_CalWorks_Approved',
'DPSS_CalWorks_Approved_Refugee',
'DPSS_CalWorks_Intake',
'DPSS_CalWorks_Intake_Refugee',
'DPSS_CAPI_Approved',
'DPSS_CAPI_Intake',
'DPSS_GAIN_Approved',
'DPSS_GAIN_Intake',
'DPSS_GeneralRelief_Approved',
'DPSS_GeneralRelief_Intake',
'DPSS_GROW_Approved',
'DPSS_GROW_Intake',
'DPSS_IHSS',
'DPSS_Medical_Approved_Adult',
'DPSS_Medical_Approved_Family',
'DPSS_Medical_Intake_Adult',
'DPSS_Medical_Intake_Family'
]

# Create and populate a dictionary for gathering services provided by DPSS offices
dpss_dict = {}

for t in dpss_tables:
  s_dpss = "select name from " + t + " where ST_Intersects(" + t + ".geom, " + myloc + ");"
  cur.execute(s_dpss)
  dpss = cur.fetchone()
  dpss = dpss[0]
  
  if dpss not in dpss_dict:
    dpss_dict[dpss] = t
  else:
    old_value = dpss_dict[dpss]
    new_value = old_value + ", " + t
    dpss_dict[dpss] = new_value

for i in dpss_dict:
  s_dpss_office = "select street, city, state, zip, telephone from dpss_offices where name like '" + i + "';"
  cur.execute(s_dpss_office)
  dpss_office = cur.fetchone()
  dpss_office_street = dpss_office[0]
  dpss_office_city = dpss_office[1]
  dpss_office_state = dpss_office[2]
  dpss_office_zip = dpss_office[3]
  dpss_office_phone = dpss_office[4]
  dpss_services = dpss_dict[i]
  print("Office: " + i)
  print("Address (1): " + dpss_office_street)
  print("Address (1): " + dpss_office_city + ", " + dpss_office_state + " " + dpss_office_zip)
  print("Phone: " + dpss_office_phone)
  print("Services: " + dpss_services)
  print("")

conn.close()
