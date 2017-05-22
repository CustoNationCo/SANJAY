# Copyright (c) 2017 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

import xml.etree.ElementTree as ET

from UM.VersionUpgrade import VersionUpgrade


class XmlMaterialUpgrader(VersionUpgrade):
    def getXmlVersion(self, serialized):
        data = ET.fromstring(serialized)

        # get format version
        version = None
        metadata = data.iterfind("./um:metadata/*")
        for entry in metadata:
            tag_name = entry.tag
            if tag_name == "version":
                try:
                    version = int(entry.text)
                except Exception as e:
                    raise ValueError("Invalid version string '%s': %s" % (entry.text, e))
                break
        if version is None:
            raise RuntimeError("Missing version in metadata")

        # get setting version
        if "version" in data.attrib:
            setting_version = self._xmlVersionToSettingVersion(data.attrib["version"])
        else:
            setting_version = self._xmlVersionToSettingVersion("1.2")

        if version is None:
            raise RuntimeError("Missing version in metadata")

        return version * 1000000 + setting_version

    def _xmlVersionToSettingVersion(self, xml_version: str) -> int:
        if xml_version == "1.3":
            return 1
        return 0 #Older than 1.3.

    def upgradeMaterial(self, serialised, filename):
        data = ET.fromstring(serialised)

        # update version
        metadata = data.iterfind("./um:metadata/*", {"um": "http://www.ultimaker.com/material"})
        for entry in metadata:
            if _tag_without_namespace(entry) == "version":
                entry.text = "2"
                break

        data.attrib["version"] = "1.3"

        # this makes sure that the XML header states encoding="utf-8"
        new_serialised = ET.tostring(data, encoding="utf-8").decode("utf-8")

        return [filename], [new_serialised]


def _tag_without_namespace(element):
    return element.tag[element.tag.rfind("}") + 1:]
