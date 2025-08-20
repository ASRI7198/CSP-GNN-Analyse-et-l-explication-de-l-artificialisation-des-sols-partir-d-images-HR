package org.example;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;

public class BuildResult {
    public final Model model;
    public final IntVar[] X;
    public BuildResult(Model model, IntVar[] X) { this.model = model; this.X = X; }
}