// Copyright (c) 2022 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.3
import QtQuick.Controls 2.15
import UM 1.5 as UM
import Cura 1.6 as Cura

/**
 * A MonitorInfoBlurb is an extension of the GenericPopUp used to show static information (vs. interactive context
 * menus). It accepts some text (text), an item to link to to (target), and a specification of which side of the target
 * to appear on (direction). It also sets the GenericPopUp's color to black, to differentiate itself from a menu.
 */
Item
{
    property alias target: popUp.target

    property var printJob: null

    GenericPopUp
    {
        id: popUp

        // Which way should the pop-up point? Default is up, but will flip when required
        direction: "up"

        // Use dark grey for info blurbs and white for context menus
        color: UM.Theme.getColor("monitor_context_menu")

        contentItem: Item
        {
            id: contentWrapper
            implicitWidth: childrenRect.width
            implicitHeight: menuItems.height + UM.Theme.getSize("default_margin").height

            Column
            {
                id: menuItems
                width: 144 * screenScaleFactor

                anchors
                {
                    top: parent.top
                    topMargin: Math.floor(UM.Theme.getSize("default_margin").height / 2)
                }

                spacing: Math.floor(UM.Theme.getSize("default_margin").height / 2)

                PrintJobContextMenuItem {
                    onClicked: {
                        sendToTopConfirmationDialog.visible = true;
                        popUp.close();
                    }
                    text: catalog.i18nc("@label", "Move to top");
                    visible: {
                        if (printJob && (printJob.state == "queued" || printJob.state == "error") && !isAssigned(printJob)) {
                            if (OutputDevice && OutputDevice.queuedPrintJobs[0]) {
                                return OutputDevice.queuedPrintJobs[0].key != printJob.key;
                            }
                        }
                        return false;
                    }
                }

                PrintJobContextMenuItem {
                    onClicked: {
                        deleteConfirmationDialog.visible = true;
                        popUp.close();
                    }
                    text: catalog.i18nc("@label", "Delete");
                    visible: {
                        if (!printJob) {
                            return false;
                        }
                        var states = ["queued", "error", "sent_to_printer"];
                        return states.indexOf(printJob.state) !== -1;
                    }
                }

                PrintJobContextMenuItem {
                    enabled: visible && !(printJob.state == "pausing" || printJob.state == "resuming");
                    onClicked: {
                        if (printJob.state == "paused") {
                            printJob.setState("resume");
                            popUp.close();
                            return;
                        }
                        if (printJob.state == "printing") {
                            printJob.setState("pause");
                            popUp.close();
                            return;
                        }
                    }
                    text: {
                        if (!printJob) {
                            return "";
                        }
                        switch(printJob.state) {
                            case "paused":
                                return catalog.i18nc("@label", "Resume");
                            case "pausing":
                                return catalog.i18nc("@label", "Pausing...");
                            case "resuming":
                                return catalog.i18nc("@label", "Resuming...");
                            default:
                                catalog.i18nc("@label", "Pause");
                        }
                    }
                    visible: {
                        if (!printJob) {
                            return false;
                        }
                        var states = ["printing", "pausing", "paused", "resuming"];
                        return states.indexOf(printJob.state) !== -1;
                    }
                }

                PrintJobContextMenuItem {
                    enabled: visible && printJob.state !== "aborting";
                    onClicked: {
                        abortConfirmationDialog.visible = true;
                        popUp.close();
                    }
                    text: printJob && printJob.state == "aborting" ? catalog.i18nc("@label", "Aborting...") : catalog.i18nc("@label", "Abort");
                    visible: {
                        if (!printJob) {
                            return false;
                        }
                        var states = ["pre_print", "printing", "pausing", "paused", "resuming"];
                        return states.indexOf(printJob.state) !== -1;
                    }
                }
            }
        }
    }

    Cura.MessageDialog
    {
        id: sendToTopConfirmationDialog
        onAccepted: OutputDevice.sendJobToTop(printJob.key)
        standardButtons: Dialog.Yes | Dialog.No
        text: printJob && printJob.name ? catalog.i18nc("@label %1 is the name of a print job.", "Are you sure you want to move %1 to the top of the queue?").arg(printJob.name) : ""
        title: catalog.i18nc("@window:title", "Move print job to top")
    }

    Cura.MessageDialog
    {
        id: deleteConfirmationDialog
        onAccepted: OutputDevice.deleteJobFromQueue(printJob.key)
        standardButtons: Dialog.Yes | Dialog.No
        text: printJob && printJob.name ? catalog.i18nc("@label %1 is the name of a print job.", "Are you sure you want to delete %1?").arg(printJob.name) : ""
        title: catalog.i18nc("@window:title", "Delete print job")
    }

    Cura.MessageDialog
    {
        id: abortConfirmationDialog
        onAccepted: printJob.setState("abort")
        standardButtons: Dialog.Yes | Dialog.No
        text: printJob && printJob.name ? catalog.i18nc("@label %1 is the name of a print job.", "Are you sure you want to abort %1?").arg(printJob.name) : ""
        title: catalog.i18nc("@window:title", "Abort print")
    }

    function switchPopupState() {
        popUp.visible ? popUp.close() : popUp.open()
    }
    function open() {
        popUp.open()
    }
    function close() {
        popUp.close()
    }
    function isAssigned(job) {
        if (!job) {
            return false;
        }
        return job.assignedPrinter ? true : false;
    }
}
