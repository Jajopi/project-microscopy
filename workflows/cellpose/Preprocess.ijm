args = getArgument();
parts = split(args, "|");
input = parts[0]; output = parts[1];
open(input);

run("8-bit");
run("Subtract Background...", "rolling=10 light");
run("Gaussian Blur...", "sigma=1");
run("Enhance Contrast...", "saturated=0.35");

saveAs("PNG", input + ".cellpose" + ".tmp");
File.rename(input + ".cellpose" + ".png", output); // Fix extension always replaced with .png

eval("script", "System.exit(0);");
