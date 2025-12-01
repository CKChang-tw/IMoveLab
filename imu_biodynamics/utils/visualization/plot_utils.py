# name: plot_utils.py


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm, gaussian_kde


def plot_box(ax, data, position, color, width, alpha, side = 'left'):
    box = ax.boxplot(data, positions = [position],
                     widths = width,
                     vert = True,
                     patch_artist = True,
                     boxprops = dict(facecolor = color, alpha = alpha),
                     capprops = dict(visible = False),
                     showmeans = True,
                     meanprops = dict(marker = 'x', markeredgecolor = '#F5EE9E', ms = 4),
                     # whiskerprops = dict(x = get_xdata()),
                     medianprops = dict(color = '#4A4063', linewidth = 2.5),
                    #  flierprops = dict(marker = '+', markerfacecolor = '#9F84BD', markeredgecolor = '#9F84BD', ms = 4), 
                     showfliers = False,
                     zorder = 1)
    
    for whisker in box['whiskers']:
        x = whisker.get_xdata()
        if side == 'left':
            whisker.set_xdata([x[0] - width/2, x[1] - width/2])
        else:
            whisker.set_xdata([x[0] + width/2, x[1] + width/2])
        
    for flier in box['fliers']:
        x = flier.get_xdata()
        if side == 'left':
            flier.set_xdata(x - width/2)
        else:
            flier.set_xdata(x + width/2)

def plot_data_point(ax, data, color, position):
    # generate random numbers around position
    n = len(data)
    x = np.random.normal(position, 0.02, n)
    ax.scatter(x, data, color = color, edgecolor = 'none', alpha = 0.5, s = 25, marker = '.')

    return x

def plot_gauss(ax, data, color, position, alpha, scale):
    mu, std = norm.fit(data)
    y = np.linspace(mu - 3*std, mu + 3*std, 100)
    p = norm.pdf(y, mu, std)
    ax.plot(scale*p + position, y, color = color, alpha = alpha, linewidth = 1)

def plot_density(ax, data, position, color, scale, covf, side = 'left'):
    mu, std = norm.fit(data)

    density = gaussian_kde(data)
    ys = np.linspace(mu - 3*std, mu + 3*std, 100)
    density.covariance_factor = lambda : covf
    density._compute_covariance()

    if side == 'left':
        # ax.plot(scale*density(ys) + position, ys, color = color, lw = 1.4, zorder = 1)
        ax.fill_betweenx(ys, position, scale*density(ys) + position, color = color, alpha = 0.2, edgecolor = None, zorder = 0)
    else:
        # ax.plot(position, scale*density(ys) + ys, color = color, lw = 1.4, zorder = 1)
        ax.fill_betweenx(ys, position, -scale*density(ys) + position, color = color, alpha = 0.2, edgecolor = None, zorder = 0)
    
def label_diff(ax, i, j, p, alpha_bon, height, font_size = 11, color = '#7D7C84', range = [0, 15], s_pos = 'top'):
    if p < alpha_bon:
        text = '*'
    else:
        text = 'ns'

    height = height*(range[1] - range[0]) + range[0]

    if text == 'ns':
        askterisk_v = 0.03*(range[1] - range[0])
    else:
        askterisk_v = 0.01*(range[1] - range[0])
    bar_v       = 0.015*(range[1] - range[0])

    ax.hlines(height, i, j, color = color, lw = 0.5)
    if s_pos == 'top':
        ax.vlines(i, height, height - bar_v, color = color, lw = 0.5)
        ax.vlines(j, height, height - bar_v, color = color, lw = 0.5)
    else:
        ax.vlines(i, height, height + bar_v, color = color, lw = 0.5)
        ax.vlines(j, height, height + bar_v, color = color, lw = 0.5)
    ax.annotate(text, xy = ((i + j)/2, height + askterisk_v), zorder = 10, ha = 'center', va = 'center', fontsize = font_size, color = color)



# def plot_box(ax, data, position, color, width, alpha, side = 'mid', no_box = False, label = None):
#     box = ax.boxplot(data, positions = [position],
#                      widths = width,
#                      vert = True,
#                      patch_artist = True,
#                      boxprops = dict(facecolor = color, alpha = alpha, lw = 0.5, edgecolor = 'none'),
#                      capprops = dict(visible = False),
#                      showmeans = True,
#                     #  meanprops = dict(marker = 'x', markeredgecolor = '#F5EE9E', ms = 4),
#                     #  meanprops = dict(marker = 'x', markeredgecolor = '#7D4600', ms = 4),
#                     meanprops = dict(marker = 'o', markerfacecolor = 'none', markeredgecolor = 'k', ms = 4.5, alpha = 0.7),
#                      # whiskerprops = dict(x = get_xdata()),
#                     #  medianprops = dict(color = '#4A4063', linewidth = 2.5),
#                     medianprops = dict(color = 'k', linewidth = 0.8, alpha = 0.7),
#                     showfliers = False,
#                     # whis = 0,
#                      flierprops = dict(marker = '+', markerfacecolor = color, markeredgecolor = color, ms = 5), 
#                      label = [label] if label is not None else [''],
#                      zorder = 1)
    
#     whisker_range = []
#     toggle = False
#     for whisker in box['whiskers']:
#         x = whisker.get_xdata()
#         if side == 'left':
#             var_position = x[0] - width/2
#             whisker.set_xdata([x[0] - width/2, x[1] - width/2])
#         elif side == 'right':
#             var_position = x[0] + width/2
#             whisker.set_xdata([x[0] + width/2, x[1] + width/2])
#         else:
#             var_position = x[0]

#         if toggle:
#             whisker_range.append(max(whisker.get_ydata()))
#         else:
#             whisker_range.append(min(whisker.get_ydata()))

#         whisker.set_visible(False)
        
#         toggle = not toggle

#     if no_box:
#         var_position = position
#     ax.vlines(var_position, whisker_range[0], whisker_range[1], color = '#353238', lw = 0.8, alpha = 1, zorder = 2)
        
#     if no_box:
#         for patch in box['boxes']:
#             patch.set_visible(False)
#         for median in box['medians']:
#             median.set_visible(False)
#         for mean in box['means']:
#             mean.set_visible(False)
#     # for flier in box['fliers']:
#     #     x = flier.get_xdata()
#     #     if side == 'left':
#     #         flier.set_xdata(x - width/2)
#     #     elif side == 'right':
#     #         flier.set_xdata(x + width/2)
#     #     else:
#     #         pass

# def plot_data_point(ax, data, color, position, marker = '.', size = 40):
#     # generate random numbers around position
#     n = len(data)
#     x = np.random.normal(position, 0.01, n)

#     # print(marker)

#     if marker == '+':
#         ax.scatter(x, data, facecolor = color, alpha = 0.7, s = size, marker = marker, zorder = 1)
#     else:
#         ax.scatter(x, data, color = color, alpha = 0.7, s = size, edgecolor = 'none', marker = marker, zorder = 1)

#     return x












