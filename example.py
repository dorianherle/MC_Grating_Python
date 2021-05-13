# -*- coding: utf-8 -*-
"""
Created on Thu May 13 13:57:57 2021

@author: Dorian Herle
"""
# some standard python packages
import matplotlib.pyplot as plt
import numpy as np
# the python-MC Grating link
import mc_grating_class as mc


# create mc_grating header
gen = mc.general(orders_x = 7,orders_y= 7, single_wavelength=560)
# geometry
mc_obj = mc.object_3d_geometry(period_x=237, period_y=237)
# cover layer
mc_obj.cover_material("Air (Special Formula)")
# CYLINDER
mc_obj.cylinder(position=[0,0,0], radius=50, height=100, name = "cylinder_si", material = "Silicon (Table)")
# substrate
mc_obj.substrate("Fused Silica (Sellmeier)")
# scan
scan = mc.scanning()
scan.setting_wavelength_scan(start_w=400, end_w=700, number_of_points=100)
# run
run = mc.run_simulation(path_name = "example")
data = run.open_output()



# Plot the total reflection

def total_power(fixed_wavelength_data):
    """
    Extract the total cover reflection or substrate transmission
    """
    try:
        sum_s_cov = np.sum(fixed_wavelength_data["Cover orders"]["Power (s)"])
        sum_p_cov = np.sum(fixed_wavelength_data["Cover orders"]["Power (p)"])
        total_cov = sum_s_cov+sum_p_cov
    except:
        #print("no cover orders")
        total_cov = 0
        
    try:
        sum_s_sub = np.sum(fixed_wavelength_data["Substrate orders"]["Power (s)"])
        sum_p_sub = np.sum(fixed_wavelength_data["Substrate orders"]["Power (p)"])
        total_sub = sum_s_sub+sum_p_sub
    except:
        #print("no substrate orders")
        total_sub = 0
        
    return [total_cov, total_sub]



wavelengths = [int(w) for w in data.keys()]
reflection = [total_power(data[w])[0] for w in data.keys()]
plt.plot(wavelengths,reflection)
plt.title("Reflection Spectra C[0,0].Pow")
plt.xlabel("Wavelength (nm)")
plt.ylabel("Reflection")