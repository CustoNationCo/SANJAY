# Display Filename and Layer on the LCD by Amanda de Castilho on August 28, 2018
# Modified: Joshua Pope-Lewis on November 16, 2018 
# Display Progress on LCD by Mathias Lyngklip Kjeldgaard, Alexander Gee, Kimmo Toivanen, Inigo Martinez on July 31, 2019
# Show Progress was adapted from Display Progress by Louis Wooters on January 6, 2020.  His changes are included here.
#---------------------------------------------------------------
# DisplayNameOrProgressOnLCD.py
# Cura Post-Process plugin
# Combines 'Display Filename and Layer on the LCD' with 'Display Progress'
# Combined and adapted by: GregValiant (Greg Foresi)
# Date:       March 5, 2023
# NOTE:  This combined post processor will make 'Display Filename and Layer on the LCD' and 'Display Progress' obsolete
# Description:  Display Filename and Layer options:
#           Status messages sent to the printer...
#               - Scrolling (SCROLL_LONG_FILENAMES) if enabled in Marlin and you aren't printing a small item select this option.
#               - Name: By default it will use the name generated by Cura (EG: TT_Test_Cube) - You may enter a custom name here
#               - Start Num: Choose which number you prefer for the initial layer, 0 or 1
#               - Max Layer: Enabling this will show how many layers are in the entire print (EG: Layer 1 of 265!)
#               - Add prefix 'Printing': Enabling this will add the prefix 'Printing'
#               - Example Line on LCD:  Printing Layer 0 of 395 3DBenchy
#           Display Progress options:
#               - Display Total Layer Count
#               - Disply Time Remaining for the print
#               - Time Fudge Factor % - Divide the Actual Print Time by the Cura Estimate.  Enter as a percentage and the displayed time will be adjusted.
#                 This allows you to bring the displayed time closer to reality (Ex: Entering 87.5 would indicate an adjustement to 87.5% of the Cura estimate).
#               - Example line on LCD:  1/479 | ET 2h13m
#            - 'Add M118 Line' is available with either option.  M118 will bounce the message back to a remote print server through the USB connection.

from ..Script import Script
from UM.Application import Application

class DisplayNameOrProgressOnLCD(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Disp Layer&Filename or Disp Progress",
            "key": "DisplayNameOrProgressOnLCD",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "display_option":
                {
                    "label": "LCD display option...",
                    "description": "Display Filename and Layer was formerly 'Display Filename and Layer on LCD' post-processor.  The message format on the LCD is 'Printing Layer 0 of 15 3D Benchy'.  Display Progress is similar to the former 'Display Progress on LCD' post-processor.  The display format is '1/16 | ET 2hr28m'.  Display Progress includes a fudge factor for the print time estimate.",
                    "type": "enum",
                    "options": {
                        "display_progress": "Display Progress",
                        "filename_layer": "Filename and Layer"
                        },
                    "default_value": "display_progress"
                },
                "format_option":
                {
                    "label": "Scroll enabled/Small layers?",
                    "description": "If SCROLL_LONG_FILENAMES is enabled in your firmware select this setting.",
                    "type": "bool",
                    "default_value": false,
                    "enabled": "display_option == 'filename_layer'"
                },
                "name":
                {
                    "label": "Text to display:",
                    "description": "By default the current filename will be displayed on the LCD. Enter text here to override the filename and display something else.",
                    "type": "str",
                    "default_value": "",
                    "enabled": "display_option == 'filename_layer'"
                },
                "startNum":
                {
                    "label": "Initial layer number:",
                    "description": "Choose which number you prefer for the initial layer, 0 or 1",
                    "type": "int",
                    "default_value": 0,
                    "minimum_value": 0,
                    "maximum_value": 1,
                    "enabled": "display_option == 'filename_layer'"                 
                },
                "maxlayer":
                {
                    "label": "Display max layer?:",
                    "description": "Display how many layers are in the entire print on status bar?",
                    "type": "bool",
                    "default_value": true,
                    "enabled": "display_option == 'filename_layer'"
                },
                "addPrefixPrinting":
                {
                    "label": "Add prefix 'Printing'?",
                    "description": "This will add the prefix 'Printing'",
                    "type": "bool",
                    "default_value": true,
                    "enabled": "display_option == 'filename_layer'"
                },
                "display_total_layers":
                {
                    "label": "Display total layers",
                    "description": "This setting adds the 'Total Layers' to the LCD message as '17/234'.",
                    "type": "bool",
                    "default_value": true,
                    "enabled": "display_option == 'display_progress'"
                },
                "display_remaining_time":
                {
                    "label": "Display remaining time",
                    "description": "This will add the remaining printing time to the LCD message.",
                    "type": "bool",
                    "default_value": true,
                    "enabled": "display_option == 'display_progress'"
                },
                "add_m118_line":
                {
                    "label": "Add M118 Line",
                    "description": "Adds M118 in addition to the M117.  It will bounce the message back through the USB port to a computer print server (if a printer server is enabled).",
                    "type": "bool",
                    "default_value": false
                },
                "speed_factor":
                {
                    "label": "Time Fudge Factor %",
                    "description": "Tweak this value to get better estimates. ([Actual Print Time]/[Cura Estimate]) x 100 = Time Fudge Factor.  If Cura estimated 9hr and the print actually took 10hr30min then enter 117 here to adjust any estimate closer to reality.",
                    "type": "float",
                    "unit": "%",
                    "default_value": 100,
                    "enabled": "display_option == 'display_progress'"
                }
            }
        }"""

    def execute(self, data):
        display_option = self.getSettingValueByKey("display_option")
        add_m118_line = self.getSettingValueByKey("add_m118_line")

# This is Display Filename and Layer on LCD---------------------------------------------------------
        if display_option == "filename_layer":
            max_layer = 0
            lcd_text = "M117 "
            if self.getSettingValueByKey("name") != "":
                name = self.getSettingValueByKey("name")
            else:
                name = Application.getInstance().getPrintInformation().jobName
            if self.getSettingValueByKey("addPrefixPrinting"):
                lcd_text += "Printing "
            if not self.getSettingValueByKey("scroll"):
                lcd_text += "Layer "
            else:
                lcd_text += name + " - Layer "
            i = self.getSettingValueByKey("startNum")
            for layer in data:
                display_text = lcd_text + str(i)
                layer_index = data.index(layer)
                lines = layer.split("\n")
                for line in lines:
                    if line.startswith(";LAYER_COUNT:"):
                        max_layer = line
                        max_layer = max_layer.split(":")[1]
                        if self.getSettingValueByKey("startNum") == 0:
                            max_layer = str(int(max_layer) - 1)
                    if line.startswith(";LAYER:"):
                        if self.getSettingValueByKey("maxlayer"):
                            display_text = display_text + " of " + max_layer
                            if not self.getSettingValueByKey("scroll"):
                                display_text = display_text + " " + name
                        else:
                            if not self.getSettingValueByKey("scroll"):
                                display_text = display_text + " " + name + "!"
                            else:
                                display_text = display_text + "!"
                        line_index = lines.index(line)
                        lines.insert(line_index + 1, display_text)
                        if add_m118_line:
                            lines.insert(line_index + 2, str(display_text.replace("M117", "M118", 1)))
                        i += 1
                final_lines = "\n".join(lines)
                data[layer_index] = final_lines

# Display Progress from Show Progress and Display Progress on LCD------------------------------------------------------
        elif display_option == "display_progress":
        # get settings
            display_total_layers = self.getSettingValueByKey("display_total_layers")
            display_remaining_time = self.getSettingValueByKey("display_remaining_time")
            speed_factor = self.getSettingValueByKey("speed_factor") / 100

        # initialize global variables
            first_layer_index = 0
            time_total = 0
            number_of_layers = 0
            time_elapsed = 0
        # if at least one of the settings is disabled, there is enough room on the display to display "layer"
            first_section = data[0]
            lines = first_section.split("\n")
            for line in lines:
                if ";TIME:" in line:
                    tindex = lines.index(line)
                    print_time = int(line.split(":")[1])
                    print_time = print_time*speed_factor
                    hhh = print_time/3600
                    hr = round(hhh // 1)
                    mmm = round((hhh % 1) * 60)
                    if add_m118_line: lines.insert(tindex+1,"M118 Adjusted Print Time " + str(hr) + "hr " + str(mmm) + "min")
                    lines.insert(tindex+1,"M117 ET " + str(hr) + "hr " + str(mmm) + "min")
                    data[0] = "\n".join(lines)
                    data[len(data)-1] += "M117 Orig Est " + str(hr) + "hr " + str(mmm) + "min\n"
                    if add_m118_line: data[len(data)-1] += "M118 Orig Est w/FudgeFactor at " + str(speed_factor * 100) + "% was " + str(hr) + "hr " + str(mmm) + "min\n"
            if not display_total_layers or not display_remaining_time:
                base_display_text = "layer "
            else:
                base_display_text = ""

        # Search for the number of layers and the total time from the start code
            for index in range(len(data)):
                data_section = data[index]
        # We have everything we need, save the index of the first layer and exit the loop
                if data_section.startswith(";LAYER:"):
                    first_layer_index = index
                    break
                else:
                    for line in data_section.split("\n"):
                        if line.startswith(";LAYER_COUNT:"):
                            number_of_layers = int(line.split(":")[1])
                        elif line.startswith(";TIME:"):
                            time_total = int(line.split(":")[1])
        # for all layers...
            for layer_counter in range(number_of_layers):
                current_layer = layer_counter + 1
                layer_index = first_layer_index + layer_counter
                display_text = base_display_text
                display_text += str(current_layer)

        # create a list where each element is a single line of code within the layer
                lines = data[layer_index].split("\n")

        # add the total number of layers if this option is checked
                if display_total_layers:
                    display_text += "/" + str(number_of_layers)

        # if display_remaining_time is checked, it is calculated in this loop
                if display_remaining_time:
                    time_remaining_display = " | ET "  # initialize the time display
                    m = (time_total - time_elapsed) // 60  # estimated time in minutes
                    m *= speed_factor  # correct for printing time
                    m = int(m)
                    h, m = divmod(m, 60)  # convert to hours and minutes

        # add the time remaining to the display_text
                    if h > 0:  # if it's more than 1 hour left, display format = xhxxm
                        time_remaining_display += str(h) + "h"
                        if m < 10:  # add trailing zero if necessary
                            time_remaining_display += "0"
                        time_remaining_display += str(m) + "m"
                    else:
                        time_remaining_display += str(m) + "m"
                    display_text += time_remaining_display
        # find time_elapsed at the end of the layer (used to calculate the remaining time of the next layer)
                    if not current_layer == number_of_layers:
                        for line_index in range(len(lines) - 1, -1, -1):
                            line = lines[line_index]
                            if line.startswith(";TIME_ELAPSED:"):
        # update time_elapsed for the NEXT layer and exit the loop
                                time_elapsed = int(float(line.split(":")[1]))
                                break

        # insert the text AFTER the first line of the layer (in case other scripts use ";LAYER:")
                lines[0] = lines[0] + "\nM117 " + display_text
                
                if add_m118_line:
                    lines[0] = lines[0] + "\nM118 " + display_text

        # overwrite the layer with the modified layer
                data[layer_index] = "\n".join(lines)
        
        data[1] = ";  Display Layer and Filename | Display Progress (Option: " + str(display_option) + ")\n" + data[1]
        return data
