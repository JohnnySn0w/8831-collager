# 88x31px geocities banner collager
## Bricolaging software for taking source images and converting them into assemblages of 88x31px banners from geocities archive

https://hellnet.work/8831

## To run
### Step 1
If the filehosting of the data zips goes down, the scraper.py script can be used, it's a lot slower though.

Otherwise, grab the deduped zip file linked on the hellnet.work site. put it in the root of this repo.

### Step 2

```bash
python -m venv venv
```
on osx/linux:

```bash
source ./venv/bin/activate
```

on windows:

```powershell
./venv/Scripts/activate
```

and 

```
pip install -r requirements.txt
```

### Step 3

Pass the image you want to convert into a call to `image_converter.py`.

```bash
python image_converter.py imagefile.png
```

### Step 4
wait

### Step 5

done!


## Process

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

https://www.youtube.com/watch?v=8XRhzpTc_GA

