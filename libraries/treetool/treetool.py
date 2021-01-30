from time import sleep
from pathlib import Path

import os
import json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Treetool:
    """Get information about a 3D model from CREO or Treetool
    creo_get = Booleon (True, connect to CREO use standard treetool mapkey - slow)
    param_list = two dimentional array (Selected parameters from model only)
    example: [["Note", "First Line"],["Info","Feat ID"],["Info","Feat #"],["Model Params","ITEMCODE"]]
    treetool_location = path to treetool.txt file (if existing can be used to bypass connection to CREO)
    return allparts dictionary of information about model tree"""
    def __init__(self, 
                creo_get=False, 
                param_list=False, 
                treetool_location='C:/PTC/Bar_Start_Creo/Drawing-exchange/treetool.txt',
                ):
        self.location = treetool_location
        if creo_get or param_list:
            
            from pycreo import client as pycreo
            self.client = pycreo.CreosonClient()
            self.session_id = self.connectCS()
            print(f"CREOSON - Session_id {self.session_id}")
            "This get information from CREO"
            self.active = self.activeM()
            if not self.active:
                raise NameError("Error on CREO Connection, or no active model")
            if param_list:
                "Specify what CREO parameters you want"
                self.autolysis(param_list)
                if self.get_lines('%treetool09'):
                    self.lines = self.treetool_lines()
            else:
                if self.get_lines("%treetool01"):
                    self.lines = self.treetool_lines()
            self.asm_dict_tree()
        else:
            "Assume treetool.txt exists"
            self.lines = self.treetool_lines()
        if self.lines:
            
            pass
    
    
    def connectCS(self):
        try:
            ses_id, err = self.client.connect()
            return ses_id
        except:
            print("CANNOT CONNECT TO CREOSON...")
            creo_start = "C:/ptc/start_creoson.bat"
            if os.path.isfile(creo_start):
                os.system(creo_start)
            for i in range(0, 10):
                try:
                    ses_id, err = self.client.connect()
                    break
                except:
                    err = True
                    print(f"TRYING TO CONNECT TO CREOSON TRY: {i}")
                    pass
                sleep(1)
            if err:
                print("COULD NOT CONNECT TO CREOSON")
                return False
            else:
                return ses_id
            
    def activeM(self):
        active = (self.client.get_active(self.session_id))
        if active==True or active==None:
            return False
        active = active["file"]
        if active == None:
            active = False
        return active
        

    # paraPull is an array of model parameters which should appear in treetool
    @staticmethod
    def autolysis(paraPull):
        file = "C:/PTC/creo_stds/tree_config/autolysis.cfg"

        with open(file, 'w') as f:
            f.write("""!PTC Creo Parametric cfg file Version No. 1 
!Creo  TM  3.0  (c) 2019 by PTC Inc.  All Rights Reserved. \n""")
            # This makes sure the First Line is always writing at the end of treetool.txt
            first = False
            paraPull.append(["Note", "First Line"])
            for param, value in paraPull:
                if "First Line" in value:
                    first = True
                    firstline = param, value
                else:
                    f.write('COLUMN "' + param + '" "' + value + '" 14\n')
            if ["Info", "Feature Status"] not in paraPull:
                f.write('COLUMN "Info" "Feature Status" 14\n')
            if ["Model Params", "PRT_CLASS"] not in paraPull:
                f.write('COLUMN "Model Params" "PRT_CLASS" 14\n')
            if ["Model Params", "CREO_MODEL_TYPE"] not in paraPull:
                f.write('COLUMN "Model Params" "CREO_MODEL_TYPE" 14\n')
            if ["Model Params", "MAT_DESC"] not in paraPull:
                f.write('COLUMN "Model Params" "MAT_DESC" 14\n')
            if first:
                f.write('COLUMN "' + firstline[0] + '" "' + firstline[1] + '" 14\n')
            f.write("""SUPPRESSED    ON
EXCLUDED    ON
FEATURES    ON
MFG_OWNER    ON
NOTES    ON
BLANKED    ON
INCOMPLETE    ON
COMPS    ON
BT_BODY_CONNS    ON
BT_INCOMING_CONNS    ON
BT_BODY_CONTS    ON
BT_MOTION_AXES    ON
ENVELOPE    ON
COMP_PLACEMENT    OFF
GEOM_BACKUPS    ON
MECH_STR    ON
MECH_THR    ON
MOLD_OWNER    ON
SECTIONS    ON""")


    def get_lines(self, treetool_map):
        ready = "C:\\PTC\\Bar_Start_Creo\\Drawing-exchange\\ready.txt"
        if os.path.isfile(ready):
            os.remove(ready)
        self.client.mapkey(self.session_id, treetool_map)
        counter = 0
        while not os.path.isfile(ready):
            counter += 1
            sleep(1)
            print(str(counter) + " - TREETOOL RUNNING")
        return True
    # Return two element array first element is name of part
    # and the second is the generic name of the family table
    # if they are the same you are dealing with the generic

    def treetool_lines(self):
        if os.path.isfile(self.location):
            
            with open(self.location, encoding='utf8') as g:
                lines = g.read().splitlines()
            return lines
        else:
            return False
    

    def mapkeyFunction(self, text, limit=False):
        """Text == mapkey to run
        limit == defautl == False, else == int() timer for maximum wait time"""

        text = text + ";"
        text = text.replace("mapkey(continued) ", "")
        text = text.replace(";\\", ";")
        text = text.replace(" \\", " ")
        text = text.replace("\n", "")
        text = text.replace("; ~", ";~")

        # This add to the mapkey to create a ready.txt file
        text = text + '@SYSTEM"cd" > C:\\\\PTC\\\\Bar_Start_Creo\\\\Drawing-exchange\\\\ready.txt;'
        ready = "C:\\PTC\\Bar_Start_Creo\\Drawing-exchange\\ready.txt"
        if os.path.isfile(ready):
            os.remove(ready)

        self.client.mapkey(self.session_id, script=text)
        counter = 0
        print(limit)

        while not os.path.isfile(ready):
            counter += 1
            print(counter)
            sleep(1)
            if limit:
                if counter >= limit:
                    break

            # if counter % 10000 == 0:
                # print(str(int(counter/10000)) + " Awaiting Mapkey to Finish")
        # This delete the ready.txt file, which sometimes don't have write access

        # The while loop tries till it deletes it.
        if not os.path.isfile(ready):
            return False
        else:
            os.remove(ready)
            return True
            sleep(1)
    

    def asm_dict_tree(self):
        text = """
        mapkey(continued) ~ Command `ProCmdMdlTreeFilter` ;\\
        mapkey(continued) ~ Activate `mdl_filter` `unselect_all_btn`;\\
        mapkey(continued) ~ Activate `mdl_filter` `feat_btn` 0;\\
        mapkey(continued) ~ Activate `mdl_filter` `note_btn` 0;\\
        mapkey(continued) ~ Activate `mdl_filter` `section_btn` 0;\\
        mapkey(continued) ~ Activate `mdl_filter` `supres_btn` 0;\\
        mapkey(continued) ~ Activate `mdl_filter` `incomp_btn` 0;\\
        mapkey(continued) ~ Activate `mdl_filter` `exclud_btn` 0;\\
        mapkey(continued) ~ Activate `mdl_filter` `blank` 0;\\
        mapkey(continued) ~ Activate `mdl_filter` `envelope_btn` 0;\\
        mapkey(continued) ~ Activate `mdl_filter` `ok_btn`;\\
        mapkey(continued) ~ Command `ProCmdMdlTreeExpandAll` ;\\
        mapkey(continued) ~ Command `ProCmdMdlTreeSaveAsText` ;\\
        mapkey(continued) ~ Update `inputname` `InpName` \\
        mapkey(continued) `C:\\\\PTC\\\\Bar_Start_Creo\\\\Drawing-exchange\\\\treetool00.txt`;\\
        mapkey(continued) ~ Activate `inputname` `InpName`;\\
        mapkey(continued) ~ Command `ProCmdMdlTreeFilter` ;\\
        mapkey(continued) ~ Activate `mdl_filter` `select_all_btn`;\\
        mapkey(continued) ~ Activate `mdl_filter` `feat_btn` 1;\\
        mapkey(continued) ~ Activate `mdl_filter` `note_btn` 1;\\
        mapkey(continued) ~ Activate `mdl_filter` `section_btn` 1;\\
        mapkey(continued) ~ Activate `mdl_filter` `supres_btn` 1;\\
        mapkey(continued) ~ Activate `mdl_filter` `incomp_btn` 1;\\
        mapkey(continued) ~ Activate `mdl_filter` `exclud_btn` 1;\\
        mapkey(continued) ~ Activate `mdl_filter` `blank` 1;\\
        mapkey(continued) ~ Activate `mdl_filter` `envelope_btn` 1;\\
        mapkey(continued) ~ Activate `mdl_filter` `placement_btn` 0;\\
        mapkey(continued) ~ Activate `mdl_filter` `ok_btn`;\\
        mapkey(continued) ~ Command `ProCmdMdlTreeCollapseAll` ;\\
        mapkey(continued) ~ Select `main_dlg_cur` `PHTLeft.AssyTree` 1 `node0`;\\
        mapkey(continued) ~ Activate `main_dlg_cur` `PHTLeft.AssyTree` 1 `node0`;\\
        """
        
        self.mapkeyFunction(text)

class AllpartsJson(Treetool):
    """Get information about a 3D model from CREO or Treetool
    creo_get = Booleon (True, connect to CREO use standard treetool mapkey - slow)
    param_list = two dimentional array (Selected parameters from model only)
    treetool_location = path to treetool.txt file (if existing can be used to bypass connection to CREO)
    return allparts dictionary of information about model tree"""
    def __init__(self, creo_get=False, param_list=False, treetool_location='C:/PTC/Bar_Start_Creo/Drawing-exchange/treetool.txt', details=True, workdir=False):

        super().__init__(creo_get=creo_get,
                        param_list=param_list, 
                        treetool_location=treetool_location)
        self.employee_csv = os.path.join(BASE_DIR, 'data/employees.csv')
        self.allparts = self.AllElements(details=details)

        asmname_line = str(self.lines[2])
        self.asmname = self.partname(asmname_line)[0]

        if workdir:
            workdir = str(Path(workdir))
            
            data_path = str(Path(os.path.join(workdir, self.asmname[:-4], "data")))
            if not os.path.exists(data_path):
                os.makedirs(data_path)
            self.allpart_json_file = str(Path(os.path.join(data_path, "allparts.json")))
            self.json_dumper(self.allpart_json_file, self.allparts)

            self.asmDict_json_file = str(Path(os.path.join(data_path, 'asmDict.json')))
            self.json_dumper(self.asmDict_json_file, self.asmDict())

    def json_dumper(self, file, json_dict):
        with open(file, 'w') as fp:
            json.dump(json_dict, fp)


    def elementCounter(self):
        elements = []
        counter = {}
        for line in self.lines:
            if self.partname(line) and "Suppressed" not in line:
                elements.append(self.partname(line)[0])
        for el in elements:
            counter.update({el : elements.count(el)})

        return counter
    

    def parameters(self):
        para = self.lines[0].split("  ")[1:]
        para[:] = [names for names in para if names != ""][1:]
        for x in range(0, len(para)):
            para[x] = " " + para[x].strip() + " "
        return para
    
    def parameter_position(self, parameter):
        parameters = self.parameters()
        parameter = " " + parameter + " "
        start = self.lines[0].find(parameters[parameters.index(parameter)]) - 2
        if parameters.index(parameter) == len(parameters)-1:
            end = len(self.lines[0])-3
        else:
            end = self.lines[0].find(parameters[parameters.index(parameter) + 1]) - 2
        position = [start, end]
        return position

    @staticmethod
    def paraDetail(parameter_pos, line):
        try:
            return line[parameter_pos[0]:parameter_pos[1]].strip().lower()
        except:
            return False
    
    @staticmethod
    def familyNames(name):
        family = name
        generic = name
        if "<" in name:
            family = name[:name.find("<")] + name[name.find("."):]
            generic = name[name.find("<")+1:name.find(">")] + name[name.find("."):]
        return [family, generic]

    def partname(self, line):
        if (".prt" in line.lower() or ".asm" in line.lower()) and "pattern" not in line.lower() and "suppress" not in line.lower():
            return self.familyNames(line.split()[0])
        return False  
    
    def getUser(self):
        import csv
        userProfile = os.getlogin()
        userEmail = ""

        with open(self.employee_csv,"r") as csvfile:
            readCSV = csv.reader(csvfile, delimiter=';')

            for row in readCSV:
                firstName = row[0]
                lastName = row[1]
                email = row[2]
                fullName = firstName + " " + lastName
                trelloID = row[6]

                if (lastName.lower() in userProfile.lower() and firstName[0].lower() == userProfile[0].lower()):
                    # userName = firstName + " " + lastName
                    userEmail = email
                    userID = trelloID
                    break
        if userEmail == "":
            userEmail = "martin.cronje@barrowsglobal.com"
            userID = "533acb8a542e7a9f0c1f49f9"
        
        return userEmail, userID 
    
    @staticmethod
    def accessories():
        acc_dir = "C:\\PTC\\creo_stds\\accessories"
        accessories = []

        for root, dirs, files in os.walk(acc_dir, topdown=False):
            for file in files:
                if ".prt" in file or ".asm" in file:
                    accessories.append(file[:file.rfind(".")])
        
        return accessories
    
    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    #posCounter create a extention of a name at the end of part based on the order it appear in treetool
    def posCounter(self, line, prtCounter, asmCounter, eleCounter, ledCounter):
        FullName = self.partname(line)
        part = FullName[0].lower()
        prt_class = self.paraDetail(self.parameter_position("PRT_CLASS"), line).lower()
        mat_desc = self.paraDetail(self.parameter_position("MAT_DESC"), line).lower()
        if ".asm" in part and (mat_desc == "harness" or prt_class == "harness") and prt_class != "" and prt_class != "bar":
            eleCounter += 1
            if eleCounter < 10:
                partPosition = "H0" + str(eleCounter)
            else:
                partPosition = "H" + str(eleCounter)
        elif ".asm" in part and prt_class != "" and prt_class != "bar":
            asmCounter += 1
            if asmCounter < 10:
                partPosition = "A0" + str(asmCounter)
            else:
                partPosition = "A" + str(asmCounter)
        elif ".prt" in part and mat_desc == "led":
            ledCounter += 1
            if ledCounter < 10:
                partPosition = "FL0" + str(ledCounter)
            else:
                partPosition = "FL" + str(ledCounter)
        elif ".prt" in part and (prt_class != "acc" and prt_class != "elec" and prt_class != "bar" and prt_class != ""):
            prtCounter += 1
            if prtCounter < 10:
                partPosition = "P0" + str(prtCounter)
            else:
                partPosition = "P" + str(prtCounter)
        else:
            return [False, prtCounter, asmCounter, eleCounter, ledCounter]
        return [partPosition, prtCounter, asmCounter, eleCounter, ledCounter]

    def AllElements(self, details=True):
        allparts = {}
        prtCounter = 0
        asmCounter = 0
        eleCounter = 0
        ledCounter = 0
        lineCounter = 0
        
        accList = self.accessories()
        AsmFeatID = []
        AsmIDcounter = 0
        asmname_line = str(self.lines[2])
        asmname = self.partname(asmname_line)
        if self.lines:
            countedElements = self.elementCounter()
            paramNames = self.parameters()
            for line in self.lines:
                
                lineCounter += 1
                bends = 0
                if self.partname(line):
                    loc = (self.parameter_position("PRT_CLASS"), line)
                    prt_class = self.paraDetail(self.parameter_position("PRT_CLASS"), line).lower()
                    if prt_class != "bar":
                        qty = countedElements[self.partname(line)[0]]
                        treePositionID = []

                        if ".asm" in self.partname(line)[0].lower():
                            if " Feat ID " in paramNames:
                                FeatID = self.paraDetail(self.parameter_position("Feat ID"), line).lower()
                                AsmFeatID = [[len(line) - len(line.lstrip()), FeatID]] + AsmFeatID

                        if self.partname(line)[0] not in allparts.keys():
                            itemParameters = {}
                            # Don't count accessories to get the counter position for RENAMING app
                            if self.partname(line)[1].lower() not in accList:
                                position_output = self.posCounter(line, prtCounter, asmCounter, eleCounter, ledCounter)
                                partPosition = position_output[0]
                                prtCounter = position_output[1]
                                asmCounter = position_output[2]
                                eleCounter = position_output[3]
                                ledCounter = position_output[4]
                            
                            # This add all the HEADERS from TREETOOL in the dictionary
                            for para in paramNames:
                                itemParameters.update({para[1:-1] : self.paraDetail(self.parameter_position(para[1:-1]), line)})

                            # This finds the parent assembly for the component in question.
                            if " Feat ID " in paramNames:
                                asm_locaton = ""
                                for distance in AsmFeatID:
                                    step = 2
                                    if "PATTERN" in self.lines[AsmIDcounter - 1].upper():
                                        step = 4
                                    if len(line) - len(line.lstrip()) - step == distance[0]:
                                        if self.is_number(distance[1]):
                                            asm_locaton = distance[1]
                                        break
                            
                            # Adding the Feat ID and Feat # of a component it is exists in the headers from TREETOOL
                            if " Feat # " in paramNames and " Feat ID " in paramNames:
                                FeatNO = self.paraDetail(self.parameter_position( "Feat #"), line).lower()
                                FeatID = self.paraDetail(self.parameter_position("Feat ID"), line).lower()
    
                                if [FeatNO, FeatID, asm_locaton] not in treePositionID:
                                    treePositionID.append([FeatNO, FeatID, asm_locaton])
                            itemParameters.update({"treePositionID" : treePositionID})

                            itemParameters.update({"model_tree_position" : partPosition})

                            # Checking if part is has a jig:
                            if " JIG " in paramNames:
                                if "yes" in self.paraDetail(self.parameter_position("JIG"), line).lower():
                                    itemParameters.update({"JIG" : True})

                            # Check features for information:
                            if ".prt" in self.partname(line)[0].lower():
                                tempCounter = lineCounter

                                # sheetType can be:
                                # 1. sheet
                                # 2. solid
                                # 3. bend
                                # 4. form

                                # tubeType can be:
                                # 1. solid
                                # 2. extrusion
                                # 3. sheet
                                # Note thet tubeType only search for to find undefined TUBES/WIRES/SHEET
                                if self.partname(line)[1].lower() == "cable.prt":
                                    itemParameters.update({"tubeType" : "cable"})
                                    itemParameters.update({"sheetType" : "cable"})
                                else:
                                    itemParameters.update({"tubeType" : "solid"})
                                    itemParameters.update({"sheetType" : "solid"})
                                areaExists = False
                                volExists = False

                                Manual_Length = False
                                Manual_Width = False
                                Manual_Height = False
                                Manual_Thickness = False

                                while "Insert Here" not in self.lines[tempCounter] and details and tempCounter != len(self.lines)-1:
                                    if "S_LENGTH" in self.lines[tempCounter].upper():
                                        Manual_Length = True
                                    if "S_WIDTH" in self.lines[tempCounter].upper():
                                        Manual_Width = True
                                    if "S_HEIGHT" in self.lines[tempCounter].upper():
                                        Manual_Height = True
                                    if "S_THICKNES" in self.lines[tempCounter].upper():
                                        Manual_Thickness = True
                                    
                                    if Manual_Thickness:
                                        itemParameters.update({"sheetType" : "sheet"})
                                        itemParameters.update({"tubeType" : "sheet"})
                                    
                                    if not (Manual_Length or Manual_Width or Manual_Height or Manual_Thickness):
                                    
                                        if "First Wall" in self.lines[tempCounter]:
                                            itemParameters.update({"sheetType" : "sheet"})
                                            
                                        if "BEND_NOTE" in self.lines[tempCounter].upper():
                                            itemParameters.update({"sheetType" : "bend"})
                                            bends += 1
                                            bend_type = self.paraDetail(self.parameter_position("First Line"), self.lines[tempCounter]).lower()
                                            # Finding forming components and switch on JIGS
                                            if "x80" in str(bend_type.split("***")[0].encode("utf-8")):
                                                itemParameters.update({"JIG" : True})
                                                itemParameters.update({"sheetType" : "form"})
                                        
                                        if "FLATPATTERN" in self.lines[tempCounter]:
                                            itemParameters.update({"tubeType" : "sheet"})
                                        
                                        # Checking if extrusion:
                                        try:
                                            if self.lines[tempCounter].split()[0].strip().upper() == "AREA":
                                                areaExists = True
                                        except:
                                            pass
                                        
                                        try:
                                            if self.lines[tempCounter].split()[0].strip().upper() == "VOL":
                                                volExists = True
                                        except:
                                            pass

                                        if areaExists and volExists:
                                            itemParameters.update({"tubeType" : "extrusion"})
                                                                    
                                    tempCounter += 1
        
                            allparts.update({self.partname(line)[0] : itemParameters})

                        elif self.partname(line)[0] in allparts.keys() and " Feat # " in  paramNames and " Feat ID " in paramNames:
                            for featIDNO in allparts[self.partname(line)[0]]["treePositionID"]:
                                treePositionID.append(featIDNO)
                            FeatNO = self.paraDetail(self.parameter_position("Feat #"), line)
                            FeatID = self.paraDetail(self.parameter_position("Feat ID"), line)

                            asm_locaton = ""
                            for distance in AsmFeatID:
                                step = 2
                                if "PATTERN" in self.lines[AsmIDcounter - 1].upper():
                                    step = 4
                                if len(line) - len(line.lstrip()) - step == distance[0]:
                                    if self.is_number(distance[1]):
                                        asm_locaton = distance[1]
                                    break
                            
                            if [FeatNO, FeatID, asm_locaton] not in treePositionID:
                                posInfo = allparts[self.partname(line)[0]]["treePositionID"]
                                allparts[self.partname(line)[0]]["treePositionID"] = [[FeatNO, FeatID, asm_locaton]] + posInfo
                        allparts[self.partname(line)[0]]["COUNTED_QTY"] = qty
        userEmail, UserId = self.getUser()
        allparts[asmname[0]]['publisher'] = userEmail
        return allparts
    
 
    @staticmethod
    def treetool_lines_filename(filename):
        location = 'C:\\PTC\\Bar_Start_Creo\\Drawing-exchange\\' + filename + '.txt'
        with open(location, encoding='utf8') as g:
            lines = g.read().splitlines()
        return lines
    
    @staticmethod
    def lineSpace(line, space):
        line = line[space:]
        return line

    @staticmethod
    def startSpace(line):
        return len(line) - len(line.lstrip())
    

    def relines(self, linList, mark):
        for x in range(0, len(linList)):
            if mark in linList[x].lower():
                marker = self.startSpace(linList[x])
                counter = 1
                while self.startSpace(linList[x+counter]) > marker:
                    newLine = self.lineSpace(linList[x+counter], 2)
                    linList[x+counter] = newLine
                    counter += 1
        return linList

    
    def asm(self, harnessAssemblies, accList):
        # This export a list of lines which should be changed.
        partlines = self.treetool_lines_filename('treetool00')
        partlines.append("martin")

        if any("group" in s.lower() for s in partlines):
            partlines = self.relines(partlines, "group")

        if any("pattern" in s.lower() for s in partlines):
            partlines = self.relines(partlines, "pattern")

        asmDict = {}

        for x in range(0, len(partlines)):
            if "pattern" not in partlines[x].lower() and "group" not in partlines[x].lower():
                if ".asm" in partlines[x].lower():
                    part = []
                    asmname = partlines[x].split()[0].strip()
                    counter = 1
                    marker = self.startSpace(partlines[x])
                    while self.startSpace(partlines[x+counter]) > marker:
                        partname = self.familyNames(partlines[x+counter].split()[0].strip())[0]
                        if "pattern" not in partlines[x+counter].lower() and "group" not in partlines[x+counter].lower():
                            if marker + 2 == self.startSpace(partlines[x+counter]):
                                # None Harness assemblies goes here:
                                if asmname.lower() not in harnessAssemblies:
                                    part.append(partname)
                                    # part = list(set(part))
                                else:
                                    # Harness assemblies goes here
                                    part.append(partname)
                            # Making sure we capture harness assembly elements despite of the depth of the components (".prt" only)
                            elif ".prt" in partlines[x+counter].lower() and asmname.lower() in harnessAssemblies:
                                if asmname.lower() in harnessAssemblies:
                                    part.append(partname)

                        counter += 1
                    if self.familyNames(asmname)[1].lower() not in accList:
                        asmdict = {asmname : part}
                        asmDict.update(asmdict)
        return asmDict
    

    @staticmethod
    def accessories():
        """
        accessories() export a list of generic names of all the items in the library.
        """
        acc_dir = "C:\\PTC\\creo_stds\\accessories"
        accessories = []

        for root, dirs, files in os.walk(acc_dir, topdown=False):
            for file in files:
                if ".prt" in file or ".asm" in file:
                    accessories.append(file[:file.rfind(".")])

        return accessories


    def asmDict(self):
        """Getting Harness assemblies"""
        harnessAssemblies = []
        for harness in self.allparts:
            if self.allparts[harness]["PRT_CLASS"].lower() == "harness":
                harnessAssemblies.append(harness.lower())

        accList = list(set(self.accessories()))

        asmDict = self.asm(harnessAssemblies, accList)
        return asmDict
    
