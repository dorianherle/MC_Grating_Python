Welcome to MC_Grating_Python documentation!
===========================================

MC_Grating_Python was written in order to interface python with `MC Grating <https://mcgrating.com/>`_. This facilitates the creation of more complex geometries, optimizations and visualizations.
 
The code is in continous development. Currently it only works for the Crossed Grating codes. 

###############
Getting Started
###############

Download the `mc_grating_class <https://github.com/dorianherle/MC_Grating_Python/blob/main/mc_grating_class.py>`_ to the directory from which you would like to run the python script.


***********
First Simulation using 2D Geometry
***********
This tutorial will teach you how to run your first MC Grating simulation through python. It will include defining your geometry, setting up the scan, and retreiveing as well as visualizing the result.

We will be simulating the reflection from a periodic nanostructure (2D grating). The nanostructure consists of silicon nano-discs on an oxide substrate. 

.. image:: _static/periodic_nano_discs.*
   :align: center



Start by importing all necessary packages and python files (mc_grating_class):

.. code-block:: python

   # some standard python packages 
   import matplotlib.pyplot as plt
   import numpy as np
   # the python-MC Grating link 
   import mc_grating_class as mc
   

Define all the general simulation parameters:

.. code-block:: python

   # create mc_grating header
   gen = mc.general(orders_x = 7,orders_y= 7, single_wavelength=560)
 
Create the geometry (and define materials used):

.. code-block:: python

   # geometry 
   geo = mc.geometry(period_x=237, period_y=237)
   # Cover Layer
   geo.cover_material("Air (Special Formula)")

   # LAYER 1
   geo.layer(thickness = 100, sourrounding_material = "Air (Special Formula)")
   geo.circle(center = [0,0], radius = 50, material = "Silicon (Table)")
   
   # Substrate
   geo.substrate("Fused Silica (Sellmeier)")

let's create a wavelength scan in the visible range from 400nm to 700nm:

.. code-block:: python

   # scan
   scan = mc.scanning()
   scan.setting_wavelength_scan(start_w=400, end_w=700, number_of_points=100)
   

Finnaly, let's run the simulation and visualize the result

.. code-block:: python

   # run 
   run = mc.run_simulation()
   data = run.open_output(scan = "wavelength_range")

   # Visualize
   w = data[0]["WaveL"]
   r = data[0]["C[0,0].Pow"]
   plt.plot(w,r*100)
   plt.title("Reflection Spectra C[0,0].Pow")
   plt.xlabel("Wavelength (nm)")
   plt.ylabel("Reflection %")


.. image:: _static/reflection_spectra_nanostructure.*
   :align: center
   
***********
First Simulation using 3D Geometry (NEW)
***********

As of April 2021 it is now possible to define the geometry in an even easier way using 3D objects.
Let's see how the previous geometry can be defined much easier with this new capability:

Create the geometry (and define materials used):

.. code-block:: python

   # geometry 
   mc_obj = mc.object_3d_geometry(period_x=period, period_y=period)
   
   # cover layer
   mc_obj.cover_material("Air (Special Formula)")

   # CYLINDER
   mc_obj.cylinder(position=[0,0,0], radius=50, height=100, name = "cylinder_si", material = "Silicon (Table)")
   
   # substrate
   mc_obj.substrate("Fused Silica (Sellmeier)")

 
.. toctree::
   :maxdepth: 3
   
   licence
   help
 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
