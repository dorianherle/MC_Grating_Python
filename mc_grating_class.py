# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 10:31:47 2019

@author: Dorian
"""

import subprocess
import numpy as np
import pandas as pd
import json 


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
            geometry.mc_grating_geometry = document
            

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
      
    def rectangle(self, center, w_x, w_y, material):
        if self.counting_layers:     # don't count unless a layer was defined
            self.counting_pillars += 1
              
        number_points = 4
        cX,cY = center
            
        # MC Grating Repeats Geometries where a point is negative
        # Therefore the centers have to be displaced to the middle of a unit cetl
        cX = cX+self.period_X/2
        cY = cY+self.period_Y/2
        # TODO Fix
        #print("Attention Center at bottom: rectangle class mc grating")
        # Getting the points of the rectangle 
        x11 = (cX-w_x/2)/self.period_X
        y12 = (cY-w_y/2)/self.period_Y
        x21 = (cX+w_x/2)/self.period_X
        y22 = (cY+w_y/2)/self.period_Y
        
        points = [[x11,y12],[x21,y12],[x21,y22],[x11,y22]]
        
        rectangle = \
        '1' +   '\t' + '0' + '\t' + str(number_points) + '\t' + 'Eps.Re; Eps.Im; Npoints of Pillar[' + str(self.counting_pillars) + ']; Material:' + ' ' + material + "\n" \
        
        for i,point in enumerate(points):
            i += 1
            rectangle = rectangle + \
            str(point[0]) + "\t\t" + str(point[1]) + "\t\t" + "x[" + str(i) + "]/(X-Period); y[" + str(i) + "]/(Y-Period)" + "\n" 

        
        self.save_to_temp(rectangle)
        
    def polygon(self, xy_data, material):
        if self.counting_layers:     # don't count unless a layer was defined
            self.counting_pillars += 1
            
        number_points = xy_data.shape[0]
        # MC Grating Repeats Geometries where a point is negative
        # Therefore the centers have to be displaced to the middle of a unit cet
        # Assumption: STL File is centered a zero
        # Correction
        centroid = xy_data.mean(axis=0)
        points_centered = np.add(xy_data,[self.period_X/2-centroid[0], self.period_Y/2-centroid[1]])
        # Scale the points to the MC Grating Length
        points = np.divide(points_centered,[self.period_X, self.period_Y])
        
        ### ------------------------------------------------------------------
        ### SORT COUNTERCLOCKWISE
        ## SOURCE: https://stackoverflow.com/questions/58377015/counterclockwise-sorting-of-x-y-data
        x,y = points.T
        
        dist2 = lambda a,b: (a[0]-b[0])*(a[0]-b[0]) + (a[1]-b[1])*(a[1]-b[1])

        z = list(zip(x, y)) # get the list of coordinate pairs
        z.sort() # sort by x coordinate
        
        cw = z[0:1] # first point in clockwise direction
        ccw = z[1:2] # first point in counter clockwise direction
        # reverse the above assignment depending on how first 2 points relate
        if z[1][1] > z[0][1]: 
            cw = z[1:2]
            ccw = z[0:1]
        
        for p in z[2:]:
            # append to the list to which the next point is closest
            if dist2(cw[-1], p) < dist2(ccw[-1], p):
                cw.append(p)
            else:
                ccw.append(p)
        
        cw.reverse()
        points_counter_clockwise = cw + ccw
        ### ------------------------------------------------------------------
        
        polygon = \
        '1' +   '\t' + '0' + '\t' + str(number_points) + '\t' + 'Eps.Re; Eps.Im; Npoints of Pillar[' + str(self.counting_pillars) + ']; Material:' + ' ' + material + "\n" \
        
        for i,point in enumerate(points_counter_clockwise):
            i += 1
            polygon = polygon + \
            str(point[0]) + "\t" + str(point[1]) + "\t" + "x[" + str(i) + "]/(X-Period); y[" + str(i) + "]/(Y-Period)" + "\n" 
    
        
        self.save_to_temp(polygon)
    
        
    
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
    
    def __init__(self, geo=""):
        
        # Initialize scanning
        scanning.document = ""
        # Initalize scan type
        scanning.type = 0
        # 0 wavelength range scan
        # 1 single wavlength scan
        
        # Get Geometry document
        if geo=="":
            self.geo = geometry.mc_grating_geometry
        else:
            self.geo = geo
        
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
        
    def export_doument(self, path=""):
        if path != "":
            document = scanning.document
            with open(path+ ".mdl", 'w') as new_file: 
                new_file.write(document)
            new_file.close()
        
        
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
        if not self.from_file:
            self.create_script()
        

        # Run the file as command line input
        subprocess.run(['C:\Program Files\MC Grating Software\Full\ModalCrossed.exe', self.path_name+'.mdl',  self.path_name+'_output.json'])
        
        
     
        
        

    def create_script(self):
        document = scanning.document
        with open(self.path_name+ ".mdl", 'w') as new_file: 
            new_file.write(document)
        new_file.close()
        
        # Reset Document to be able to add a new geometry without changing header
        # document = mc_grating_header
        
        return self.path_name+ ".mdl"
        

    def open_output(self):
        
        # Get MC Grating Result
        with open(self.path_name+'_output'+'.json') as json_file:
            output = json.load(json_file)
        
    
        dict_keys = np.array(list(output.keys()))
        
        if output["ScanType"] == 1: # 1 Parameter scan
            # get initial value
            iniValue = output["ScanPar"]["IniValue"]
            # get index where iniutal value starts in dict keys
            indx = np.where(dict_keys== str(iniValue))
            values = dict_keys[indx[0][0]: ]
            
            data = {}
            for value in values:
                data[value] = output[value]
            return data
        
            
 
        
class object_3d_geometry():
    
    def __init__(self, period_x, period_y):
        self.period_X = period_x
        self.period_Y = period_y
        self.geo = geometry(period_x=period_x, period_y=period_y) 
        self.objects = []

    
    def cover_material(self, material):
        self.geo.cover_material(material)
        
    # OBJECTS
    def cylinder(self, position, radius, height, name = "cylinder", material = "Silicon (Table)", order = 0):
        """
        Creates a 3D cylinder object
    
        Parameters
        ----------
        position : list
            Position of bottom center of cylinder. 
            Example: position = [0,0,0].
        radius : float
            Radius of cylinder.
            Example: radius = 49.
        height : float
            Height of cylinder 
            Example: height = 77.
    
        Returns
        -------
        None.
    
        """
        
        # points where cross-section changes - z Axis
        points_cross_section_change = [position[2], position[2]+height]
        
        # Create cylinder object -> As dictionnary 
        dict_ = {}
        dict_["name"] = name
        dict_["type"] = 'cylinder'
        dict_["parameters"] = [position, radius, height]
        dict_["material"] = material
        dict_["points_cross_section_change"] = points_cross_section_change
        dict_["order"] = order
        
        self.objects.append(dict_)
        


    def cuboid(self, position, length, width, height, name = "cuboid", material = "Silicon (Table)", order = 0):
        """
        Creates a 3D cuboid
        
        """
        
        # points where cross-section changes - z Axis
        points_cross_section_change = [position[2], position[2]+height]
        
        # Create cylinder object -> As dictionnary 
        dict_ = {}
        dict_["name"] = name
        dict_["type"] = 'cuboid'
        dict_["parameters"] = [position, length, width, height]
        dict_["material"] = material
        dict_["points_cross_section_change"] = points_cross_section_change
        dict_["order"] = order
        
        self.objects.append(dict_)
        
    


    def object_to_layer(self, object_):
        
        # Cylinder
        if object_["type"] == 'cylinder':
            [position, radius, height] = object_["parameters"]
            material = object_["material"]
            
            self.geo.circle(position[:-1], radius, material)
            
        
        # Cuboid
        if object_["type"] == 'cuboid':
            [position, length, width, height] = object_["parameters"]
            material = object_["material"]
            
            
            self.geo.rectangle(position[:-1], length, width, material)
            
        
    def string_diff(self, list_of_list_of_strings):
        # When you have a list of list of strings 
        # and you wan to create a list of list of strings where only the strings are
        # inserted that are the same in subsequent lists
        # Example: temp1 = [['One', 'Two'],['One', 'Two','Three', 'Four']]
        # Res: [['One', 'Two']]
        res = []
        start = list_of_list_of_strings[0]
        for list_ in list_of_list_of_strings[1:]:
            s = set(start)
            temp = [x for x in list_ if x in s]
            res.append(temp)
            # update
            start = list_
        return res 
            
        
    def check_if_cuboid_spans_doamin(self, object_):
        # first check if imput object is a cuboid ...
        if object_["type"] == 'cuboid':
            # Check if the Cuboid spans the entire domain. If it is the case, then
            # it is better to define it as a layer than a rectangle
            [position, length, width, height] = object_["parameters"]
            pos_X, pos_Y, pos_Z = position
            if pos_X == 0 and pos_Y == 0 and length == self.period_X and width == self.period_Y:
                return True
            else:
                return False
        else:
            return False
    
    def substrate(self, material):
            self.geometry_to_mc_grating_script()
            self.geo.substrate(material)
            

    def geometry_to_mc_grating_script(self):
        objects = self.objects
        geometry_objects = {}
        for obj in objects:
            geometry_objects[obj["name"]]=obj
            
        
        names_list = []
        points_cross_section_change_list = []
        for object_ in objects:
            for point_ in object_["points_cross_section_change"]:
                names_list.append(object_["name"])
                points_cross_section_change_list.append(point_)
                
        
        
        df = pd.DataFrame([names_list, points_cross_section_change_list], index=['Name', 'Cross-Section-Change']).T
        df = df.sort_values('Cross-Section-Change')  
        
        
        
        # Combine all objects that belong to the same layer
        # Source: https://stackoverflow.com/questions/65740018/pandas-dataframe-regrouping/65740157#65740157
        df = (df.pivot(index='Cross-Section-Change', columns='Name', values='Name')
           .apply(lambda x: x[x.notna().cumsum().ne(0)].bfill())
           .apply(lambda x: list(x.dropna()), axis=1)
        )
        
        # Get layer thicknesses and objects
        # From top to bottom -> MC Grating Layer Definition
        layer_thicknesses = np.abs(np.diff(df.index.tolist()[::-1]))
        
        objects_at_each_cross_section_change = list(df.values)[::-1]
        # Get object in each layer -> Keep strings which are the same in subsequent lists
        objects_in_each_layer = self.string_diff(objects_at_each_cross_section_change)
        
        # order objects in each layer according to their order -> important to make holes etc.
        sorted_objects_in_each_layer = []
        for objects_in_layer in objects_in_each_layer:
        
            orders = [geometry_objects[object_name]["order"] for object_name in objects_in_layer]
        
            # sort
            sorted_objects_in_layer = [x for _,x in sorted(zip(orders,objects_in_layer))][::-1]
            
            sorted_objects_in_each_layer.append(sorted_objects_in_layer)
        
        
        
        # Build MC Grating Script
        for i,layer_thickness in enumerate(layer_thicknesses):
            # check if cuboid in span domain
            check = [self.check_if_cuboid_spans_doamin(geometry_objects[object_name]) for object_name in sorted_objects_in_each_layer[i]]
            
            # BACKGROUND MATERIAL (LAYER) 
            if True in check:
                name = np.array(sorted_objects_in_each_layer[i])[check]
                if len(name) > 1:
                    raise Exception('Perfectly overlapping cuboids found in layer '+ str(i)+". Object names: " + str(name) +"\nPlease fix.")
                else:
                    name_of_cuboid_that_spans_domain = name[0]
                    
                object_ = geometry_objects[name_of_cuboid_that_spans_domain]
                [_, _, _, height] = object_["parameters"]
                material = object_["material"]
                # LAYER 
                self.geo.layer(thickness = height, sourrounding_material = material)
                
                # ADD "PILLARS" to LAYER
                for object_name in sorted_objects_in_each_layer[i]:
                    # if object does not span the domain 
                    if object_name != name_of_cuboid_that_spans_domain:
                        self.object_to_layer(geometry_objects[object_name])
                    
                
            else:
                # LAYER 
                self.geo.layer(thickness = layer_thickness, sourrounding_material = "Air (Special Formula)")
                
                # ADD "PILLARS" to LAYER
                for object_name in sorted_objects_in_each_layer[i]:
                    self.object_to_layer(geometry_objects[object_name])
                    
        
                
  