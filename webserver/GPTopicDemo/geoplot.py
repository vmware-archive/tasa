from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import os

data_folder = os.environ['DATA_FOLDER']+'/images/'

# lon_0 is central longitude of robinson projection.
# resolution = 'c' means use crude resolution coastlines.
m = Basemap(projection='robin',lon_0=0,resolution='c')
#set a background colour
m.drawmapboundary(fill_color='#85A6D9')


# draw coastlines, country boundaries, fill continents.
m.fillcontinents(color='white',lake_color='#85A6D9')
m.drawcoastlines(color='#6D5F47', linewidth=.4)
m.drawcountries(color='#6D5F47', linewidth=.4)



# draw lat/lon grid lines every 30 degrees.
m.drawmeridians(np.arange(-180, 180, 30), color='#bbbbbb')
m.drawparallels(np.arange(-90, 90, 30), color='#bbbbbb')


# lat/lon coordinates of top ten world cities
lats = [35.69,37.569,19.433,40.809,18.975,-6.175,-23.55,28.61,34.694,31.2]
lngs = [139.692,126.977,-99.133,-74.02,72.825,106.828,-46.633,77.23,135.502,121.5]
populations = [32.45,20.55,20.45,19.75,19.2,18.9,18.85,18.6,17.375,16.65] #millions


# compute the native map projection coordinates for cities
x,y = m(lngs,lats)

#scale populations to emphasise different relative pop sizes
s_populations = [p * p for p in populations]


#scatter scaled circles at the city locations
m.scatter(
    x,
    y,
    s=s_populations, #size
    c='blue', #color
    marker='o', #symbol
    alpha=0.25, #transparency
    zorder = 2, #plotting order
    )
    
    
# plot population labels of the ten cities.
for population, xpt, ypt in zip(populations, x, y):
    label_txt = int(round(population, 0)) #round to 0 dp and display as integer
    plt.text(
        xpt,
        ypt,
        label_txt,
        color = 'blue',
        size='small',
        horizontalalignment='center',
        verticalalignment='center',
        zorder = 3,
        )
        
#add a title and display the map on screen
plt.title('Top Ten World Metropolitan Areas By Population')
plt.savefig(data_folder+'geo.png')