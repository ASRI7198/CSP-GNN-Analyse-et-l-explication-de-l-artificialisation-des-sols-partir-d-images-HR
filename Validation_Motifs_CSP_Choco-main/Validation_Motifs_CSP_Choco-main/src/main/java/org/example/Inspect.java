package org.example;

import java.nio.file.Path;
import java.util.*;


public class Inspect {

    private static String preview(int[] arr, int max) {
        if (arr == null) return "[]";
        StringBuilder sb = new StringBuilder();
        sb.append("[");
        int k = Math.min(max, arr.length);
        for (int i = 0; i < k; i++) {
            if (i > 0) sb.append(", ");
            sb.append(arr[i]);
        }
        if (arr.length > k) sb.append(", ...");
        sb.append("]");
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        Path graphPath = Path.of("C:/Users/rasri/IdeaProjects/Projet-CSP/src/main/java/stgraph4.json");
        STGraph G = STLoader.fromJson(graphPath);

        System.out.println("=== Résumé du graphe spatio-temporel ===");
        System.out.println("N (nb noeuds) : " + G.N);

        Map<Integer,Integer> classCount = new TreeMap<>();
        for (int c : G.classOf) classCount.merge(c, 1, Integer::sum);
        System.out.println("Classes (classe -> count) : " + classCount);

        Map<Integer,Integer> layerCount = new TreeMap<>();
        for (int l : G.layerOf) layerCount.merge(l, 1, Integer::sum);
        System.out.println("Couches (layer -> count) : " + layerCount + "  |  #layers=" + layerCount.size());

        int minT = Integer.MAX_VALUE, maxT = Integer.MIN_VALUE;
        Set<Integer> distinctT = new HashSet<>();
        for (int t : G.timeOf) { minT = Math.min(minT, t); maxT = Math.max(maxT, t); distinctT.add(t); }
        System.out.println("Temps min/max : " + minT + " / " + maxT + "  |  distincts=" + distinctT.size());

        long spatialEdgesDirected = 0;
        for (int a = 0; a < G.N; a++) spatialEdgesDirected += G.spatialAdj[a].length;
        long spatialEdgesUndirected = spatialEdgesDirected / 2;

        long temporalEdges = 0;
        for (int a = 0; a < G.N; a++) temporalEdges += G.temporalAdj[a].length;

        System.out.println("#Arêtes spatiales (non orienté) : " + spatialEdgesUndirected);
        System.out.println("#Arêtes temporelles (orienté)   : " + temporalEdges);

        System.out.println("\n=== Vérifications ===");
        int badSpatial = 0;
        for (int a = 0; a < G.N; a++) {
            for (int b : G.spatialAdj[a]) {
                if (G.layerOf[a] != G.layerOf[b]) badSpatial++;
            }
        }
        if (badSpatial == 0) System.out.println("OK spatial : toutes les arêtes relient des noeuds de même couche");
        else System.out.println("ATTENTION spatial : " + badSpatial + " liens entre couches différentes");

        int badTemporal = 0;
        for (int a = 0; a < G.N; a++) {
            for (int b : G.temporalAdj[a]) {
                if (!(G.timeOf[b] > G.timeOf[a])) badTemporal++;
            }
        }
        if (badTemporal == 0) System.out.println("OK temporel : toutes les arêtes vont vers le futur strict");
        else System.out.println("ATTENTION temporel : " + badTemporal + " liens non strictement vers le futur");

        System.out.println("\n=== Aperçu des 5 premiers noeuds ===");
        int show = Math.min(12, G.N);
        for (int i = 0; i < show; i++) {
            System.out.printf(
                    "Noeud %d  class=%d  layer=%d  time=%d  |  spat=%s  temp=%s%n",
                    i, G.classOf[i], G.layerOf[i], G.timeOf[i],
                    preview(G.spatialAdj[i], 10),
                    preview(G.temporalAdj[i], 10)
            );
        }

        Path motifsPath = Path.of("C:/Users/rasri/IdeaProjects/Projet-CSP/src/main/java/Motifs/500_pairs_12_k-hop_32_N=4500_s=2.json");
        try {
            List<Pattern_M> patterns = MotifJsonLoader.loadPatterns(motifsPath, false);
            System.out.println("\n=== Motifs ===");
            System.out.println("Motifs chargés : " + patterns.size());

            int mSp = 0, mTemp = 0;
            for (Pattern_M p : patterns) {
                for (Edge e : p.edges) {
                    if (e.type == EdgeType.SPATIAL) mSp++; else mTemp++;
                }
            }
            System.out.println("Arêtes de motifs : SPATIAL=" + mSp + "  TEMPOREL=" + mTemp);

            int toShow = Math.min(5, patterns.size());
            for (int i = 0; i < toShow; i++) {
                System.out.println("\nMotif #" + (i+1));
                System.out.print(patterns.get(i));
            }
        } catch (Exception ex) {
            System.out.println("\n[INFO] Motifs non chargés : " + ex.getMessage());
        }
    }
}