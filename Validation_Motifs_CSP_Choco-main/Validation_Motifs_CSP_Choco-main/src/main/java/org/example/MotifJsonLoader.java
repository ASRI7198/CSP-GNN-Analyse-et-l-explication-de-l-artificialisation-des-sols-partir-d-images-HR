package org.example;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.nio.file.Files;
import java.nio.file.Path;
import java.text.Normalizer;
import java.util.*;



public final class MotifJsonLoader {

    private static String norm(String s) {
        if (s == null) return "";
        return Normalizer.normalize(s, Normalizer.Form.NFD)
                .replaceAll("\\p{M}", "")
                .toLowerCase(Locale.ROOT)
                .trim();
    }

    private static EdgeType mapRelationToType(String raw) {
        String t = norm(raw);
        switch (t) {
            case "adjacence":   return EdgeType.SPATIAL;
            case "derivation":
            case "continuation":
            case "scission":
            case "fusion":      return EdgeType.TEMPORAL;
            default:            return null;
        }
    }

    private static String[] splitOnce(String s, String sep) {
        int k = s.indexOf(sep);
        if (k < 0) return null;
        return new String[]{ s.substring(0, k), s.substring(k + sep.length()) };
    }

    private static final class MiniNode {
        final String node;
        final String date;
        MiniNode(String node, String date) { this.node = node; this.date = date; }
    }

    private static MiniNode parseNodeDate(String text) {
        String t = text.trim();
        String[] parts = t.split("/");
        if (parts.length < 3) return null;
        String node = parts[0].trim();
        String yyyy = parts[1].trim();
        String mm   = parts[2].trim();
        if (yyyy.length() != 4 || mm.length() != 2) return null;
        return new MiniNode(node, yyyy + "/" + mm);
    }

    private static final class ParsedRel {
        final String leftKey;
        final String rightKey;
        final EdgeType type;
        ParsedRel(String l, String r, EdgeType t){ leftKey=l; rightKey=r; type=t; }
    }

    private static ParsedRel parseRelationLine(String line, boolean debug, int motifIdx) {
        if (line == null) return null;

        String raw = line
                .replace('\u2014','-')   // —
                .replace('\u2013','-')   // –
                .replace("\u2192","->"); // →  =>  ->

        String[] p1 = splitOnce(raw, "---");
        if (p1 == null) { if (debug) System.out.println("[REL] motif " + motifIdx + " : manque '---' : " + line); return null; }
        String lhs = p1[0];
        String rest = p1[1];

        String[] p2 = splitOnce(rest, "--->");
        if (p2 == null) { p2 = splitOnce(rest, "->"); }
        if (p2 == null) { if (debug) System.out.println("[REL] motif " + motifIdx + " : manque '--->'/'->' : " + line); return null; }

        String label = p2[0].trim();
        String rhs   = p2[1];

        String rhsClean = rhs;
        String rhsNorm = norm(rhs);
        int k = rhsNorm.indexOf("avec score");
        if (k >= 0) {
            int approxIdx = Math.max(0, rhs.toLowerCase(Locale.ROOT).indexOf("avec"));
            rhsClean = approxIdx > 0 ? rhs.substring(0, approxIdx) : rhs;
        }

        MiniNode L = parseNodeDate(lhs);
        MiniNode R = parseNodeDate(rhsClean);
        if (L == null || R == null) { if (debug) System.out.println("[REL] motif " + motifIdx + " : parse Node/Date échoué : " + line); return null; }

        EdgeType type = mapRelationToType(label);
        if (type == null) { if (debug) System.out.println("[REL] motif " + motifIdx + " : type inconnu: '" + label + "'"); return null; }

        return new ParsedRel(L.node + "/" + L.date, R.node + "/" + R.date, type);
    }

    public static List<Pattern_M> loadPatterns(Path jsonFile) throws Exception {
        return loadPatterns(jsonFile, false);
    }

    public static List<Pattern_M> loadPatterns(Path jsonFile, boolean debug) throws Exception {
        byte[] bytes = Files.readAllBytes(jsonFile);
        ObjectMapper om = new ObjectMapper();
        JsonNode root = om.readTree(bytes);

        if (!root.isArray()) {
            throw new IllegalArgumentException("Le JSON des motifs doit être un tableau de motifs.");
        }

        List<Pattern_M> out = new ArrayList<>();
        int motifIdx = 0;

        for (JsonNode motifArr : root) {
            motifIdx++;
            if (!motifArr.isArray() || motifArr.size() < 2) {
                if (debug) System.out.println("[SKIP] motif " + motifIdx + " : pas assez d'éléments");
                continue;
            }

            JsonNode meta = motifArr.get(0);

            List<Integer> motifClass = new ArrayList<>();
            Map<String,Integer> localIndex = new HashMap<>();
            List<String> nodeKeysList = new ArrayList<>();
            List<Integer> nodeTimes = new ArrayList<>();

            for (int i = 1; i < motifArr.size(); i++) {
                JsonNode n = motifArr.get(i);
                if (!n.has("Node") || !n.has("Date") || !n.has("Classe_int")) continue;

                String nodeId = n.get("Node").asText();
                String date   = n.get("Date").asText();
                int clazz     = n.get("Classe_int").asInt();

                int u = motifClass.size();
                motifClass.add(clazz);
                localIndex.put(nodeId + "/" + date, u);
                nodeKeysList.add(nodeId + "/" + date);
                int yyyymm = Integer.parseInt(date.substring(0,4) + date.substring(5,7));
                nodeTimes.add(yyyymm);

            }

            List<Edge> edges = new ArrayList<>();
            if (meta.has("Relation") && meta.get("Relation").isArray()) {
                for (JsonNode relLineNode : meta.get("Relation")) {
                    String line = relLineNode.asText();
                    ParsedRel pr = parseRelationLine(line, debug, motifIdx);
                    if (pr == null) continue;

                    Integer u = localIndex.get(pr.leftKey);
                    Integer v = localIndex.get(pr.rightKey);
                    if (u == null || v == null) {
                        if (debug) System.out.println("[REL] motif " + motifIdx + " : pair inconnue " + pr.leftKey + " -> " + pr.rightKey);
                        continue;
                    }
                    edges.add(new Edge(u, v, pr.type));
                }
            } else {
                if (debug) System.out.println("[WARN] motif " + motifIdx + " : champ 'Relation' manquant ou non tableau");
            }

            int[] motifClassArr = motifClass.stream().mapToInt(Integer::intValue).toArray();
            String[] nodeKeys = nodeKeysList.toArray(new String[0]);
            Pattern_M P = new Pattern_M(motifClassArr, edges, nodeKeys);

            if (debug) {
                System.out.printf("[OK] motif %d : U=%d, edges=%d%n", motifIdx, P.U, P.edges.size());
                System.out.print(P);
            }
            out.add(P);
        }
        return out;
    }
}