args = getArgument();
input = args;
open(input);

run("8-bit");
run("Subtract Background...", "rolling=10 light");
run("Gaussian Blur...", "sigma=1");
run("Enhance Contrast...", "saturated=0.35");

setAutoThreshold("Otsu dark");
run("Convert to Mask");

saveAs("PNG", input + ".tmp");
File.rename(input + ".png", input + ".tmp"); // Fix extension always replaced with .png

eval("script", "System.exit(0);");
