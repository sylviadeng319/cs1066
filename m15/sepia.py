### m15/sepia.py

from PIL import Image

imfile = 'images/' + input('Filename of input image: ')

with Image.open(imfile) as im:
    im = im.convert('RGB') # convert to RGB if not already

    for i in range(im.size[0]):
        for j in range(im.size[1]):
            pixel = im.getpixel((i,j))

            # Give the pixel a sepia tone
            r, g, b = pixel
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            r = 255 if tr > 255 else tr
            g = 255 if tg > 255 else tg
            b = 255 if tb > 255 else tb
            new_pixel = (r, g, b)

            im.putpixel((i,j), new_pixel)

    im.save('images/sepia.png')
