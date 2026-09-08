args = getArgument();
parts = split(args, "|");
input = parts[0]; output = parts[1];
open(input);

run("Set Measurements...", "area centroid perimeter bounding shape feret's redirect=None decimal=3");

//run("Analyze Particles...", "size=25-Infinity circularity=0.30-1.00 show=Outlines display exclude clear include add");
// Function is broken in headless mode, agent rewrite:
code = "" +
"var imp = WindowManager.getCurrentImage();" +
"imp.getProcessor().setThreshold(0, 128, ImageProcessor.NO_LUT_UPDATE);" +
"var rt = new ResultsTable();" +
"var measurements = Measurements.AREA | Measurements.CENTROID | Measurements.PERIMETER | Measurements.RECT | Measurements.SHAPE_DESCRIPTORS | Measurements.FERET;" +
"var options = ParticleAnalyzer.EXCLUDE_EDGE_PARTICLES | ParticleAnalyzer.INCLUDE_HOLES | ParticleAnalyzer.ADD_TO_MANAGER;" +
"" +
"var pa = new ParticleAnalyzer(options, measurements, rt, 25.0, 150.0, 0.30, 1.00);" +
"pa.analyze(imp);" +
"" +
"rt.save('" + output + "');";
eval("script", code);

eval("script", "System.exit(0);");
