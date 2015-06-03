// Copyright (c) 2015 Ultimaker B.V.
// Cura is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1

import UM 1.0 as UM

Button {
    id: base;

    property Action saveAction;

    property real progress: UM.Backend.progress;
    Behavior on progress { NumberAnimation { duration: 250; } }

    enabled: progress >= 0.95;

    property string currentDevice: "local_file"
    property bool defaultOverride: false;
    property bool defaultAmbiguous: false;

    property variant printDuration: PrintInformation.currentPrintTime;
    property real printMaterialAmount: PrintInformation.materialAmount;

    iconSource: UM.Theme.icons[Printer.outputDevices[base.currentDevice].icon];
    tooltip: Printer.outputDevices[base.currentDevice].description;

    Connections {
        target: Printer;
        onOutputDevicesChanged: {
            if(!base.defaultOverride) {
                base.defaultAmbiguous = false;
                var device = null;
                for(var i in Printer.outputDevices) {
                    if(device == null) {
                        device = i;
                    } else if(Printer.outputDevices[i].priority > Printer.outputDevices[device].priority) {
                        device = i;
                    } else if(Printer.outputDevices[i].priority == Printer.outputDevices[device].priority) {
                        base.defaultAmbiguous = true;
                    }
                }

                if(device != null) {
                    base.currentDevice = device;
                }
            }
        }
    }

    style: ButtonStyle {
        background: UM.AngledCornerRectangle {
            implicitWidth: control.width;
            implicitHeight: control.height;

            color: UM.Theme.colors.save_button_border;
            cornerSize: UM.Theme.sizes.default_margin.width;

            UM.AngledCornerRectangle {
                anchors.fill: parent;
                anchors.margins: UM.Theme.sizes.save_button_border.width;
                cornerSize: UM.Theme.sizes.default_margin.width;
                color: UM.Theme.colors.save_button;
            }

            UM.AngledCornerRectangle {
                anchors {
                    left: parent.left;
                    top: parent.top;
                    bottom: parent.bottom;
                }

                width: Math.max(parent.height + (parent.width - parent.height) * control.progress, parent.height);
                cornerSize: UM.Theme.sizes.default_margin.width;

                color: !control.enabled ? UM.Theme.colors.save_button_inactive : control.hovered ? UM.Theme.colors.save_button_active_hover : UM.Theme.colors.save_button_active;
                Behavior on color { ColorAnimation { duration: 50; } }
            }

            UM.AngledCornerRectangle {
                anchors.left: parent.left;
                width: parent.height + UM.Theme.sizes.save_button_border.width;
                height: parent.height;
                cornerSize: UM.Theme.sizes.default_margin.width;
                color: UM.Theme.colors.save_button;
            }

            UM.AngledCornerRectangle {
                anchors.left: parent.left;
                width: parent.height + UM.Theme.sizes.save_button_border.width;
                height: parent.height;
                cornerSize: UM.Theme.sizes.default_margin.width;

                color: UM.Theme.colors.save_button;
            }

            UM.AngledCornerRectangle {
                id: icon;

                anchors.left: parent.left;
                width: parent.height;
                height: parent.height;
                cornerSize: UM.Theme.sizes.default_margin.width;
                color: !control.enabled ? UM.Theme.colors.save_button_inactive : control.hovered ? UM.Theme.colors.save_button_active_hover : UM.Theme.colors.save_button_active;
                Behavior on color { ColorAnimation { duration: 50; } }

                Image {
                    anchors.centerIn: parent;

                    width: UM.Theme.sizes.button_icon.width;
                    height: UM.Theme.sizes.button_icon.height;

                    sourceSize.width: width;
                    sourceSize.height: height;

                    source: control.iconSource;
                }
            }
        }

        label: Column {
            Label {
                id: label;
                anchors.left: parent.left;
                anchors.leftMargin: control.height + UM.Theme.sizes.save_button_label_margin.width;

                color: UM.Theme.colors.save_button_text;
                font: UM.Theme.fonts.default;

                text: control.text;
            }
            Label {
                anchors.left: parent.left;
                anchors.leftMargin: control.height + UM.Theme.sizes.save_button_label_margin.width;

                color: UM.Theme.colors.save_button_text;
                font: UM.Theme.fonts.default;

                text: (!control.printDuration || !control.printDuration.valid) ? "" : control.printDuration.getDisplayString(UM.DurationFormat.Long)
            }
            Label {
                anchors.left: parent.left;
                anchors.leftMargin: control.height + UM.Theme.sizes.save_button_label_margin.width;

                color: UM.Theme.colors.save_button_text;
                font: UM.Theme.fonts.default;

                //: Print material amount save button label
                text: control.printMaterialAmount < 0 ? "" : qsTr("%1m of material").arg(control.printMaterialAmount);
            }
        }
    }

    MouseArea {
        anchors.fill: parent;

        acceptedButtons: Qt.RightButton;

        onClicked: devicesMenu.popup();
    }

    Menu {
        id: devicesMenu;

        Instantiator {
            model: Printer.outputDeviceNames;
            MenuItem {
                text: Printer.outputDevices[modelData].description;
                checkable: true;
                checked: base.defaultAmbiguous ? false : modelData == base.currentDevice;
                exclusiveGroup: devicesMenuGroup;
                onTriggered: {
                    base.defaultOverride = true;
                    base.currentDevice = modelData;
                    if(base.defaultAmbiguous) {
                        base.defaultAmbiguous = false;
                        Printer.writeToOutputDevice(modelData);
                    }
                }
            }
            onObjectAdded: devicesMenu.insertItem(index, object)
            onObjectRemoved: devicesMenu.removeItem(object)
        }

        ExclusiveGroup { id: devicesMenuGroup; }
    }

    text: {
        if(base.progress < 0) {
            //: Save button label
            return qsTr("Please load a 3D model");
        } else if (base.progress < 0.95) {
            //: Save button label
            return qsTr("Calculating Print-time");
        } else {
            //: Save button label
            return qsTr("Estimated Print-time");
        }
    }

    onClicked: {
        if(base.defaultAmbiguous) {
            devicesMenu.popup();
        } else {
            Printer.writeToOutputDevice(base.currentDevice);
        }
    }
}
