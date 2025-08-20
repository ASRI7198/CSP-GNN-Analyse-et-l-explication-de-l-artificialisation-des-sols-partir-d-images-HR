package org.example;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.variables.IntVar;

import java.util.*;
import java.util.stream.Collectors;
import java.util.Arrays;

public class CSPModelBuilder {

    static final boolean FILTER_BY_MOTIF_DATE = true;

    private static Integer parseYyyymmFromNodeKey(String key) {
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

    private static String yyyymmToStr(int t) {
        int yyyy = t / 100, mm = t % 100;
        return String.format("%04d/%02d", yyyy, mm);
    }

    public static BuildResult build(STGraph G, Pattern_M P) {
        Model model = new Model("CSP_ST_single_class");

        Integer[] motifTime = new Integer[P.U];
        for (int u = 0; u < P.U; u++) {
            motifTime[u] = (FILTER_BY_MOTIF_DATE && P.nodeKeys != null && u < P.nodeKeys.length)
                    ? parseYyyymmFromNodeKey(P.nodeKeys[u])
                    : null;
        }

        IntVar[] X = new IntVar[P.U];
        List<int[]> candidateDomains = new ArrayList<>(P.U);

        for (int u = 0; u < P.U; u++) {
            int targetClass = P.motifClass[u];
            Integer targetTime = motifTime[u];

            ArrayList<Integer> domList = new ArrayList<>();
            if (targetTime == null) {
                for (int v = 0; v < G.N; v++) {
                    if (G.classOf[v] == targetClass) domList.add(v);
                }
            } else {
                for (int v = 0; v < G.N; v++) {
                    if (G.classOf[v] == targetClass && G.timeOf[v] == targetTime) domList.add(v);
                }
            }

            if (domList.isEmpty()) {
                String timeMsg = (targetTime == null ? "ANY" : yyyymmToStr(targetTime));
                throw new IllegalStateException(
                        "Domaine vide pour u=" + u +
                                " (class=" + targetClass + ", time=" + timeMsg + ", label=" +
                                (P.nodeKeys != null && u < P.nodeKeys.length ? P.nodeKeys[u] : ("u"+u)) + ")"
                );
            }
            int[] dom = domList.stream().mapToInt(Integer::intValue).toArray();
            candidateDomains.add(dom);
            X[u] = model.intVar("X_" + u, dom);
        }

        model.allDifferent(X).post();

        int minT = Arrays.stream(G.timeOf).min().orElse(0);
        int maxT = Arrays.stream(G.timeOf).max().orElse(0);

        for (Edge E : P.edges) {
            int u = E.u, v = E.v;
            IntVar Xu = X[u], Xv = X[v];
            int[] domU = candidateDomains.get(u);
            int[] domV = candidateDomains.get(v);

            switch (E.type) {
                case SPATIAL -> {
                    IntVar layer_u = model.intVar("layer_u_" + u,
                            Arrays.stream(G.layerOf).min().orElse(0),
                            Arrays.stream(G.layerOf).max().orElse(0));
                    IntVar layer_v = model.intVar("layer_v_" + v, layer_u.getLB(), layer_u.getUB());
                    model.element(layer_u, G.layerOf, Xu, 0).post();
                    model.element(layer_v, G.layerOf, Xv, 0).post();
                    model.arithm(layer_u, "=", layer_v).post();

                    Tuples allowed = new Tuples(true);
                    int allowedCount = 0;

                    Map<Integer, Set<Integer>> neigh = new HashMap<>();
                    for (int a : domU)
                        neigh.put(a, Arrays.stream(G.spatialAdj[a]).boxed().collect(Collectors.toSet()));

                    for (int a : domU) for (int b : domV) {
                        if (G.layerOf[a] == G.layerOf[b] && neigh.get(a).contains(b)) {
                            allowed.add(a, b);
                            allowedCount++;
                        }
                    }

                    if (allowedCount == 0) {
                        String lu = (P.nodeKeys != null && u < P.nodeKeys.length) ? P.nodeKeys[u] : ("u"+u);
                        String lv = (P.nodeKeys != null && v < P.nodeKeys.length) ? P.nodeKeys[v] : ("v"+v);
                        throw new IllegalStateException(
                                "Aucune paire spatiale autorisée pour l’arête " + lu + " --SPATIAL--> " + lv +
                                        " (vérifie l’adjacence et la même couche)."
                        );
                    }

                    model.table(new IntVar[]{Xu, Xv}, allowed).post();
                }

                case TEMPORAL -> {
                    Tuples allowed = new Tuples(true);
                    int allowedCount = 0;

                    Map<Integer, Set<Integer>> succ = new HashMap<>();
                    for (int a : domU)
                        succ.put(a, Arrays.stream(G.temporalAdj[a]).boxed().collect(Collectors.toSet()));

                    for (int a : domU) for (int b : domV) {
                        if (succ.get(a).contains(b) && G.timeOf[b] > G.timeOf[a]) {
                            allowed.add(a, b);
                            allowedCount++;
                        }
                    }

                    if (allowedCount == 0) {
                        String lu = (P.nodeKeys != null && u < P.nodeKeys.length) ? P.nodeKeys[u] : ("u"+u);
                        String lv = (P.nodeKeys != null && v < P.nodeKeys.length) ? P.nodeKeys[v] : ("v"+v);

                        String tu = (motifTime[u] == null) ? "ANY" : yyyymmToStr(motifTime[u]);
                        String tv = (motifTime[v] == null) ? "ANY" : yyyymmToStr(motifTime[v]);

                        throw new IllegalStateException(
                                "Aucune paire temporelle autorisée pour " + lu + " --TEMPORAL--> " + lv +
                                        " (attendu passé→futur ; motif times u=" + tu + ", v=" + tv + ").\n" +
                                        "→ Si ta ligne JSON est écrite du futur→passé (ex: Dérivation récente→ancienne), " +
                                        "réoriente-la au chargement."
                        );
                    }

                    model.table(new IntVar[]{Xu, Xv}, allowed).post();

                    IntVar t_u = model.intVar("t_u_" + u, minT, maxT);
                    IntVar t_v = model.intVar("t_v_" + v, minT, maxT);
                    model.element(t_u, G.timeOf, Xu, 0).post();
                    model.element(t_v, G.timeOf, Xv, 0).post();
                    model.arithm(t_v, ">", t_u).post();
                }
            }
        }

        return new BuildResult(model, X);
    }
}