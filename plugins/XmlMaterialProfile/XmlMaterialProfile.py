# Copyright (c) 2016 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

import math
import copy
import xml.etree.ElementTree as ET

from UM.Logger import Logger

import UM.Settings

# The namespace is prepended to the tag name but between {}.
# We are only interested in the actual tag name, so discard everything
# before the last }
def _tag_without_namespace(element):
        return element.tag[element.tag.rfind("}") + 1:]

class XmlMaterialProfile(UM.Settings.InstanceContainer):
    def __init__(self, container_id, *args, **kwargs):
        super().__init__(container_id, *args, **kwargs)

    def serialize(self):
        raise NotImplementedError("Writing material profiles has not yet been implemented")

    def deserialize(self, serialized):
        data = ET.fromstring(serialized)

        self.addMetaDataEntry("type", "material")

        # TODO: Add material verfication
        self.addMetaDataEntry("status", "Unknown")

        metadata = data.iterfind("./um:metadata/*", self.__namespaces)
        for entry in metadata:
            tag_name = _tag_without_namespace(entry)

            if tag_name == "name":
                brand = entry.find("./um:brand", self.__namespaces)
                material = entry.find("./um:material", self.__namespaces)
                color = entry.find("./um:color", self.__namespaces)

                self.setName("{0} {1} ({2})".format(brand.text, material.text, color.text))

                self.addMetaDataEntry("brand", brand.text)
                self.addMetaDataEntry("material", material.text)
                self.addMetaDataEntry("color_name", color.text)

                continue

            self.addMetaDataEntry(tag_name, entry.text)

        property_values = {}
        properties = data.iterfind("./um:properties/*", self.__namespaces)
        for entry in properties:
            tag_name = _tag_without_namespace(entry)
            property_values[tag_name] = entry.text

        diameter = float(property_values.get("diameter", 2.85)) # In mm
        density = float(property_values.get("density", 1.3)) # In g/cm3

        weight_per_cm = (math.pi * (diameter / 20) ** 2 * 0.1) * density

        spool_weight = property_values.get("spool_weight")
        spool_length = property_values.get("spool_length")
        if spool_weight:
            length = float(spool_weight) / weight_per_cm
            property_values["spool_length"] = str(length / 100)
        elif spool_length:
            weight = (float(spool_length) * 100) * weight_per_cm
            property_values["spool_weight"] = str(weight)

        self.addMetaDataEntry("properties", property_values)

        self.setDefinition(UM.Settings.ContainerRegistry.getInstance().findDefinitionContainers(id = "fdmprinter")[0])

        global_setting_values = {}
        settings = data.iterfind("./um:settings/um:setting", self.__namespaces)
        for entry in settings:
            key = entry.get("key")
            if key in self.__material_property_setting_map:
                self.setProperty(self.__material_property_setting_map[key], "value", entry.text, self._definition)
                global_setting_values[self.__material_property_setting_map[key]] = entry.text
            else:
                Logger.log("d", "Unsupported material setting %s", key)

        machines = data.iterfind("./um:settings/um:machine", self.__namespaces)
        for machine in machines:
            machine_setting_values = {}
            settings = machine.iterfind("./um:setting", self.__namespaces)
            for entry in settings:
                key = entry.get("key")
                if key in self.__material_property_setting_map:
                    machine_setting_values[self.__material_property_setting_map[key]] = entry.text
                else:
                    Logger.log("d", "Unsupported material setting %s", key)

            identifiers = machine.iterfind("./um:machine_identifier", self.__namespaces)
            for identifier in identifiers:
                machine_id = self.__product_id_map.get(identifier.get("product"), None)
                if machine_id is None:
                    Logger.log("w", "Cannot create material for unknown machine %s", machine_id)
                    continue

                definitions = UM.Settings.ContainerRegistry.getInstance().findDefinitionContainers(id = machine_id)
                if not definitions:
                    Logger.log("w", "No definition found for machine ID %s", machine_id)
                    continue

                definition = definitions[0]

                new_material = XmlMaterialProfile(self.id + "_" + machine_id)
                new_material.setName(self.getName())
                new_material.setMetaData(copy.deepcopy(self.getMetaData()))
                new_material.setDefinition(definition)

                for key, value in global_setting_values.items():
                    new_material.setProperty(key, "value", value, definition)

                for key, value in machine_setting_values.items():
                    new_material.setProperty(key, "value", value, definition)

                new_material._dirty = False

                UM.Settings.ContainerRegistry.getInstance().addContainer(new_material)

                hotends = machine.iterfind("./um:hotend", self.__namespaces)
                for hotend in hotends:
                    hotend_id = hotend.get("id")
                    if hotend_id is None:
                        continue

                    variant_containers = UM.Settings.ContainerRegistry.getInstance().findInstanceContainers(id = hotend_id)
                    if not variant_containers:
                        # It is not really properly defined what "ID" is so also search for variants by name.
                        variant_containers = UM.Settings.ContainerRegistry.getInstance().findInstanceContainers(definition = definition.id, name = hotend_id)

                    if not variant_containers:
                        Logger.log("d", "No variants found with ID or name %s for machine %s", hotend_id, definition.id)
                        continue

                    new_hotend_material = XmlMaterialProfile(self.id + "_" + machine_id + "_" + hotend_id.replace(" ", "_"))
                    new_hotend_material.setName(self.getName())
                    new_hotend_material.setMetaData(copy.deepcopy(self.getMetaData()))
                    new_hotend_material.setDefinition(definition)

                    new_hotend_material.addMetaDataEntry("variant", variant_containers[0].id)

                    for key, value in global_setting_values.items():
                        new_hotend_material.setProperty(key, "value", value, definition)

                    for key, value in machine_setting_values.items():
                        new_hotend_material.setProperty(key, "value", value, definition)

                    settings = hotend.iterfind("./um:setting", self.__namespaces)
                    for entry in settings:
                        key = entry.get("key")
                        if key in self.__material_property_setting_map:
                            new_hotend_material.setProperty(self.__material_property_setting_map[key], "value", entry.text, definition)
                        else:
                            Logger.log("d", "Unsupported material setting %s", key)

                    new_hotend_material._dirty = False
                    UM.Settings.ContainerRegistry.getInstance().addContainer(new_hotend_material)


    # Map XML file setting names to internal names
    __material_property_setting_map = {
        "print temperature": "material_print_temperature",
        "heated bed temperature": "material_bed_temperature",
        "standby temperature": "material_standby_temperature",
        "print cooling": "cool_fan_speed",
        "retraction amount": "retraction_amount",
        "retraction speed": "retraction_speed",
    }

    # Map XML file product names to internal ids
    __product_id_map = {
        "Ultimaker2": "ultimaker2",
        "Ultimaker2+": "ultimaker2_plus",
        "Ultimaker2go": "ultimaker2_go",
        "Ultimaker2extended": "ultimaker2_extended",
        "Ultimaker2extended+": "ultimaker2_extended_plus",
        "Ultimaker Original": "ultimaker_original",
        "Ultimaker Original+": "ultimaker_original_plus"
    }

    __namespaces = {
        "um": "http://www.ultimaker.com/material"
    }
