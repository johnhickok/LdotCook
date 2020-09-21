# enter script, lat, lon from Google Maps
# python py07.py 33.876381, -118.102511
import psycopg2
from sys import argv

mylat = argv[1].replace(',', '')
mylon = argv[2]

# Use lat/lon inputs to create a binary geom value in Zone 5 coordinates.
myloc = "ST_Transform(ST_GeomFromText('POINT(" + mylon + " " + mylat + ")',4326),2229)"

# Connect to database
conn = psycopg2.connect("dbname=[db name] user=[user name] password=[your password]") 

# Open a cursor to perform database operations
cur = conn.cursor()

# Print header
print("")
print("Results for coordinates " + mylat + ", " + mylon)

# Create & execute a search string for county and state
s_usa_county = (
"""
select 
name, 
state_name 
from usa_counties 
where ST_Intersects(
	usa_counties.geom,
    ST_GeomFromText('POINT(mylon mylat)', 4326)
	);
"""
)
s_usa_county = s_usa_county.replace("mylon", mylon)
s_usa_county = s_usa_county.replace("mylat", mylat)

cur.execute(s_usa_county)
s_county_state = cur.fetchone()
usa_county = s_county_state[0]
usa_state = s_county_state[1]

if usa_county != 'Los Angeles':
  print("County of " + usa_county + ", " + usa_state)
else:
  print("Los Angeles County Services:")

  # Create & execute a search string for legal city
  s_legal_city = "select city_name from dpw_city_boundaries where ST_Intersects(dpw_city_boundaries.geom, " + myloc + ");"
  cur.execute(s_legal_city)
  legal_city = cur.fetchone()[0]
  print("Legal City: " + legal_city)
  
  # Create & execute a search string for CSA Community Name
  s_community = "select label from bos_countywide_statistical_areas where ST_Intersects(bos_countywide_statistical_areas.geom, " + myloc + ");"
  cur.execute(s_community)
  community = cur.fetchone()[0]
  print("Community: " + community)
  
  # Create & execute a search string for DCFS ZIP Code
  s_dcfs_zip = "select ziptxt from dcfs_zip_codes where ST_Intersects(dcfs_zip_codes.geom, " + myloc + ");"
  cur.execute(s_dcfs_zip)
  dcfs_zip = cur.fetchone()[0]
  print("ZIP Code: " + dcfs_zip)
  
  # Create & execute a search string for Sup Dist
  s_sup_dist = "select sup_dist_n from dpw_sup_dist where ST_Intersects(dpw_sup_dist.geom, " + myloc + ");"
  cur.execute(s_sup_dist)
  sup_dist = cur.fetchone()[0]
  print("Sup Dist: " + sup_dist)
  
  # Create & execute a search string for SPA
  s_spa = "select abbv from dhs_spa where ST_Intersects(dhs_spa.geom, " + myloc + ");"
  cur.execute(s_spa)
  spa = cur.fetchone()[0]
  print("SPA: " + spa)

  # Create & execute a search string for dcfs field office info
  s_dcfs = "select dcfsoffice, d_addr1, d_addr2, d_phone from dcfs_service_areas where ST_Intersects(dcfs_service_areas.geom, " + myloc + ");"
  cur.execute(s_dcfs)
  dcfs = cur.fetchone()
  d_office = dcfs[0]
  d_addr1 = dcfs[1]
  d_addr2 = dcfs[2]
  d_phone = dcfs[3]
  
  print("")
  print("DCFS Office")
  print("Office: " + d_office)
  print("Address (1): " + d_addr1)
  print("Address (2): " + d_addr2)
  print("Phone: " + d_phone)
  
  s_lasd = (
  """
  select 
  lasd_reporting_districts.st_name as station,
  lasd_reporting_districts.s_type as agency,
  lasd_stations.addrln1,
  lasd_stations.addrln2,
  lasd_stations.ravs_phone,
  lasd_stations.ravs_fax
  from lasd_reporting_districts
  join lasd_stations
  on lasd_reporting_districts.st_name = lasd_stations.st_name
  where ST_Intersects(lasd_reporting_districts.geom,
  """
  )
  
  s_lasd += myloc + ");"
  
  cur.execute(s_lasd)
  lasd = cur.fetchone()

  lasd_station = lasd[0]
  lasd_agency = lasd[1]
  lasd_addrln1 = lasd[2]
  lasd_addrln2 = lasd[3]
  lasd_phone = lasd[4]
  lasd_fax = lasd[5]
  
  print("")
  print("Law Enforcement Jurisdiction")
  print("Station: " + lasd_station)
  print("Agency: " + lasd_agency)
  print("Address (1): " + lasd_addrln1)
  print("Address (2): " + lasd_addrln2)
  print("Phone: " + lasd_phone)
  print("Fax: " + lasd_fax)
  
  
  # compute distance of myloc to the nearest feature in LASD CSB
  s_lasd_csb = (
  """
  select
  name, 
  service, 
  patrolarea, 
  phone, 
  addrln1, 
  addrln2, 
  ST_Distance(lasd_service_bureau_rd.geom,
  					myloc
  					)
  from lasd_service_bureau_rd order by ST_Distance(lasd_service_bureau_rd.geom,
  					myloc
  					) asc limit 1;
  """
  )
  
  s_lasd_csb = s_lasd_csb.replace("myloc", myloc)

  cur.execute(s_lasd_csb)
  lasd_csb = cur.fetchone()
  
  lasd_csb_name = lasd_csb[0]
  lasd_csb_service = lasd_csb[1]
  lasd_csb_patrol = lasd_csb[2]
  lasd_csb_phone = lasd_csb[3]
  lasd_csb_addrln1 = lasd_csb[4]
  lasd_csb_addrln2 = lasd_csb[5]
  lasd_csb_distance = lasd_csb[6]
  
  print("")
  print("LASD County Service Bureau")
  print("Nearest Facility: " + lasd_csb_name)
  print("Distance: " + str(int(round(lasd_csb_distance,0))) + " feet")
  print("Patrol Area: " + str(int(lasd_csb_patrol)))
  print("Address (1): " + lasd_csb_addrln1)
  print("Address (2): " + lasd_csb_addrln2)
  print("Phone: " + lasd_csb_phone)
  
  
  # compute distance of myloc to the nearest feature in LASD Parks
  s_lasd_parks = (
  """
  select
  park_name, 
  station,
  patrol_area,
  tel_num, 
  ST_Distance(lasd_parks_rd.geom,
  					myloc
  					)
  from lasd_parks_rd order by ST_Distance(lasd_parks_rd.geom,
  					myloc
  					) asc limit 1;
  """
  )

  s_lasd_parks = s_lasd_parks.replace("myloc", myloc)
  
  cur.execute(s_lasd_parks)
  lasd_parks = cur.fetchone()
  
  lasd_parks_name = lasd_parks[0]
  lasd_parks_station = lasd_parks[1]
  lasd_parks_patrol = lasd_parks[2]
  lasd_parks_phone = lasd_parks[3]
  lasd_parks_distance = lasd_parks[4]
  
  print("")
  print("LASD County Parks Service")
  print("Nearest Facility: " + lasd_parks_name)
  print("Distance: " + str(int(round(lasd_parks_distance,0))) + " feet")
  print("Station: " + lasd_parks_station)
  print("Patrol Area: " + str(int(lasd_parks_patrol)))
  print("Phone: " + lasd_parks_phone)
  
  
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