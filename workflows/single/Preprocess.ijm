args = getArgument();
parts = split(args, "|");
input = parts[0]; output = parts[1];
open(input);

run("8-bit");
run("Subtract Background...", "rolling=10 light");
run("Gaussian Blur...", "sigma=1");
run("Enhance Contrast...", "saturated=0.35");

setAutoThreshold("Otsu dark");
run("Convert to Mask");

run("Invert");
run("Watershed");
run("Invert");

saveAs("PNG", input + ".single" + ".tmp");
File.rename(input + ".single" + ".png", output); // Fix extension always replaced with .png

eval("script", "System.exit(0);");
