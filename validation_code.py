import arcpy
import os 
import datetime

params = {"EMSR_number": 0,
          "AOI_number": 1,
          "Product_type": 2,
          "Sensor": 3,
          "Raw_sensor_data": 4,
          "Acquisition_date_time": 7,
          "Availability_date_time": 8,
          "Reception_date_time":9,
          "Image": 5,
          "Res":10,
          "Pre_image_condition": 6,
          "Cleaning_condition": 11,
          }

metadata_function = ["COSMO-SkyMed", "GeoEye-1", "Landsat-8", "Landsat-9", "PAZ", "Pleiades Neo", "PlanetScope", "Pleiades", "RADARSAT-2", "Sentinel-1",
"Sentinel-2", "SkySat", "SPOT-6", "SPOT-7", "WorldView-2", "WorldView-3", "TerraSAR-X"]

class ToolValidator:
  # Class to add custom behavior and properties to the tool and tool parameters.
    
    def __init__(self):
        # Set self.params for use in other validation methods.
        self.params = arcpy.GetParameterInfo()
        self.firstStart = True
        
    def initializeParameters(self):
        # Customize parameter properties. This method gets called when the
        # tool is opened.
        
        # Compile date and times based on sensor folder           
        aprx = arcpy.mp.ArcGISProject('current')
        maps = aprx.listMaps()
        map = next((map for map in maps if map.name == "Map Display"), None)
        layers = map.listLayers()
        aoi = next((lyr for lyr in layers if lyr.name == "General Information"), None)
        fields = ["emsr_id", "area_id", "map_type"]
        with arcpy.da.SearchCursor(aoi, fields) as cursor:
            for row in cursor:
                value = row
        activation_number = value[0]
        aoi_number = value[1]
        map_type = value[2] 
        
        if map_type == "First Estimate Product":
        	map_type = "FEP"
        elif map_type == "Reference":
        	map_type = "REF"
        elif map_type.startswith("Delineation"):
        	parts = map_type.split("-")
        	if len(parts) > 1:
        		monitoring_stage = parts[1].upper()
        		map_type = "DEL" + monitoring_stage
        	else:
        		map_type = "DEL"
        elif map_type.startswith("Grading"):
        	parts = map_type.split("-")
        	if len(parts) > 1:
        		monitoring_stage = parts[1].upper()
        		map_type = "GRA" + monitoring_stage
        	else:
        		map_type = "GRA"
        self.params[params["EMSR_number"]].value = activation_number
        self.params[params["AOI_number"]].value = aoi_number
        self.params[params["Product_type"]].value = map_type     
        self.params[params["Acquisition_date_time"]].enabled = False
        self.params[params["Image"]].enabled = True
        self.params[params["Raw_sensor_data"]].enabled = True
        return
    
    def SelfFiller(self, sensor_extention):
        raw_folders = str(self.params[params["Raw_sensor_data"]].value).split(";")
        file_path_list = []
        for raw_folder in raw_folders:
            for root, subdirs, files in os.walk(raw_folder):
                for file in files:
                    if file.endswith(sensor_extention):
                        file_path = os.path.join(root, file)
                        file_path_list.append(file_path)
        self.params[params["Image"]].value = file_path_list
    
    def updateParameters(self):
    # Modify the values and properties of parameters before internal
    # validation is performed.

        if self.params[params["Sensor"]].altered and not self.params[params["Sensor"]].hasBeenValidated:
            if self.params[params["Sensor"]].value not in metadata_function: 
                self.params[params["Acquisition_date_time"]].enabled = True
                self.params[params["Raw_sensor_data"]].enabled = False
                self.params[params["Image"]].enabled = True
            elif self.params[params["Sensor"]].value == "Sentinel-2":
                self.params[params["Acquisition_date_time"]].enabled = False
                self.params[params["Raw_sensor_data"]].enabled = True
                self.params[params["Image"]].enabled = False
            else:
                self.params[params["Acquisition_date_time"]].enabled = False
                self.params[params["Image"]].enabled = True
                self.params[params["Raw_sensor_data"]].enabled = True
    
        if self.params[params["Raw_sensor_data"]].altered and not self.params[params["Raw_sensor_data"]].hasBeenValidated:   
            sensor_folder = str(self.params[params["Raw_sensor_data"]].value).split(";")[0]
            modification_time = os.path.getmtime(sensor_folder)
            reception_datetime = datetime.datetime.utcfromtimestamp(modification_time)
            reception_datetime_formatted = reception_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            reception_datetime_formatted = reception_datetime_formatted.replace(reception_datetime_formatted[-3:-1], "00", 1)
            availability_datetime = reception_datetime - datetime.timedelta(minutes = 10)
            availability_datetime_formatted = availability_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            availability_datetime_formatted = availability_datetime_formatted.replace(availability_datetime_formatted[-3:-1], "00", 1)
            self.params[params["Availability_date_time"]].value = availability_datetime_formatted
            self.params[params["Reception_date_time"]].value = reception_datetime_formatted
        
            if self.params[params["Sensor"]].value in ["WorldView-2", "WorldView-3", "GeoEye-1"]:
                self.SelfFiller(".TIL")
            elif self.params[params["Sensor"]].value in ["SPOT-6", "SPOT-7", "Pleiades", "Pleiades Neo"]:
                self.SelfFiller(".JP2")
            elif self.params[params["Sensor"]].value == "PlanetScope":
                self.SelfFiller(".tif")   
        
        if self.params[params["Image"]].altered and not self.params[params["Image"]].hasBeenValidated:
            image_string = str(self.params[params["Image"]].value)
            image_string = image_string.replace("\\", "\\\\")
            image = arcpy.Raster(image_string.split(";")[0])
            meanCellWidth = image.meanCellWidth
            if image.spatialReference.type == 'Geographic':
                res = (40030200.0 /360.0)*meanCellWidth
            else:
                res = meanCellWidth
            base = float(f"{1:<0{len(str(int(res)))}d}") / 10.0
            sensor_res = f"{round(res / base) * base}"   
            self.params[params["Res"]].value = sensor_res
            
        if self.params[params["Sensor"]].altered and not self.params[params["Sensor"]].hasBeenValidated:
            if self.params[params["Sensor"]].value == "Sentinel-2":
                self.params[params["Res"]].value = "10"
            elif self.params[params["Sensor"]].value in ["Landsat-8", "Landsat-9"]:
                self.params[params["Res"]].value = "30"   
        return

    def updateMessages(self):
        # Modify the messages created by internal validation for each tool
        # parameter. This method is called after internal validation.
        aprx = arcpy.mp.ArcGISProject('current')
        layout = aprx.listLayouts('EMS_Template_v*')[0]
        textLayoutElm = layout.listElements('TEXT_ELEMENT', 'ovrMapType')[0]
        split_text = textLayoutElm.text.split(' -')
        text_parts = split_text[0].split(" ")
        
        
        if len(text_parts) > 1:
            monitoring_stage = text_parts[1]
            if text_parts[0].startswith("Del"):
                maptype = "DEL" + monitoring_stage
            elif text_parts[0].startswith("Gra"):
                maptype = "GRA" + monitoring_stage
        else:
            if text_parts[0].startswith("First"):
                maptype = "FEP"
            elif text_parts[0].startswith("Ref"):
                maptype = "REF"
            elif text_parts[0].startswith("Del"):  
               maptype = "DEL"
            elif text_parts[0].startswith("Gra"):  
               maptype = "GRA"
        
        current_product_type = self.params[params["Product_type"]].value
        if maptype != current_product_type:
            self.params[params["Product_type"]].setWarningMessage(f"AOI attribute table reports this is a {current_product_type}, but template reports this is a {maptype}. Fix this inconsistency!")
            
        if self.params[params["Sensor"]].value not in metadata_function:
            self.params[params["Sensor"]].setWarningMessage("There are no metadata functions available for this sensor. Time parameters must be inserted manually")
        return

    # def isLicensed(self):
    #     # Set whether the tool is licensed to execute.
    #     return True

    # def postExecute(self):
    #     # This method takes place after outputs are processed and
    #     # added to the display.
    #     return
