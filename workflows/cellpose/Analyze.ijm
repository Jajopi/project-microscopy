args = getArgument();
parts = split(args, "|");
input = parts[0]; output = parts[1];
open(input);

cellposeEnvPath = "/home/janci/skola/4/microscopy/envs/microscopy";
cellposeEnvType = "conda";
cellposeModel = "cyto3";

cellposeDiameter = 11;
cellposeCh1 = 0;
cellposeCh2 = 0;

// Workaround for headless mode, agent rewrite:
code = "" +
"var tmpDir = java.nio.file.Files.createTempDirectory('cellpose_').toFile();" +
"var imageFile = new java.io.File(tmpDir, 'image.tif');" +
"var fs = new FileSaver(WindowManager.getCurrentImage());" +
"fs.saveAsTiff(imageFile.getAbsolutePath());" +
"" +
"var CellposeTaskSettings = Java.type('ch.epfl.biop.wrappers.cellpose.CellposeTaskSettings');" +
"var DefaultCellposeTask = Java.type('ch.epfl.biop.wrappers.cellpose.DefaultCellposeTask');" +
"var settings = new CellposeTaskSettings();" +
"settings.setEnvPath('" + cellposeEnvPath + "');" +
"settings.setEnvType('" + cellposeEnvType + "');" +
"settings.setDatasetDir(tmpDir.getAbsolutePath());" +
"settings.setModel('" + cellposeModel + "');" +
"settings.setDiameter(" + cellposeDiameter + ");" +
"settings.setChannel1(" + cellposeCh1 + ");" +
"settings.setChannel2(" + cellposeCh2 + ");" +
"settings.setAdditionalFlags('');" +
"" +
"var task = new DefaultCellposeTask();" +
"task.setSettings(settings);" +
"task.run();" +
"" +
"var maskFile = new java.io.File(tmpDir, 'image_cp_masks.tif');" +
"var labelImp = new ImagePlus(maskFile.getAbsolutePath());" +
"var ip = labelImp.getProcessor().convertToFloat();" +
"var w = ip.getWidth(), h = ip.getHeight();" +
"var pixels = ip.getPixels();" +
"var maxLabel = 0;" +
"for (var i = 0; i < pixels.length; i++) { var v = Math.round(pixels[i]); if (v > maxLabel) maxLabel = v; }" +
"" +
"var count = new Array(maxLabel + 1);" +
"var sumX = new Array(maxLabel + 1);" +
"var sumY = new Array(maxLabel + 1);" +
"var minX = new Array(maxLabel + 1);" +
"var maxX = new Array(maxLabel + 1);" +
"var minY = new Array(maxLabel + 1);" +
"var maxY = new Array(maxLabel + 1);" +
"for (var i = 0; i <= maxLabel; i++) {" +
"    count[i] = 0; sumX[i] = 0; sumY[i] = 0;" +
"    minX[i] = Infinity; maxX[i] = -1; minY[i] = Infinity; maxY[i] = -1;" +
"}" +
"" +
"for (var y = 0; y < h; y++) {" +
"    var rowOff = y * w;" +
"    for (var x = 0; x < w; x++) {" +
"        var v = Math.round(pixels[rowOff + x]);" +
"        if (v == 0) continue;" +
"        count[v]++; sumX[v] += x; sumY[v] += y;" +
"        if (x < minX[v]) minX[v] = x;" +
"        if (x > maxX[v]) maxX[v] = x;" +
"        if (y < minY[v]) minY[v] = y;" +
"        if (y > maxY[v]) maxY[v] = y;" +
"    }" +
"}" +
"" +
"var rt = new ResultsTable();" +
"for (var v = 1; v <= maxLabel; v++) {" +
"    if (count[v] == 0) continue;" +
"    rt.incrementCounter();" +
"    rt.addValue('Area', count[v]);" +
"    rt.addValue('X', sumX[v] / count[v]);" +
"    rt.addValue('Y', sumY[v] / count[v]);" +
"    rt.addValue('Perim.', 0);" +
"    rt.addValue('BX', minX[v]);" +
"    rt.addValue('BY', minY[v]);" +
"    rt.addValue('Width', maxX[v] - minX[v] + 1);" +
"    rt.addValue('Height', maxY[v] - minY[v] + 1);" +
"}" +
"rt.save('" + output + "');" +
"" +
"labelImp.close();" +
"var tmpFiles = tmpDir.listFiles();" +
"for (var i = 0; i < tmpFiles.length; i++) tmpFiles[i].delete();" +
"tmpDir.delete();";
eval("script", code);

eval("script", "System.exit(0);");
