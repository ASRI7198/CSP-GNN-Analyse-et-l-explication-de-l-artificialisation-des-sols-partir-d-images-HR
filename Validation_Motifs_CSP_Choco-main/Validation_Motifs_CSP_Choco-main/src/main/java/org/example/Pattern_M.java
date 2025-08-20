package org.example;

import java.util.List;

public class Pattern_M {
    public final int U;
    public final int[] motifClass;
    public final List<Edge> edges;
    public final String[] nodeKeys;

    public Pattern_M(int[] motifClass, List<Edge> edges, String[] nodeKeys) {
        this.motifClass = motifClass;
        this.edges = edges;
        this.nodeKeys = nodeKeys;
        this.U = motifClass.length;
    }

    private String nodeLabel(int u) {
        return (nodeKeys != null && u >= 0 && u < nodeKeys.length) ? nodeKeys[u] : ("u"+u);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("Pattern{U=").append(U)
                .append(", edges=").append(edges.size()).append("}\n");

        int leftColWidth = 12;
        if (nodeKeys != null && nodeKeys.length > 0) {
            for (String k : nodeKeys) if (k != null) leftColWidth = Math.max(leftColWidth, k.length());
        }

        for (Edge e : edges) {
            String left  = (nodeKeys != null && e.u >= 0 && e.u < nodeKeys.length) ? nodeKeys[e.u] : ("u"+e.u);
            String right = (nodeKeys != null && e.v >= 0 && e.v < nodeKeys.length) ? nodeKeys[e.v] : ("u"+e.v);

            String typeStr = (e.type == EdgeType.SPATIAL) ? "SPATIAL" : "TEMPOREL";

            sb.append(String.format("%-" + leftColWidth + "s  %-9s  %s%n", left, typeStr, right));
        }
        return sb.toString();
    }
}