// Copyright (c) 2016 Ultimaker B.V.
// Cura is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1

import UM 1.1 as UM
import Cura 1.0 as Cura

Rectangle
{
    id: base;
    UM.I18nCatalog { id: catalog; name:"cura"}

    property bool printerConnected: Cura.MachineManager.printerOutputDevices.length != 0
    property bool printerAcceptsCommands: printerConnected && Cura.MachineManager.printerOutputDevices[0].acceptsCommands
    property real progress: printerConnected ? Cura.MachineManager.printerOutputDevices[0].progress : 0
    property int backendState: UM.Backend.state

    property variant statusColor:
    {
        if(!printerConnected || !printerAcceptsCommands)
            return UM.Theme.getColor("text");

        switch(Cura.MachineManager.printerOutputDevices[0].jobState)
        {
            case "printing":
            case "pre_print":
            case "wait_cleanup":
                return UM.Theme.getColor("status_busy");
            case "ready":
            case "":
                return UM.Theme.getColor("status_ready");
            case "paused":
                return UM.Theme.getColor("status_paused");
            case "error":
                return UM.Theme.getColor("status_stopped");
            case "offline":
                return UM.Theme.getColor("status_offline");
            default:
                return UM.Theme.getColor("text");
        }
    }

    property bool activity: Printer.getPlatformActivity;
    property int totalHeight: childrenRect.height + UM.Theme.getSize("default_margin").height
    property string fileBaseName
    property string statusText:
    {
        if(!printerConnected)
            return catalog.i18nc("@label:MonitorStatus", "Not connected to a printer");
        if(!printerAcceptsCommands)
            return catalog.i18nc("@label:MonitorStatus", "Printer does not accept commands");

        var printerOutputDevice = Cura.MachineManager.printerOutputDevices[0]
        switch(printerOutputDevice.jobState)
        {
            case "offline":
                return catalog.i18nc("@label:MonitorStatus", "Lost connection with the printer");
            case "printing":
                return catalog.i18nc("@label:MonitorStatus", "Printing...");
            case "paused":
                return catalog.i18nc("@label:MonitorStatus", "Paused");
            case "pre_print":
                return catalog.i18nc("@label:MonitorStatus", "Preparing...");
            case "wait_cleanup":
                return catalog.i18nc("@label:MonitorStatus", "Please remove the print");
            case "error":
                return printerOutputDevice.errorText;
            default:
                return " ";
        }
    }

    Label
    {
        id: statusLabel
        width: parent.width - 2 * UM.Theme.getSize("default_margin").width
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.leftMargin: UM.Theme.getSize("default_margin").width

        color: base.statusColor
        font: UM.Theme.getFont("large")
        text: statusText
    }

    Label
    {
        id: percentageLabel
        anchors.top: parent.top
        anchors.right: progressBar.right

        color: base.statusColor
        font: UM.Theme.getFont("large")
        text: Math.round(progress) + "%"
        visible: printerConnected
    }

    Rectangle
    {
        id: progressBar
        width: parent.width - 2 * UM.Theme.getSize("default_margin").width
        height: UM.Theme.getSize("progressbar").height
        anchors.top: statusLabel.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").height / 4
        anchors.left: parent.left
        anchors.leftMargin: UM.Theme.getSize("default_margin").width
        radius: UM.Theme.getSize("progressbar_radius").width
        color: UM.Theme.getColor("progressbar_background")

        Rectangle
        {
            width: Math.max(parent.width * base.progress / 100)
            height: parent.height
            color: base.statusColor
            radius: UM.Theme.getSize("progressbar_radius").width
        }
    }

    Button
    {
        id: abortButton

        visible: printerConnected
        enabled: printerConnected && Cura.MachineManager.printerOutputDevices[0].acceptsCommands &&
                 (Cura.MachineManager.printerOutputDevices[0].jobState == "paused" || Cura.MachineManager.printerOutputDevices[0].jobState == "printing")

        height: UM.Theme.getSize("save_button_save_to_button").height
        anchors.top: progressBar.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").height
        anchors.right: parent.right
        anchors.rightMargin: UM.Theme.getSize("default_margin").width

        text: catalog.i18nc("@label:", "Abort Print")
        onClicked: Cura.MachineManager.printerOutputDevices[0].setJobState("abort")


        style: ButtonStyle
        {
            background: Rectangle
            {
                border.width: UM.Theme.getSize("default_lining").width
                border.color:
                {
                    if(!control.enabled)
                        return UM.Theme.getColor("action_button_disabled_border");
                    else if(control.pressed)
                        return UM.Theme.getColor("action_button_active_border");
                    else if(control.hovered)
                        return UM.Theme.getColor("action_button_hovered_border");
                    else
                        return UM.Theme.getColor("action_button_border");
                }
                color:
                {
                    if(!control.enabled)
                        return UM.Theme.getColor("action_button_disabled");
                    else if(control.pressed)
                        return UM.Theme.getColor("action_button_active");
                    else if(control.hovered)
                        return UM.Theme.getColor("action_button_hovered");
                    else
                        return UM.Theme.getColor("action_button");
                }
                Behavior on color { ColorAnimation { duration: 50; } }

                implicitWidth: actualLabel.contentWidth + (UM.Theme.getSize("default_margin").width * 2)

                Label
                {
                    id: actualLabel
                    anchors.centerIn: parent
                    color:
                    {
                        if(!control.enabled)
                            return UM.Theme.getColor("action_button_disabled_text");
                        else if(control.pressed)
                            return UM.Theme.getColor("action_button_active_text");
                        else if(control.hovered)
                            return UM.Theme.getColor("action_button_hovered_text");
                        else
                            return UM.Theme.getColor("action_button_text");
                    }
                    font: UM.Theme.getFont("action_button")
                    text: control.text;
                }
            }
        label: Item { }
        }
    }

    Button
    {
        id: pauseResumeButton

        height: UM.Theme.getSize("save_button_save_to_button").height
        anchors.top: progressBar.bottom
        anchors.topMargin: UM.Theme.getSize("default_margin").height
        anchors.right: abortButton.left
        anchors.rightMargin: UM.Theme.getSize("default_margin").width

        visible: printerConnected
        enabled: printerConnected && Cura.MachineManager.printerOutputDevices[0].acceptsCommands &&
                 (Cura.MachineManager.printerOutputDevices[0].jobState == "paused" || Cura.MachineManager.printerOutputDevices[0].jobState == "printing")

        text: printerConnected ? Cura.MachineManager.printerOutputDevices[0].jobState == "paused" ? catalog.i18nc("@label:", "Resume") : catalog.i18nc("@label:", "Pause") : ""
        onClicked: Cura.MachineManager.printerOutputDevices[0].setJobState(Cura.MachineManager.printerOutputDevices[0].jobState == "paused" ? "print" : "pause")

        style: ButtonStyle
        {
            background: Rectangle
            {
                border.width: UM.Theme.getSize("default_lining").width
                border.color:
                {
                    if(!control.enabled)
                        return UM.Theme.getColor("action_button_disabled_border");
                    else if(control.pressed)
                        return UM.Theme.getColor("action_button_active_border");
                    else if(control.hovered)
                        return UM.Theme.getColor("action_button_hovered_border");
                    else
                        return UM.Theme.getColor("action_button_border");
                }
                color:
                {
                    if(!control.enabled)
                        return UM.Theme.getColor("action_button_disabled");
                    else if(control.pressed)
                        return UM.Theme.getColor("action_button_active");
                    else if(control.hovered)
                        return UM.Theme.getColor("action_button_hovered");
                    else
                        return UM.Theme.getColor("action_button");
                }
                Behavior on color { ColorAnimation { duration: 50; } }

                implicitWidth: actualLabel.contentWidth + (UM.Theme.getSize("default_margin").width * 2)

                Label
                {
                    id: actualLabel
                    anchors.centerIn: parent
                    color:
                    {
                        if(!control.enabled)
                            return UM.Theme.getColor("action_button_disabled_text");
                        else if(control.pressed)
                            return UM.Theme.getColor("action_button_active_text");
                        else if(control.hovered)
                            return UM.Theme.getColor("action_button_hovered_text");
                        else
                            return UM.Theme.getColor("action_button_text");
                    }
                    font: UM.Theme.getFont("action_button")
                    text: control.text
                }
            }
        label: Item { }
        }
    }
}
