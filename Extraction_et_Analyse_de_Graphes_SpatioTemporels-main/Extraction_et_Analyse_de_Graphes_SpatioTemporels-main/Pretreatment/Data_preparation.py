import geopandas as gpd
import os


os.environ["SHAPE_RESTORE_SHX"] = "YES"

def To_Json(path,nams):
    gdf = gpd.read_file(path)
    to_path = "C:/Users/DELL/Desktop/Projet/Pretreatment/Grabels"+nams+".csv"
    gdf.to_csv(to_path, index=False)




if __name__ == "__main__":

    nams = ["_01_2015","_01_2024","_02_2025","_03_2017","_03_2019","_03_2020","_03_2021","_05_2015","_05_2016","_06_2022","_09_2023","_11_2016","_11_2017","_11_2018","_11_2020","_11_2021"]
    
    for i in range(16):
        path = f"C:/Users/DELL/Desktop/Projet/Pretreatment/Statistiques/Grabels{nams[i]}.gpkg"
        To_Json(path,nams[i])




 
    
    