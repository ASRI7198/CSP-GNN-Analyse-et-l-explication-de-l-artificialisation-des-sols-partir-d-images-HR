import numpy as np
import math
from shapely.geometry import Polygon



class Noeud :
    def _init_(self ,DN ,year , Area ,perimeter ,Compacite ,width ,height ,Rectangularity ,mean,std,variance,Classe, multipolygone):
        self.DN = DN
        self.year = year
        self.Aire = Area
        self.Perimeter = perimeter
        self.Largeur = width
        self.Hauteur = height
        self.Rectangularity = Rectangularity
        self.Elongation = None
        self.I_Miller = Compacite
        self.multipolygone = multipolygone   
        self.centroid = self.multipolygone.centroid
        self.mean = mean
        self.std = std
        self.variance = variance
        self.Nbr_Voisins = None
        self.surface_voisins = None
        self.classe = Classe
   
    
    def Polygon_Elongation(self):
        self.Elongation = max(self.Largeur,self.Hauteur) / min(self.Largeur,self.Hauteur)

    def nombre_voisins_adjacents(self, multipolygones):
        compteur = 0
        for multipolygone in multipolygones:
            if multipolygone != self.multipolygone and self.multipolygone.touches(multipolygone):
                compteur += 1
        self.Nbr_Voisins = compteur

    def surface_cumulee_voisins(self, multipolygones):
        surface_voisins = 0.0
        for multipolygone in multipolygones:
            if multipolygone != self.multipolygone and self.multipolygone.touches(multipolygone):
                surface_voisins += multipolygone.area
        self.surface_voisins = surface_voisins




    def compute_all(self,multipolygones):
        self.Polygon_Elongation()
        self.nombre_voisins_adjacents(multipolygones)
        self.surface_cumulee_voisins(multipolygones)


        

    def _str_(self):
        return f"DN: {self.DN}, Classe: {self.classe}, Aire: {self.Aire},Perimeter: {self.Perimeter}, Indice Miller: {self.I_Miller}, Largeur: {self.Largeur}, Hauteur: {self.Hauteur}, Rectangularity: {self.Rectangularity}, Elongation: {self.Elongation}, Centroid: ({self.centroid}),Nombre de Voisins: {self.Nbr_Voisins},surface voisins: {self.surface_voisins}"
   
    def _repr_(self):
        return f"DN: {self.DN}, Classe: {self.classe}, Aire: {self.Aire},Perimeter: {self.Perimeter}, Indice Miller: {self.I_Miller}, Largeur: {self.Largeur}, Hauteur: {self.Hauteur}, Rectangularity: {self.Rectangularity}, Elongation: {self.Elongation}, Centroid: ({self.centroid}),Nombre de Voisins: {self.Nbr_Voisins},surface voisins: {self.surface_voisins}"
    def _hash_(self):
        return hash((self.DN, self.year, self.Aire, self.Perimeter, self.I_Miller, self.Largeur, self.Hauteur, self.Rectangularity, self.Elongation, tuple(self.centroid.coords), self.Nbr_Voisins, self.surface_voisins))  
    def _eq_(self, other):
        if isinstance(other, Noeud):
            return (self.DN == other.DN and
                    self.year == other.year and
                    self.Aire == other.Aire and
                    self.Perimeter == other.Perimeter and
                    self.I_Miller == other.I_Miller and
                    self.Largeur == other.Largeur and
                    self.Hauteur == other.Hauteur and
                    self.Rectangularity == other.Rectangularity and
                    self.Elongation == other.Elongation and
                    self.centroid.equals(other.centroid) and
                    self.Nbr_Voisins == other.Nbr_Voisins and
                    self.surface_voisins == other.surface_voisins)
        return False
    def _ne_(self, other):
        return not self._eq_(other)