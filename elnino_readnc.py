# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 18:56:30 2017

@author: Gerardo A. Rivera Tello
"""
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.io import netcdf
import numpy as np
import os

#%%
def read_nc(nino_nc):
    data = np.zeros((len(nino_nc),59,84))
    time = []
    for j,dataset in enumerate(nino_nc):
        nc_file = netcdf.NetCDFFile(dataset,'r')
        time.append(nc_file.variables['Time'][0])
        sst_anomaly = np.copy(nc_file.variables['Sea_level_anomaly'][0,:])
        sst_anomaly[np.where(sst_anomaly==0.)]=np.nan
        data[j] = sst_anomaly
        nc_file.close
    lon,lat = np.meshgrid(nc_file.variables['Longitude'][:],nc_file.variables['Latitude'][:])
    return data,lat,lon,time

#%%
class Animated_map(object):
    def __init__(self,lat,lon,data,time):
        self.lat = lat
        self.lon = lon
        self.time = time
        self.data = np.ma.masked_array(data, np.isnan(data))
        
        self.fig, self.axis = plt.subplots(figsize=(20,10))

        self.moving_map = Basemap(projection = 'merc', resolution = 'l',
                llcrnrlat=self.lat.min()-1,urcrnrlat=self.lat.max()+1,
                llcrnrlon=self.lon.min()-1, urcrnrlon=self.lon.max()+1)
        self.moving_map.drawcoastlines(linewidth = 0.7)
        self.moving_map.drawparallels(np.arange(-90.0,90.0,5.0),
                                      labels = [1,0,0,0],linewidth=0.7)
        self.moving_map.drawmeridians(np.arange(-180.0,180.0,5.0),
                                      labels = [0,0,0,0],linewidth=0.5)
        self.moving_map.drawmeridians(np.arange(-180.0,180.0,10.0),
                                      labels = [0,0,0,1],linewidth=0.7)
        self.moving_map.drawcountries()
        self.moving_map.fillcontinents(color='0.8')
        x, y =self.moving_map(self.lon,self.lat)
        
        self.initial_cond = self.moving_map.pcolormesh(x,y,data[0],
                                                   vmin=np.nanmin(self.data[0]),
                                                   vmax=np.nanmax(self.data[0]),
                                                   cmap=plt.cm.jet)
#        self.cbar = self.moving_map.colorbar(self.initial_cond,location='bottom',size='10%',pad='15%')
#        self.cbar.set_label('Degrees C')

    def setup_plot(self):
        self.initial_cond.set_array([])
        return self.initial_cond

    def update(self,i):
        self.initial_cond.set_array(self.data[i][:-1,:-1].ravel())
        self.axis.set_title(self.time[i])
        print time[i]
        self.initial_cond.set_clim(np.array([np.nanmin(self.data[i]),np.nanmax(self.data[i])]))
        return self.initial_cond
    
    def animate(self):
        self.ani = animation.FuncAnimation(self.fig, self.update,frames=1204, interval=200, 
                                           init_func=self.setup_plot)
        self.ani.save('dynamic_images.mp4',fps=15)

#%%
if __name__ == "__main__":
    nc_files=[]
    for files in os.listdir(os.getcwd()):
        if files.endswith("nc"):
            nc_files.append(files)
    
    data, lat, lon, time = read_nc(nc_files)
    a = Animated_map(lat,lon,data,time)
    a.animate()