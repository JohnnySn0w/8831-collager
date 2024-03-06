# 88x31px geocities banner collager
## Bricolaging software for taking source images and converting them into assemblages of 88x31px banners from geocities archive

https://hellnet.work/8831

If the filehosting of the data zips goes down, the scraper.py script can be used, it's a lot slower though.

Otherwise, unzip the zip file, and run the convert script on whatever you want.

Steps:

1. load in all immages
2. Go through each image, and calculate mean color of image.
    - for animated images, there should also be a stddev calc, to determine if they are flashy. High stddev intervals means lots of variation, and therefore more likely to be a flashy animation.
3. Some images are absolutely massive. One at least is too large for me to process, causes a memory error. Don't use those.
4. Take in a source image, break into pixels.
5. Replace pixels with banners that have closest match in rgb value. Random pick
if identically close to 2 different banners.
6. optionally squanch banners to squares.
7. compose this all into one image, animation included.

### Example
![](./acraker2001_back_button.jpg)



https://github.com/JohnnySn0w/8831-collager/assets/33181572/c498a3bb-e21b-4e5d-b537-3cdc9fe1a816

