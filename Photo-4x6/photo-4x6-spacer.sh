#!/bin/bash

# 0. Install tools if needed
# sudo apt update
# sudo apt install imagemagick

# Step 1: Find width and height of input.png
read width height <<< $(identify -format "%w %h" input.png)

# Step 2: Calculate the smaller side
if [ "$width" -lt "$height" ]; then
  side=$width
else
  side=$height
fi

echo "Cropping to square size: ${side}x${side}"

# Step 3: Crop input.png into a square
convert input.png -crop ${side}x${side}+0+0 +repage cropped.png

# Step 4: Set DPI to 300
convert cropped.png -units PixelsPerInch -density 300 dpi_set.png

# Step 5: Resize to 600x600 pixels (for 2x2 inch at 300 DPI)
convert dpi_set.png -resize 600x600 resized.png

# Step 6: Create black spacers
convert -size 1x600 xc:black spacer_vert.png
convert -size 1201x1 xc:black spacer_horiz.png

# Step 7: Build rows using resized.png
montage resized.png spacer_vert.png resized.png -tile x1 -geometry +0+0 -background white row1.png
montage resized.png spacer_vert.png resized.png -tile x1 -geometry +0+0 -background white row2.png
montage resized.png spacer_vert.png resized.png -tile x1 -geometry +0+0 -background white row3.png

# Step 8: Stack rows
montage row1.png spacer_horiz.png row2.png spacer_horiz.png row3.png \
  -tile 1x -geometry +0+0 -background white final_temp.png

# Step 9: Set DPI to 300 for final 4x6 print
convert final_temp.png -units PixelsPerInch -density 300 final_4x6_printready.png

echo "✅ Created final_4x6_printready.png successfully!"

