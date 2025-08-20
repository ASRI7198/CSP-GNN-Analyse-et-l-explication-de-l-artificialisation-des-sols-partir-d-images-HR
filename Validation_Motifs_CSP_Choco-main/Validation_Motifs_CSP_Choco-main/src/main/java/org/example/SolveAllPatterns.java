package org.example;

import org.chocosolver.solver.Solver;
import org.chocosolver.solver.search.measure.IMeasures;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;


public class SolveAllPatterns {

    static final Path GRAPH_PATH  = Path.of("C:/Users/rasri/IdeaProjects/Projet-CSP/src/main/java/stgraph4.json");
    static final Path MOTIFS_PATH = Path.of("C:/Users/rasri/IdeaProjects/Projet-CSP/src/main/java/Motifs/500_pairs_12_k-hop_32_N=4500_s=2.json");

    static final int MAX_SOL_PER_PATTERN = 5;
    static final int MAX_PATTERNS         = 50;
    static final long SOLVE_TIME_MS       = 10_000;

    static final boolean FLIP_TEMPORAL_EDGES_IN_APP = true;

    private static String yyyymmToStr(int t) {
        int yyyy = t / 100, mm = t % 100;
        return String.format("%04d/%02d", yyyy, mm);
    }

    private static Integer parseYyyymmFromKey(String key) {
        if (key == null) return null;
        String[] parts = key.trim().split("/");
        if (parts.length < 3) return null;
        String yyyy = parts[1].trim();
        String mm   = parts[2].trim();
        if (yyyy.length() != 4 || mm.length() != 2) return null;
        try {
            return Integer.parseInt(yyyy + mm);
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private static Pattern_M normalizeTemporalOrientation(Pattern_M P) {
        if (!FLIP_TEMPORAL_EDGES_IN_APP) return P;

        if (P.nodeKeys == null || P.nodeKeys.length < P.U) return P;

        Integer[] t = new Integer[P.U];
        for (int u = 0; u < P.U; u++) t[u] = parseYyyymmFromKey(P.nodeKeys[u]);

        boolean changed = false;
        List<Edge> edges2 = new ArrayList<>(P.edges.size());
        for (Edge e : P.edges) {
            if (e.type == EdgeType.TEMPORAL) {
                Integer tu = (e.u >=0 && e.u < P.U) ? t[e.u] : null;
                Integer tv = (e.v >=0 && e.v < P.U) ? t[e.v] : null;
                if (tu != null && tv != null && tu > tv) {
                    edges2.add(new Edge(e.v, e.u, e.type));
                    changed = true;
                } else {
                    edges2.add(e);
                }
            } else {
                edges2.add(e);
            }
        }
        if (!changed) return P;
        return new Pattern_M(P.motifClass, edges2, P.nodeKeys);
    }

    public static void main(String[] args) {
        try {
            STGraph G = STLoader.fromJson(GRAPH_PATH);
            System.out.println("=== Graphe chargé ===");
            System.out.println("N=" + G.N + " | #spatial=" + countSpatialUndirected(G) + " | #temporal=" + countTemporal(G));

            List<Pattern_M> patterns = MotifJsonLoader.loadPatterns(MOTIFS_PATH, false);
            System.out.println("Motifs chargés : " + patterns.size());

            int mSp = 0, mTemp = 0;
            for (Pattern_M p : patterns) {
                for (Edge e : p.edges) {
                    if (e.type == EdgeType.SPATIAL) mSp++; else mTemp++;
                }
            }
            System.out.println("Arêtes dans motifs : SPATIAL=" + mSp + "  TEMPOREL=" + mTemp);

            int processed = 0;
            for (int idx = 0; idx < patterns.size(); idx++) {
                if (MAX_PATTERNS > 0 && processed >= MAX_PATTERNS) break;

                Pattern_M Praw  = patterns.get(idx);
                Pattern_M P = normalizeTemporalOrientation(Praw);

                System.out.println("\n=== Motif #" + (idx + 1) + " | U=" + P.U + " | edges=" + P.edges.size() + " ===");
                if (P != Praw) System.out.println("[INFO] Réorientation temporelle appliquée (passé→futur).");
                System.out.print(P);

                try {
                    BuildResult br = CSPModelBuilder.build(G, P);
                    Solver solver = br.model.getSolver();
                    if (SOLVE_TIME_MS > 0) solver.limitTime(SOLVE_TIME_MS);

                    int shown = 0, total = 0;
                    while (solver.solve()) {
                        total++;
                        if (shown < MAX_SOL_PER_PATTERN) {
                            shown++;
                            System.out.println("Solution " + total + ":");
                            for (int u = 0; u < br.X.length; u++) {
                                int v = br.X[u].getValue();
                                String key = (P.nodeKeys != null && u < P.nodeKeys.length) ? P.nodeKeys[u] : ("u" + u);
                                System.out.printf("  %s -> v=%d [class=%d, layer=%d, time=%s]%n",
                                        key, v, G.classOf[v], G.layerOf[v], yyyymmToStr(G.timeOf[v]));
                            }
                        }
                    }

                    IMeasures meas = solver.getMeasures();
                    double timeSec = (meas != null) ? meas.getTimeCount() : Double.NaN;
                    long backtracks = (meas != null) ? meas.getBackTrackCount() : -1L;

                    System.out.printf(Locale.ROOT,
                            "Nb solutions = %d%s | Temps = %.3fs | Backtracks = %d%n",
                            total,
                            (SOLVE_TIME_MS > 0 ? " (limite " + SOLVE_TIME_MS + " ms)" : ""),
                            timeSec,
                            backtracks
                    );

                } catch (Exception ex) {
                    System.out.println("[ECHEC] " + ex.getMessage());
                }

                processed++;
            }

            System.out.println("\n=== Terminé ===");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static long countSpatialUndirected(STGraph G) {
        long directed = 0;
        for (int a = 0; a < G.N; a++) directed += G.spatialAdj[a].length;
        return directed / 2;
    }

    private static long countTemporal(STGraph G) {
        long temporal = 0;
        for (int a = 0; a < G.N; a++) temporal += G.temporalAdj[a].length;
        return temporal;
    }
}