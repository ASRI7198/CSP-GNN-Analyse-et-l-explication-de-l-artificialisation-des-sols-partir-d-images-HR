package org.example;

public class Edge {
    public final int u, v;
    public final EdgeType type;
    public final String label;

    public Edge(int u, int v, EdgeType type) {
        this(u, v, type, null);
    }
    public Edge(int u, int v, EdgeType type, String label) {
        this.u = u; this.v = v; this.type = type; this.label = label;
    }

    @Override public String toString() {
        String t = (label != null ? label : (type == EdgeType.SPATIAL ? "Adjacence" : "Temporel"));
        return u + " --- " + t + " ---> " + v;
    }
}