import math
import numpy as np
from matplotlib import pyplot as plt
import PIL

def images_rect(images, scale=1, labels=None):
    def get_rect_sides(i):    
        s = math.sqrt(i)
        a = math.ceil(s)
        b = int(s)
        b = b + 1 if i > a*b else b
        return b, a
    a, b = get_rect_sides(len(images))
    fig = plt.figure(figsize=(a*scale, b*scale))
    if labels is None:
        labels = [None] * len(images)
    for i, (im, label) in enumerate(zip(images, labels)):
        fig.add_subplot(a, b, i+1)
        plt.imshow(im)
        plt.axis('off')
        plt.title(label, y=-0.12)
    plt.tight_layout()