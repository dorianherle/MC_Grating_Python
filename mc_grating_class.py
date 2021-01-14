# -*- coding: utf-8 -*-
"""
@author: Dorian Herle
"""

import os
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import colour
colour.utilities.filter_warnings(True, False)
from matplotlib.patches import Rectangle
import re
import time
from os import path


class general():
    
    def __init__(self,\
                 orders_x=17,orders_y=17,\
                 single_wavelength=400,\
                 polarization_state=0,\
                 polarization_phase = 0,\
                 angle_n = 0,\
                 angle_p = 0
                 ):
    
        

        self.orders_x = orders_x
        self.orders_y = orders_y
        self.single_wavelength = single_wavelength
        self.polarization_state = 0
        self.polarization_phase = 0
        self.angle_n = angle_n
        self.angle_p = angle_p
        

        # CREATE HEADER as class variabel
        general.header = \
        str(self.orders_x) + "\t" + "Number of Modes X" + "\n" +\
        str(self.orders_y) + "\t" + "Number of Modes Y" + "\n" + \
        "PERIOD_X" + "\t" + "X-Period, nm" + "\n"  +\
        "PERIOD_Y" + "\t" + "Y-Period, nm" + "\n" +\
        str(self.single_wavelength ) + "\t" + "Wavelength, nm" + "\n"  +\
        str(self.polarization_state) + "\t" + "Pol State, deg" + "\n" +\
        str(self.polarization_phase)+ "\t" + "Pol phase, def" + "\n" +\
        str(self.angle_n)+ "\t" + "AngleN, deg (Cover, Plane Base)" + "\n" +\
        str(self.angle_p)+ "\t" + "AngleP, deg (Cover, Plane Base)" + "\n" 
        
        


class geometry(general):
        
    
    def __init__(self, period_x, period_y):
        
        # Initalize
        self.counting_layers = 0
        self.counting_pillars = 0
        
        # Period
        self.period_X = period_x
        self.period_Y = period_y
        
        # Get MC Grating Header File from general class
        self.header = general.header
        # Update mc grating header file
        self.header = self.header.replace('PERIOD_X',str(self.period_X))
        self.header = self.header.replace('PERIOD_Y',str(self.period_Y))
        
        # Initialize Geometry script as class variabel
        geometry.mc_grating_geometry = ""
    
    
    def save_to_temp(self,text):
        """
        Saving to a temproary text file
        """
        geometry.mc_grating_geometry += text 
        
        
    def cover_material(self, material):
        cover_material = \
        "1" + "\t" + "0" + "\t" + "Eps.Re; Eps.Im; Cover; Material:" + " " + material + "\n"
        self.save_to_temp(cover_material)
       
    
    def layer(self, thickness, sourrounding_material):
        # If a new layer is defined -> Add the number of pillars used for the old layer 
        # Open the Temp file -> Get the text document -> Replace NUMBER_OF_PILLARS with self.counting_pillars
        # Delete old Temp file -> Create new temp file
        if self.counting_layers > 0: 
        
            # Replace NUMBER_OF_PILLARS
            document = self.mc_grating_geometry.replace('NUMBER_OF_PILLARS',str(self.counting_pillars))

            # Delete old temp file and create new one
            self.mc_grating_geometry = document
            
        # Reset Counting Pillars
        self.counting_pillars = 0
        
        # Increase counting layer variable
        self.counting_layers += 1
        
        layer_header = \
        str(thickness) + "\t" +  "NUMBER_OF_PILLARS" + "\t" + "Layer[" + str(self.counting_layers) +"]: Thickness, nm; Number of Pillars" + "\n" \
        "1" + "\t" + "0" + "\t" + "Base" + "\t" + "Eps.Re; Eps.Im; Material:" + " " + sourrounding_material + "\n" \
        
        self.save_to_temp(layer_header)
        
        
    def circle(self, center, radius, material):
        if self.counting_layers:     # don't count unless a layer was defined
            self.counting_pillars += 1
            
        number_points = 2
        cX,cY = center
        # MC Grating Repeats Geometries where a point is negative
        # Therefore the centers have to be displaced to the middle of a unit cetl
        cX = cX+self.period_X/2
        cY = cY+self.period_Y/2
        
        # Getting the points of the sourrounding rectangle 
        x11 = (cX-radius)/self.period_X
        y12 = (cY-radius)/self.period_Y
        x21 = (cX+radius)/self.period_X
        y22 = (cY+radius)/self.period_Y
        
        points = [[x11,y12],[x21,y22]]
        
        circle = \
        '1' +   '\t' + '0' + '\t' + str(number_points) + '\t' + 'Eps.Re; Eps.Im; Npoints of Pillar[' + str(self.counting_pillars) + ']; Material:' + ' ' + material + "\n" \
        
        for i,point in enumerate(points):
            i += 1
            circle = circle + \
            str(point[0]) + "\t" + str(point[1]) + "\t" + "x[" + str(i) + "]/(X-Period); y[" + str(i) + "]/(Y-Period)" + "\n" 

        
        self.save_to_temp(circle)
      

    
        
    
    def substrate(self, material):
        substrate = \
        "1" + "\t" + "0" + "\t" + "Eps.Re; Eps.Im; Substrate;; Material:" + " " + material + "\n"
        
        self.save_to_temp(substrate)
        

        # Replace NUMBER_OF_PILLARS with self.counting_pillars
        data = self.mc_grating_geometry.replace("NUMBER_OF_PILLARS", str(self.counting_pillars))
        geometry.mc_grating_geometry = data
        
        
        
        ## COMBINR HEADER AND GEOMETRY 
        self.finish_mc_grating_geom_script()
        
        
    def finish_mc_grating_geom_script(self):
        geometry.mc_grating_geometry = self.header + str(self.counting_layers) + "\t" + "Number of Layers" + "\n"  + geometry.mc_grating_geometry
    

    def export_geo(self):
        return geometry.mc_grating_geometry


class scanning(geometry):
    
    def __init__(self):
        
        # Initialize scanning
        scanning.document = ""
        # Initalize scan type
        scanning.type = 0
        # 0 wavelength range scan
        # 1 single wavlength scan
        
        # Get Geometry document
        self.geo = geometry.mc_grating_geometry
        
        # get numbers of layers
        number_of_layers = int(self.geo.split("Number of Layers")[0].strip().split("\n")[-1])
    
        
        settings_top = """
 Settings For FMM Crossed
true                UsingNF
false               UsingSmooth
0                   SmoothStart
0                   SmoothWidth
true                Background Calculation
false               Memory Consumption
false               Calculation Direction From Substrate to Cover
Y                   Number of Modes Correction
3                   Calculation Priority
true                Cover Diffraction Orders
false               Substrate Diffraction Orders
ORDER_C_X                   ORDER_C_Y                   X,Y Cover Order
ORDER_S_X                   ORDER_S_Y                   X,Y Substrate Order    
0                   0                   MinMax X Cover Order
0                   0                   MinMax Y Cover Order
0                   0                   MinMax X Substrate Order
0                   0                   MinMax Y Substrate Order
P                   Scanning Output Format: Power; Amplitude (Re,Im); Amplitude (Mod,Ph)
true                Diffraction Angle
%10.5g              Decimal Digits Format
WaveL               String of Scanning Parameter
ROW_SCANNING_PARAMETER                   Row Scanning Parameter
NUMBER_OF_COLUMN_POINTS                  Nubmber of Column Points -1
0                   0                   Range of Scanning AngleN
0                   0                   Range of Scanning AngleP
137                 137                 Range of Scanning X-Period
137                 137                 Range of Scanning Y-Period
STARTW                 ENDW                 Range of Scanning Wavelength            
0                   0                   Range of Scanning RowVar
0                   0                   Range of Scanning ColVar
"""
            
        layer_settings = ""
        for layer in range(1,number_of_layers+1):
            layer_settings += \
            "38.5                38.5                Range of Scanning Thickness of Layer[" + str(layer)+ "]" 
            if layer < number_of_layers: layer_settings += "\n"
            
                
        settings_bottom = """
1                   Layer Index
false               Advanced Options
false               Field Calculation
true                Automatically Starts Second Stage
100                 Nubmber of Points -1 for NPFx
100                 Nubmber of Points -1 for NPFy
100                 Nubmber of Points -1 for NPFz
-1                  2D Field Component
M                   Field Output Format: Power Flow; Amplitude (Re,Im); Amplitude (Mod,Ph)
%10.5g              Decimal Digits Format
0                   Scanning Direction
0                   Units Along X
0                   1                   Range of Scanning X Direction
0                   1                   Range of Scanning Y Direction
0                   82                  Range of Scanning Z Direction
0                   Fixed X
0                   Fixed Y
0                   Fixed Z
0                   Graph Index for X-axis
1                   Graph Index for Y-axis
2                   Graph Index for Z-axis
POLARIZATION_TYPE                   Polarization Type (Any, Hy=0, Ey=0, Hx=0, Ex=0)
false               Output Polarizer
0                   Polarizer Angle, deg
"""
        self.settings = settings_top + layer_settings + settings_bottom
        
    def setting_wavelength_scan(self,start_w, end_w, number_of_points, polarization_type="Any", order_c_x = 0,order_c_y=0, order_s_x = 0, order_s_y =0 ):
        # Seeting scan type variabel 
        scanning.type = 0
        
        if polarization_type == 'Any' : polarization_type = '0'
        if polarization_type == 'Hy': polarization_type = '1'
        if polarization_type == 'Ey': polarization_type = '2'
        if polarization_type == 'Hx': polarization_type = '3'
        if polarization_type == 'Ex': polarization_type = '4'
        
        self.settings = self.settings.replace("STARTW", str(start_w))
        self.settings = self.settings.replace("ENDW", str(end_w))
        self.settings = self.settings.replace("ROW_SCANNING_PARAMETER", str(5)) # Indicates wavelengths as a row scanning parameter
        self.settings = self.settings.replace("NUMBER_OF_COLUMN_POINTS", str(number_of_points))
        self.settings = self.settings.replace("ORDER_C_X", str(order_c_x)) # Cover X Order
        self.settings = self.settings.replace("ORDER_C_Y", str(order_c_y)) # Cover Y Order
        self.settings = self.settings.replace("ORDER_S_X", str(order_s_x)) # Cover X Order
        self.settings = self.settings.replace("ORDER_S_Y", str(order_s_y)) # Cover Y Order
        self.settings = self.settings.replace("POLARIZATION_TYPE", str(polarization_type)) # Cover X Order
        
        scanning.document=self.geo + self.settings
    
    
    def setting_single_wavlength(self, polarization_type="Any"):
        # Seeting scan type variabel 
        scanning.type = 1
        
        if polarization_type == 'Any' : polarization_type = '0'
        if polarization_type == 'Hy': polarization_type = '1'
        if polarization_type == 'Ey': polarization_type = '2'
        if polarization_type == 'Hx': polarization_type = '3'
        if polarization_type == 'Ex': polarization_type = '4'
        
        self.settings = self.settings.replace("STARTW", str(0))
        self.settings = self.settings.replace("ENDW", str(0))
        self.settings = self.settings.replace("ROW_SCANNING_PARAMETER", str(0)) # Indicates single parameter
        self.settings = self.settings.replace("NUMBER_OF_COLUMN_POINTS", str(0))
        self.settings = self.settings.replace("ORDER_C_X", str(0)) # Cover X Order
        self.settings = self.settings.replace("ORDER_C_Y", str(0)) # Cover X Order
        self.settings = self.settings.replace("ORDER_S_X", str(0)) # Cover X Order
        self.settings = self.settings.replace("ORDER_S_Y", str(0)) # Cover X Order
        self.settings = self.settings.replace("POLARIZATION_TYPE", str(polarization_type)) # Cover X Orders
        
    
        scanning.document= self.geo + self.settings
        
    def export_doument(self):
        return scanning.document


class run_simulation(scanning):
    
    def __init__(self,path_name = "mc_grating_script", from_file=False):
        #print(mc_grating_script)

        self.orders_x = 0
        self.orders_y = 0
        self.period_X = 0
        self.period_Y = 0
        self.path_name = path_name
        self.from_file = from_file

        self.launch_simulation()
        
    def launch_simulation(self):
        # Check if mc_grating_script_path was provided
        # else create file 
        if self.from_file:
            pass
        else:
            self.create_script()
        

        # Run the file as command line input
        subprocess.run(['C:\Program Files\MC Grating Software\Full\ModalCrossed.exe', self.path_name+'.mdl',  self.path_name+'_output.dat'])
        
        
     
        
        

    def create_script(self):
        document = scanning.document
        with open(self.path_name+ ".mdl", 'w') as new_file: 
            new_file.write(document)
        new_file.close()
        
        # Reset Document to be able to add a new geometry without changing header
        # document = mc_grating_header
        
        return self.path_name+ ".mdl"
        
    # def read_script(self):
        
    #     with open(self.path_name+ ".mdl", 'r') as file: 
    #         mc_grating_script = file.read()
    #     file.close()
        
    #     self.orders_x = int(mc_grating_script.split("Number of Modes X")[0].strip())
    #     self.orders_y = int(mc_grating_script.split("Number of Modes X\n")[1].split("Number of Modes Y")[0].strip()) 
    #     self.period_X = float(mc_grating_script.split("\n")[2].split("X-Period")[0].strip())
    #     self.period_Y = float(mc_grating_script.split("\n")[3].split("Y-Period")[0].strip())
        
  


    def open_output(self, scan = "wavelength_range"):
        
        # Get MC Grating Result
        f = open(self.path_name+'_output'+'.dat', "r")
        output = f.read()
        
        f.close()
        
    
        # Delete MC Grating .dat file
        #os.remove(output_name+'.dat')
        
        
        if scan == "wavelength_range":
            
            with open(self.path_name+'_output.dat', "rb") as f:  # binary mode
                columns = [element.decode("latin-1") for element in next(f).strip().split()]
                df = pd.DataFrame((
                    [float(e.decode("latin-1")) if e != b'\xa0' else 0 for e in l.strip().split()] for l in f), columns=columns)
                f.close()
            # Find Index to break dataframe into data and notifications
            none_indexes = [i for i,val in enumerate(df["WaveL"]) if val!=val]
            try:
                break_index = none_indexes[0]
                break_index_2 = none_indexes[1]
            except:
                break_index = len(df["WaveL"])-1
                break_index_2 = len(df["WaveL"])
            
            # Data
            data = df[:break_index]
            # Notification
            corrected_order_X = self.period_X
            corrected_order_Y = self.period_Y
            
            if break_index+1 != break_index_2:
                notification = df[break_index+1:]
                notification_string = notification.to_string()
                notification_sentence =  " ".join(notification_string.split())
                corrected_order_X = notification_sentence.split("Number of Orders was Corrected!")[1].split("X Orders =")[1].split()[0]
                corrected_order_Y = notification_sentence.split("Number of Orders was Corrected!")[1].split("Y Orders =")[1].split()[0]
                
           # os.remove(output_name+'.dat')
            
            return data,corrected_order_X,corrected_order_Y
            
       
        # TODO
        if scan == "single_parameter":
            
            
            def mc_grating_data_to_dict(data):
                    """
                    Generates a python dictionary from mc grating data 
                    keys=['Order', 'AngleN, deg', 'AngleP, deg', 'Power', 'Power(s)', 'Power(p)']
    
                    Parameters
                    ----------
                    data : string
                        extracted data from .dat file.
    
                    Returns
                    -------
                    dict_file: dictionary
                        converted dictionary
    
                    """
                    
                    # Initialize
                    lines = [l for l in data.splitlines()]
                    dict_file={}
                    keys=['Order', 'AngleN, deg', 'AngleP, deg', 'Power', 'Power(s)', 'Power(p)']
                    # Assign keys to dictionary 
                    for col in keys: dict_file[col]=[] 
                
                    for i, col in enumerate(lines[1:]):
                       for e,i in enumerate(re.split(r'\s{2,}', col.strip())):
    
                           if keys[e] == 'Order':
                               dict_file[keys[e]].append(i)
                           else:
                               dict_file[keys[e]].append(float(i))
                
                    dict_file['Order'] = dict_file['Order'][:-1]
                    
                    return dict_file
            
            # Help variable
            substrate_exists = False
                
            # EXTRACT Cover
            data_cover_substrate = (output.split("Cover diffractive Orders\n")[1]).split("Substrate diffractive Orders\n")
            data_cover = data_cover_substrate[0]
            # Convert Data to dict
            result_cover = mc_grating_data_to_dict(data_cover)
            
            #print("COVER")
            #print(data_cover)
                
            if len(data_cover_substrate) > 1 :
                substrate_exists = True
                #print("SUBSTRATE")
                data_substrate = data_cover_substrate[1]
                # Convert data to dict
                result_substrate = mc_grating_data_to_dict(data_substrate)
                #print(data_substrate)
                
            
            # Extract Notification 
            try:
                notifications = [elem.strip() for elem in output.split("Balance")[1].split("\n")[1:] if elem  is not ""]
                #print("\n")
                #print(notifications)
            except :
                notifications = None
                
            
            if notifications is not None:
                if 'Number of Orders was Corrected!' in notifications:
                    
                    self.orders_x = (([elem for elem in notifications if "X Orders" in elem][0]).split("=")[1]).strip()
                    self.orders_y = (([elem for elem in notifications if "Y Orders" in elem][0]).split("=")[1]).strip()
                    print("\nNumber of orders was auto-corrected by MC Grating")
                    print("Orders X: ", self.orders_x, "Orders Y: ", self.orders_y)
                
            
           
            
            
            
           
            
            if substrate_exists: 
                return [result_cover,result_substrate], self.orders_x, self.orders_y, substrate_exists
            else:
                #print("A")
                #print(substrate_exists)
                return [result_cover], self.orders_x, self.orders_y, substrate_exists
