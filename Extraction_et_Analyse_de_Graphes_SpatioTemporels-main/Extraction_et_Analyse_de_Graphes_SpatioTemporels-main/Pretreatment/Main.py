import Functions as f
import os


os.environ["MKL_THREADING_LAYER"] = "GNU"
nams = ["_2015_01","_2015_05","_2016_05","_2016_11","_2017_03","_2017_11","_2018_11","_2019_03","_2020_03","_2020_11","_2021_03","_2021_11","_2022_06","_2023_09","_2024_01","_2025_02"]

def traitement_Creat_GS():
    for i in range(16):
        path = "C:/Users/rasri/Desktop/GST/GST/Data/Grabels"+nams[i]+".csv"
        noeuds = f.Create_Noeuds(path)
        G = f.Create_Graph(noeuds)
        print('created')
        f.Stocker_Graph_GraphML(G,nams[i],0)
        print('stocked')

def traitement_Read_GS(): 
    GS = []
    for i in range(len(nams)):
        path = "C:/Users/DELL/Desktop/Projet/Pretreatment/Graphes spatiaux/Grabels"+nams[i]+".graphml.xml"
        GS.append(f.Read_GraphML(path,nams[i]))
    return GS

def traitement_Read_GST(nams_st): 
    G_st = []
    for i in range(len(nams_st)):
        path = "C:/Users/DELL/Desktop/Projet/Pretreatment/Graphes Spasio-Temporelles/RST_Grabels"+nams_st[i]+".graphml.xml"
        G_st.append(f.Read_GraphML(path,nams_st[i]))
    return G_st


def traitement_Creat_GST():
    GS = traitement_Read_GS()
    for i in range(0, len(nams) - 1, 2):
        print("create")
        G_st = f.Create_Graphe_spatio_temporel(GS[i], GS[i+1])
        print("Stoker")
        nom = nams[i]+nams[i+1]
        f.Stocker_Graph_GraphML(G_st,nom,1)

def traitement_Creat_GST_2(nams_st):
    GST = traitement_Read_GST()
    for i in range(0, len(nams_st) - 1, 2):
        print("create")
        G_st = f.Create_Graphe_spatio_temporel_2(GST[i], GST[i+1])
        print("Stoker")
        nom = nams_st[i]+nams_st[i+1]
        f.Stocker_Graph_GraphML(G_st,nom,1)
    
   



if __name__ == "__main__":

    traitement_Creat_GS()

    #--------------------------------------------------------------------------------------------
    
    traitement_Read_GST()

    #--------------------------------------------------------------------------------------------

    nams_st =["_2015_01_2015_05","_2016_05_2016_11","_2017_03_2017_11","_2018_11_2019_03","_2020_03_2020_11","_2021_03_2021_11","_2022_06_2023_09","_2024_01_2025_02"]
    traitement_Creat_GST_2(nams_st)

    #--------------------------------------------------------------------------------------------

    nams_st =["_2015_01_2015_05_2016_05_2016_11","_2017_03_2017_11_2018_11_2019_03","_2020_03_2020_11_2021_03_2021_11","_2022_06_2023_09_2024_01_2025_02"]
    traitement_Creat_GST_2(nams_st)

    #--------------------------------------------------------------------------------------------

    nams_st =["_2015_01_2015_05_2016_05_2016_11_2017_03_2017_11_2018_11_2019_03","_2020_03_2020_11_2021_03_2021_11_2022_06_2023_09_2024_01_2025_02"]
    traitement_Creat_GST_2(nams_st) # ===> Graphes spatio-temporelles finales

    



    


        

    
    