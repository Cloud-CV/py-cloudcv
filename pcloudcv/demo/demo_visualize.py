__author__ = 'dexter'
import os
import utility.job as job
import json
import collections
import matplotlib.pyplot as plt

def visualize(ImagePath, scores):
    import sys
    from PIL import Image
    from PIL import ImageFont
    from PIL import ImageDraw

    IMAGE_FILE = ImagePath
    BGimg = Image.new('RGB', (277, 355))
    img = Image.open(IMAGE_FILE)
    imgResized = img.resize((277, 277))
    BGimg.paste(imgResized, (0, 0))
    draw = ImageDraw.Draw(BGimg)
    font = ImageFont.truetype("New_Press.ttf", 16)
    scoresKeys = scores.keys()
    scoresValues = scores.values()

    sorted_scores = collections.OrderedDict(sorted(scores.items(), key=lambda t: t[1]))

    m = 335
    colors = (255, 255, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255)

    k = 0


    for i, j in sorted_scores.items():
        draw.text((5, m), str(i), colors[k], font=font)
        draw.text((220, m), str(j)[:6], colors[k], font=font)
        k = (k + 1) % 5
        m = m - 15


    BGimg.save('sample-out-BG.JPEG')
    BGimg.show()

def str2dict(str):
    return json.loads(str)

#Visualization Code for Classifications
def visualize_classification(str):
    output_dict = str2dict(str)
    for k, v in output_dict.iteritems():
        imagepath = os.path.join(job.job.imagepath, k)
        scores = output_dict[k]
        visualize(imagepath, scores)


