import requests
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import arcpy


class UpdateSmartOLS:
    """Class that communicate with the Smart OLS and update the image information within it."""

    polFootprint = None

    def __init__(self, pre_post: str, sensorImage: str, fileName: str, avTime: str,
                 reTime: str, acTime: str, gsdImage: str, imageQcPath: str):

        self.fileName = fileName
        self.infoProd = self.fileName.split('_')
        self.EMSRCode = self.infoProd[0]
        self.Aoi = self.infoProd[1][3:]
        self.pType = self.infoProd[2]
        self.monitoring = False if self.infoProd[3] == 'PRODUCT' else True
        self.pre_post = pre_post
        self.sensorImage = "SPOT-6-7" if sensorImage in ["SPOT-6", "SPOT-7"] else sensorImage
        self.qcTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        self.avTime = avTime
        self.reTime = reTime
        self.acTime = acTime
        self.gsdImage = gsdImage
        self.reasonDelay = None
        self.imageQcPath = imageQcPath
        self.auth = ("admin", "TestSMART11!")
        self.baseUrl = "https://smartols-test.e-geos.earth"
        self.imgId = None
        self.numberOfIds = None

    def getImageId(self):
        """Get the image ids available in the smart OLS for the specific product, discriminating between pre, and post
           images. If only one image is found, the script will automatically overwrite that specific image_id in
           smart OLS. If more than one image is found, the tool ask the user to insert the image id by hand, after
           contacting the Odo to get the correct image id between the one available. If no image is found, return an
           error and ask the user to check if all parameters are correct."""

        linkApi = f"{self.baseUrl}/api/v2/products/?page=1&aoi={self.Aoi}&aoi_id&activation={self.EMSRCode}&activation_id="
        req = requests.get(linkApi, auth=self.auth, verify=False)
        products = req.json()

        for product in products['results']:
            if self.pType == product['type'] and self.monitoring == product['monitoring']:
                images = product['images']
                for image in images:
                    if self.pre_post == image['preOrPost']:
                        imageIdList = [image['id'] for image in images if image['preOrPost'] == self.pre_post]
                        self.numberOfIds = len(imageIdList)

                        if self.numberOfIds == 1:
                            self.imgId = image['id']
                            print(f'Found only one {self.pre_post} image.')
                            return True

                        elif self.numberOfIds > 1:
                            print(f'There are more than one {self.pre_post} images {tuple(imageIdList)}. Please, ask to the Odo, '
                                  f'the correct image_id that will be overwritten in the SMART OLS, and insert it in '
                                  f'the next window carefully!')
                            self.insertImageID(tuple(imageIdList))
                            return True
        return False

    def insertImageID(self, imageIds: tuple):
        """Open a user interface that allow the user to insert the image id that need to be updated in Smart OLS.
           The function, will accept only the image id present in the imageId variable."""

        def assign_id():
            id = combobox.get()
            if id.isdigit():
                self.imgId = id
                root.destroy()
            else:
                warning_label.pack(pady=10)

        root = self.GUIstructure()   
        label = tk.Label(root, text = f"The following Ids were found in the SMART OLS {imageIds}. Please associate your image to one of them and, in case you have doubts, ask the OdO", font=("Helvetica", 14), bg="lightblue")
        label.pack(pady=20)
        warning_label = tk.Label(root, text = "You have to select a number of the list!", font=("Helvetica", 14), bg="red")
        combobox = ttk.Combobox(root, values=imageIds, font=("Helvetica", 12))
        combobox.pack(pady=20)
        combobox.set("Select an ID")
        submit_button = tk.Button(root, text="Submit", command=assign_id, font=("Helvetica", 12), bg="blue", fg="white", padx=20, pady=10)
        submit_button.pack(pady=10)
        root.mainloop()
        
    def createUpdatedJSON(self):
        """Create a dictionary JSON with the updated values. This, will be returned and will be used to update the Smart OLS."""

        newJSON = {}

        def CheckDateTimeFormat(dict):
            errors = []
            DateTimes = ['acquisitionTime', 'availabilityTime', 'receptionTime', 'qualityCheckTime']
            for DateTime in DateTimes:
                try:
                    date_object = datetime.strptime(dict[DateTime], "%Y-%m-%dT%H:%M:%SZ") 
                except:
                    errors.append(DateTime)
            if len(errors) == 0:
                errors = None
            arcpy.AddMessage(f"first section: {errors}")
            return errors
        
        def CheckDateTimeSequence(dict):
            errors = []
            # this try prevents crushing if time format is not correct 
            try:
                acquisitionTime = datetime.strptime(dict["acquisitionTime"], "%Y-%m-%dT%H:%M:%SZ")
                availabilityTime = datetime.strptime(dict["availabilityTime"], "%Y-%m-%dT%H:%M:%SZ")
                receptionTime = datetime.strptime(dict["receptionTime"], "%Y-%m-%dT%H:%M:%SZ")
                qualityCheckTime = datetime.strptime(dict["qualityCheckTime"], "%Y-%m-%dT%H:%M:%SZ")
                DateTimes = [acquisitionTime, availabilityTime, receptionTime, qualityCheckTime]
                DateTimes_string = ['Acquisition Time', 'Availability Time', 'Reception Time', 'Quality Check Time']
                for i in range(0, len(DateTimes)):
                    for j in range(i + 1, len(DateTimes)):
                        if DateTimes[i] > DateTimes[j]:
                            errors.append(f"{DateTimes_string[i]} can't be higher than {DateTimes_string[j]}!")
                if len(errors) == 0:
                    errors_string = None
                else:
                    errors_string = " AND ".join(errors)
            except:
                errors_string = None
            return errors_string
        
        def CheckDateTimeConsistency(dict):
            try:
                filename_date = dict['fileName'].split("_")[5]
                filename_time = dict['fileName'].split("_")[6]
                filename_datetime = filename_date + filename_time
                filename_datetime_format = datetime.strptime(filename_datetime, "%Y%m%d%H%M")
                acquisition_datetime = dict['acquisitionTime']
                acquisition_datetime_format = datetime.strptime(acquisition_datetime, "%Y-%m-%dT%H:%M:%SZ")
                if filename_datetime_format != acquisition_datetime_format:
                    error = "Acquisition Date in the File Name field does not match the one in the Acquisition Time field!"
                else:
                    error = None
            except:
                error = None 
            return error

        def ValidateParameters(newJSON):
            errors = []
            validation = {"DateTime format": lambda: CheckDateTimeFormat(newJSON),
                          "DateTime sequence": lambda: CheckDateTimeSequence(newJSON),
                          "DateTime consistency": lambda: CheckDateTimeConsistency(newJSON)
                        }
            
            warning = {"DateTime format" : "DateTime format error: {} is not in the right format",
                       "DateTime sequence" : "DateTime sequence error: {}",
                       "DateTime consistency" : "DateTime consistency error: {}"}
                       
            for key, validate in validation.items():
                error = validate()
                if error != None:
                    errors.append(warning[key].format(error))
            return errors
        
        def UpdatedJSON():
            nonlocal newJSON
            newJSON = {
            'sensor': sensor_entry.get(),
            'fileName': fileName_entry.get(),
            'acquisitionTime': acquisitionTime_entry.get(),
            'availabilityTime': availabilityTime_entry.get(),
            'receptionTime': receptionTime_entry.get(),
            'qualityCheckTime': qualityCheckTime_entry.get(),
            'gsdResolution': gsdResolution_entry.get(),
            'footprint': footprint_entry.get(),
            'cloudCover': 0,
            'reasonForDelay': reasonForDelay_entry.get()
            }
            errors = ValidateParameters(newJSON)
            if len(errors) > 0:
                error_label.config(text="\n".join(errors), fg="red")
            else:
                root.destroy()
            
        self.addReasonForDelay()

        # Make a recap of parameters before submitting
        # Give to the user the opportunity of changing parameters if needed

        root = self.GUIstructure()
        initial_label = tk.Label(root, text="The following data will be submitted to OLS, are you sure?", bg="lightblue", font=("Helvetica", 12, "bold"))
        initial_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # sensor
        sensor_label = tk.Label(root, text="Sensor:", bg="lightblue", font=("Helvetica", 10, "bold"))
        sensor_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        sensor_entry = tk.Entry(root, width=70)
        sensor_entry.grid(row=1, column=1, padx=10, pady=10)
        sensor_entry.insert(0, self.sensorImage)

        # filename
        fileName_label = tk.Label(root, text="File Name:", bg="lightblue", font=("Helvetica", 10, "bold"))
        fileName_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        fileName_entry = tk.Entry(root, width=70)
        fileName_entry.grid(row=2, column=1, padx=10, pady=10)
        fileName_entry.insert(0, self.fileName)

        # acquisitionTime
        acquisitionTime_label = tk.Label(root, text="Acquisition Time:", bg="lightblue", font=("Helvetica", 10, "bold"))
        acquisitionTime_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        acquisitionTime_entry = tk.Entry(root, width=70)
        acquisitionTime_entry.grid(row=3, column=1, padx=10, pady=10)
        acquisitionTime_entry.insert(0, self.acTime)

        # availabilityTime
        availabilityTime_label = tk.Label(root, text="Availability Time:", bg="lightblue", font=("Helvetica", 10, "bold"))
        availabilityTime_label.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        availabilityTime_entry = tk.Entry(root, width=70)
        availabilityTime_entry.grid(row=4, column=1, padx=10, pady=10)
        availabilityTime_entry.insert(0, self.avTime)

        # receptionTime
        receptionTime_label = tk.Label(root, text="Reception Time:", bg="lightblue", font=("Helvetica", 10, "bold"))
        receptionTime_label.grid(row=5, column=0, padx=10, pady=10, sticky="w")
        receptionTime_entry = tk.Entry(root, width=70)
        receptionTime_entry.grid(row=5, column=1, padx=10, pady=10)
        receptionTime_entry.insert(0, self.reTime)

        # qualityCheckTime
        qualityCheckTime_label = tk.Label(root, text="Quality Check Time:", bg="lightblue", font=("Helvetica", 10, "bold"))
        qualityCheckTime_label.grid(row=6, column=0, padx=10, pady=10, sticky="w")
        qualityCheckTime_entry = tk.Entry(root, width=70)
        qualityCheckTime_entry.grid(row=6, column=1, padx=10, pady=10)
        qualityCheckTime_entry.insert(0, self.qcTime)

        # gsdResolution
        gsdResolution_label = tk.Label(root, text="GSD Resolution:", bg="lightblue", font=("Helvetica", 10, "bold"))
        gsdResolution_label.grid(row=7, column=0, padx=10, pady=10, sticky="w")
        gsdResolution_entry = tk.Entry(root, width=70)
        gsdResolution_entry.grid(row=7, column=1, padx=10, pady=10)
        gsdResolution_entry.insert(0, self.gsdImage)

        # footprint
        footprint_label = tk.Label(root, text="Footprint:", bg="lightblue", font=("Helvetica", 10, "bold"))
        footprint_label.grid(row=8, column=0, padx=10, pady=10, sticky="w")
        footprint_entry = tk.Entry(root, width=70)
        footprint_entry.grid(row=8, column=1, padx=10, pady=10)
        footprint_entry.insert(0, self.polFootprint)

        # reasonForDelay
        reasonForDelay_label = tk.Label(root, text="Reason for Delay:", bg="lightblue", font=("Helvetica", 10, "bold"))
        reasonForDelay_label.grid(row=9, column=0, padx=10, pady=10, sticky="w")
        reasonForDelay_entry = tk.Entry(root, width=70)
        reasonForDelay_entry.grid(row=9, column=1, padx=10, pady=10)
        reasonForDelay_entry.insert(0, self.reasonDelay)

        error_label = tk.Label(root, text="", bg="lightblue", font=("Helvetica", 10, "bold"))
        error_label.grid(row=13, column=0, columnspan=2, pady=10)

        submit_button = tk.Button(root, text="Submit to OLS", command=UpdatedJSON, font=("Helvetica", 12), bg="blue", fg="white", padx=20, pady=10)
        submit_button.grid(row=10, column=0, columnspan=2, pady=10)

        root.mainloop()

        return newJSON

    def addReasonForDelay(self):
        """Calculate the delta time between the image reception time and the QC time(now), if the difference is more
           than 30 minutes, the tool will open a user interface where the user must insert a valid reason
           (at least 10 characters to prevent involuntary errors) for delay, that will be inserted in the Smart OLS."""

        nowDateObj = datetime.strptime(self.qcTime, '%Y-%m-%dT%H:%M:%SZ')
        reTimeObj = datetime.strptime(self.reTime, '%Y-%m-%dT%H:%M:%SZ')
        difference = nowDateObj - reTimeObj
        minutes_passed = difference.total_seconds() / 60

        if minutes_passed > 30:

            def CompileReasonForDelay():
                reasonDelay = entry.get("1.0", "end-1c")
                if len(reasonDelay) > 10:
                    self.reasonDelay = reasonDelay
                    root.destroy()
                else:
                    warning_label.pack(pady=10)

            root = self.GUIstructure()
            label = tk.Label(root, text = f'Please, provide a reason for delay, {minutes_passed} minutes have passed from the image reception', font=("Helvetica", 14), bg="lightblue")
            label.pack(pady=10)
            entry = tk.Text(root, font=("Helvetica", 12), width = 40, height = 4)
            entry.pack(padx=50, pady=50)
            warning_label = tk.Label(root, text = "You must insert a reason longer than 10 characters!", font=("Helvetica", 14), bg="red", padx=10, pady=10)
            submit_button = tk.Button(root, text="Submit", command=CompileReasonForDelay, font=("Helvetica", 12), bg="blue", fg="white", padx=20, pady=10)
            submit_button.pack(pady=10)
            root.mainloop()
        else:
            self.reasonDelay = ""
            

    def updateSmartOLS(self, newJSON):
        """Here the image id in the Smart OLS is updated. If there are errors in the update, the tool will return
           the errors occurred."""

        update = f"{self.baseUrl}/api/v2/images/{self.imgId}"
        updating = requests.patch(update, json=newJSON, auth=self.auth, verify=False, headers={'Accept': 'application/json'})
        print("Response Status Code:", updating.status_code)
        print("Response Content:", updating.text)
        if not updating.ok:
            errorsDict = updating.json().get('errors', {})
            print(errorsDict)
            error_messages = "\n".join(f"{errorsDict[error][0]} -> {error}" for error in errorsDict)
            def CloseButton():
                root.destroy()
            root = self.GUIstructure()
            label = tk.Label(root, text = "Update unsuccessful, the following errors were found:", font=("Helvetica", 14), bg="red")
            error_label = tk.Label(root, text = error_messages , font=("Helvetica", 14), bg="lightblue")
            label.pack(pady=10)
            error_label.pack(pady=10)
            close_button = tk.Button(root, text= "Close", command=CloseButton, font=("Helvetica", 12), bg="blue", fg="white", padx=20, pady=10)
            close_button.pack(pady=10)
            root.mainloop()
            print("Errors encountered:\n" + error_messages)

        else:
            def CloseButton():
                root.destroy()
            root = self.GUIstructure()
            label = tk.Label(root, text = "Data successfully submitted to SMART OLS!", font=("Helvetica", 14), bg="lightblue")
            label.pack(pady=10)
            close_button = tk.Button(root, text="Close", command=CloseButton, font=("Helvetica", 12), bg="blue", fg="white", padx=20, pady=10)
            close_button.pack(pady=10)
            root.mainloop()
            print('Successfully update!')
            print(requests.get(update, auth=self.auth, verify=False).json())
    
    def GUIstructure(self):
        root = tk.Tk()
        root.title("Update SMART OLS")
        root.configure(bg="lightblue")
        root.update_idletasks() 
        return root

    def core(self):
        """Main function for the updating of the Smart OLS. "getID" is True or False, depending on if the script find or
           not at least one image in the Smart OLS, with the input parameters."""

        getId = self.getImageId()
        if getId:
            updatedJson = self.createUpdatedJSON()
            print(updatedJson)
            self.updateSmartOLS(updatedJson)
        else:
            def CloseButton():
                root.destroy()
            root = self.GUIstructure()
            text = f'No images found, please check that every parameter is correct or contact the Odo.\n If everything is correct, please send the image qc and footprint generated at this\n path {self.imageQcPath}'
            label = tk.Label(root, text = text, font=("Helvetica", 14), bg="lightblue")
            label.pack(pady=10)
            close_button = tk.Button(root, text="Close", command=CloseButton, font=("Helvetica", 12), bg="blue", fg="white", padx=20, pady=10)
            close_button.pack(pady=10)
            root.mainloop()
            