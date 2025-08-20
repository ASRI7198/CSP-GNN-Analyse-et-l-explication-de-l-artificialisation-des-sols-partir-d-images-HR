package org.example;

import java.util.Arrays;

public class STGraph {
    public final int N;
    public final int[] classOf;
    public final int[] layerOf;
    public final int[] timeOf;
    public final int[][] spatialAdj;
    public final int[][] temporalAdj;

    public STGraph(int N, int[] classOf, int[] layerOf, int[] timeOf,
                   int[][] spatialAdj, int[][] temporalAdj) {
        this.N = N;
        this.classOf = classOf;
        this.layerOf = layerOf;
        this.timeOf = timeOf;
        this.spatialAdj = spatialAdj;
        this.temporalAdj = temporalAdj;
    }

    @Override public String toString() {
        return "STGraph{N=" + N
                + ", classOf=" + Arrays.toString(classOf)
                + ", layerOf=" + Arrays.toString(layerOf)
                + ", timeOf=" + Arrays.toString(timeOf) + "}";
    }
}