#PHOTO VISA AUTO

#0 Take a Square Photo in iPhone
#Long press on the Photo and save it as input.png on Mac

# 0. Install tools if needed
#sudo apt update
#sudo apt install imagemagick

# 1. Crop the input.png to 2776 x 2776 pixels
# Crop Right Side (offset 77 pixels from left)
convert input.png -crop 2776x2776+77+0 +repage cropped.png

# OR 
# Crop Left Side (start at 0,0 and just take 2776x2776 area)
# convert input.png -crop 2776x2776+0+0 +repage cropped.png

# 2. Set the DPI to 300
convert cropped.png -units PixelsPerInch -density 300 dpi_set.png

# 3. Resize to 600x600 pixels (for 2x2 inch at 300 DPI)
convert dpi_set.png -resize 600x600 resized.png

# 4. Arrange into a 2x3 grid
montage resized.png resized.png resized.png resized.png resized.png resized.png \
  -tile 2x3 \
  -geometry 600x600+0+0 \
  -background white \
  -gravity center \
  final_4x6.png

# 5. Set the final 4x6 to be 300 DPI
convert final_4x6.png -units PixelsPerInch -density 300 final_4x6_printready.png

