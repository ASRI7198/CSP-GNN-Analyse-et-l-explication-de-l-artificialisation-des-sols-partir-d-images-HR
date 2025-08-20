package org.example;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.nio.file.*;
import java.util.Map;



record JsonData(int N, int[] classOf, int[] layerOf, int[] timeOf,
                int[][] spatialAdj, int[][] temporalAdj, Map<String,Integer> idMap) {}

public final class STLoader {
    public static STGraph fromJson(Path path) throws Exception {
        ObjectMapper om = new ObjectMapper();
        JsonData j = om.readValue(Files.readAllBytes(path), JsonData.class);
        return new STGraph(j.N(), j.classOf(), j.layerOf(), j.timeOf(), j.spatialAdj(), j.temporalAdj());
    }
}