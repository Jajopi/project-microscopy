args = getArgument();
parts = split(args, "|");
input = parts[0]; output = parts[1];
open(input);

clusterMinSize = 225;
clusterMaxSize = 10000;

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
"var paCells = new ParticleAnalyzer(options, measurements, rt, 25.0, " + clusterMinSize + ", 0.30, 1.00);" +
"paCells.analyze(imp);" +
"var cellCount = rt.size();" +
"for (var i = 0; i < cellCount; i++) rt.setValue('Class', i, 'cell');" +
"" +
"var paClusters = new ParticleAnalyzer(options, measurements, rt, " + clusterMinSize + ", " + clusterMaxSize + " , 0.1, 1.00);" +
"paClusters.analyze(imp);" +
"var totalCount = rt.size();" +
"for (var i = cellCount; i < totalCount; i++) rt.setValue('Class', i, 'cluster');" +
"" +
"rt.save('" + output + "');";
eval("script", code);

eval("script", "System.exit(0);");
