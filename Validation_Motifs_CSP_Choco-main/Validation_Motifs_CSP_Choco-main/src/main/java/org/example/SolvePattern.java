package org.example;

import java.nio.file.Path;
import java.util.List;

public class SolvePattern {

    static final int MAX_SOLUTIONS_TO_PRINT = 10;

    public static void main(String[] args) throws Exception {
        STGraph G = STLoader.fromJson(Path.of("C:/Users/rasri/IdeaProjects/Projet-CSP/src/main/java/stgraph4.json"));

        Path motifsPath = Path.of("C:/Users/rasri/IdeaProjects/Projet-CSP/src/main/java/Motifs/500_pairs_12_k-hop_32_N=4500_s=2.json");
        List<Pattern_M> patterns = MotifJsonLoader.loadPatterns(motifsPath);
        System.out.println("Motifs chargés: " + patterns.size());

        for (Pattern_M p : patterns) {
            System.out.println(p);
        }

    }
}
