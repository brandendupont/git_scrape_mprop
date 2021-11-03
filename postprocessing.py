import sys
import pandas as pd
import numpy as np
import geopandas as gpd
import requests as r
import os


## Global Vars
CRS = 4326
ALD_2018 = r'https://data.milwaukee.gov/dataset/1301738f-4b4a-4f73-bbaa-a4cac069e371/resource/51ca7f90-66cd-47f2-9197-fd4a5ba08c44/download/alderman.zip'
MPD_SHP = r'https://data.milwaukee.gov/dataset/1cb11103-18df-4c6e-b622-859d1e217920/resource/cac45f22-0609-4972-88a5-a3f6d9f74f83/download/mpd.zip'

MPROP_COLS = ['TAXKEY','YR_ASSMT', 'NR_UNITS', 'YR_BUILT', 'C_A_LAND', 'C_A_IMPRV', 'C_A_TOTAL', 'OWN_OCPD',\
                                 'LAND_USE_GP', "LAND_USE", 'HOUSE_NR_LO', 'SDIR','STREET', 'STTYPE', \
                        'OWNER_NAME_1', 'OWNER_NAME_2', 'OWNER_NAME_3', 'OWNER_MAIL_ADDR','OWNER_CITY_STATE', 'OWNER_ZIP', 'ZONING',\
                            'CONVEY_DATE','CONVEY_TYPE']

SUBSET_MPROP_COLS = ['TAXKEY', 'YR_ASSMT','C_A_LAND', 'C_A_IMPRV', 'C_A_TOTAL', 'OWNER_NAME_1', 'OWNER_NAME_2',\
       'OWNER_NAME_3', 'OWNER_MAIL_ADDR', 'OWNER_CITY_STATE', 'OWNER_ZIP',\
       'NR_UNITS', 'YR_BUILT', 'ZONING', 'LAND_USE', 'LAND_USE_GP', 'OWN_OCPD',\
       'Address', 'CONVEY_DATE','CONVEY_TYPE']


def get_mke_od_url():

    #define a new function to get 
    parcelbase_url = f'https://data.milwaukee.gov/api/3/action/resource_search?query=name:parcelpolygon'

    try:
        url_result = r.get(parcelbase_url).json()['result']['results'][0]['url']
        
    except:
        print("call didnt work")

    return url_result

def get_property_url(property_type):
    
    
    ar = r.get('https://data.milwaukee.gov/api/3/action/package_search?fq=tags:Address').json()['result']['results']
    
    address_results = [i['resources']  for i in ar]
    
    all_urls = []
    for i in address_results:
        for y in i:
            try:
                all_urls.append(y['url'])
            except:
                continue
                
    
    url_df = pd.DataFrame(all_urls,columns=['url'])

    url_df['path'] = url_df['url'].str.split('/').str.get(-1)
    
    return url_df[url_df['path'] == f'{property_type}.csv']['url'].values[0]


def pcb_to_wgs_84(df):
    
    """
    Takes city of milwaukee parcelbase and returns a centroid lat long of the parcel
    in WGS84 -- slippy maps preferred crs.
    """
    
    # drop null values
    pcb_new = df[df['geometry'].isnull() == False]

    # convert coordinate reference system to WGS 84
    pcb_new['geometry'] = pcb_new['geometry'].to_crs(epsg=4326)
    
    # get center of parcel
    pcb_new['centroid'] = pcb_new['geometry'].centroid
    #get lat long
    pcb_new['lat'] = pcb_new['centroid'].map(lambda p: p.y)
    pcb_new['long'] = pcb_new['centroid'].map(lambda p: p.x)
    
    return pcb_new


def assign_reference_tables(df, lu, lu_gp):
    
    # correct for types
    lu.index = lu.index.fillna(0).astype(np.int64)
    
    #correct for types
    lu_gp.index = lu_gp.index.fillna(0).astype(np.int64)
    
    df['LAND_USE'] = df['LAND_USE'].fillna(0).astype(np.int64)
    df['LAND_USE_GP'] = df['LAND_USE_GP'].fillna(0).astype(np.int64)
    
    #assert correct types
    assert df['LAND_USE'].dtype == lu.index.dtype
    
    #assert correct types
    assert df['LAND_USE_GP'].dtype == LU_GP.index.dtype
    
    
    df_lu = pd.merge(df, lu, how='left', left_on="LAND_USE_GP", right_index=True)
    
    df_lu_gp = pd.merge(df_lu, lu_gp, how='left', left_on="LAND_USE", right_index=True)
    
    return df_lu_gp




if __name__ == "__main__":

    print("argv :", sys.argv)

    # import aldermanic districts
    ald = gpd.read_file(ALD_2018).to_crs(CRS)

    #import police districts
    mpd = gpd.read_file(MPD_SHP).to_crs(CRS)


    # import mprop
    mp = pd.read_csv(get_property_url('mprop'),\
                            usecols=MPROP_COLS)

    # clean address
    mp[['SDIR', 'STTYPE']] = mp[['SDIR', 'STTYPE']].apply(lambda x: x.str.capitalize())
    mp['STREET'] = mp['STREET'].str.split(" ").apply(lambda x: " ".join(list(map(str.capitalize, x))))
    mp['Address'] = mp['HOUSE_NR_LO'].astype(str) + " " + mp['SDIR'] + " " + mp['STREET'] + " " + mp['STTYPE']

    #subset mprop
    mp = mp[SUBSET_MPROP_COLS]

    #import land use codes
    LU = pd.read_csv('data/land_use.csv', index_col="lu-code")
    LU_GP = pd.read_csv('data/land_use_full.csv', index_col="Category_full")

    #import census tract data
    cen = gpd.read_file("data/census.geojson")

    #read city parcelbase
    pcb = gpd.read_file(get_mke_od_url())

    #get centroid of parcel in wgs84
    pcb = pcb_to_wgs_84(pcb)

    # add land use
    mp = assign_reference_tables(mp, LU, LU_GP)

    #reconcile pcb names
    pcb['Taxkey'] = pcb['Taxkey'].fillna(0).astype('int64')
    pcb = pcb.rename(columns={'Taxkey':'TAXKEY'})

    # merge to mprop
    mp = pd.merge(mp, pcb[['TAXKEY', 'lat', 'long']])

    #convert mprop to geodataframe
    mp = gpd.GeoDataFrame(mp, geometry=gpd.points_from_xy(mp.long, mp.lat), crs=4326)

    #merge census data
    mp_cen = gpd.sjoin(mp, cen).drop('index_right', axis=1)

    #merge aldermanic boundaries
    mp_cen_ald = gpd.sjoin(mp_cen, ald[['ALDERMAN', 'geometry', 'ALD']]).drop('index_right', axis=1)

    #merge police boundaries
    mp_cen_ald_mpd = gpd.sjoin(mp_cen_ald, mpd[['POLICE', 'geometry']]).drop('index_right', axis=1)

    #drop any duplicated taxkeys 
    mp_cen_ald_mpd = mp_cen_ald_mpd.drop_duplicates("TAXKEY", keep='first')

    #save data
    mp_cen_ald_mpd.to_csv("flat_mprop.csv", index=False)

    print(mp_cen_ald_mpd.shape)

    df = pd.DataFrame(np.random.randint(
    0, 100, size=(10, 4)), columns=list('ABCD'))

    df.to_csv("df_output.csv")
