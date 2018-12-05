// Copyright (c) 2018 Ultimaker B.V.
// Cura is released under the terms of the LGPLv3 or higher.

import QtQuick 2.7
import QtQuick.Controls 2.3

import UM 1.2 as UM
import Cura 1.0 as Cura

Cura.ExpandableComponent
{
    id: viewSelector

    popupPadding: UM.Theme.getSize("default_lining").width
    popupAlignment: Cura.ExpandableComponent.PopupAlignment.AlignLeft
    iconSource: expanded ? UM.Theme.getIcon("arrow_bottom") : UM.Theme.getIcon("arrow_left")

    property var viewModel: UM.ViewModel { }

    property var activeView:
    {
        for (var i = 0; i < viewModel.count; i++)
        {
            if (viewModel.items[i].active)
            {
                return viewModel.items[i]
            }
        }
        return null
    }

    Component.onCompleted:
    {
        // Nothing was active, so just return the first one (the list is sorted by priority, so the most
        // important one should be returned)
        if (activeView == null)
        {
            UM.Controller.setActiveView(viewModel.getItem(0).id)
        }
    }

    headerItem: Item
    {
        Label
        {
            id: title
            text: catalog.i18nc("@button", "View types")
            verticalAlignment: Text.AlignVCenter
            height: parent.height
            elide: Text.ElideRight
            font: UM.Theme.getFont("default")
            color: UM.Theme.getColor("text_medium")
            renderType: Text.NativeRendering
        }

        Label
        {
            text: viewSelector.activeView ? viewSelector.activeView.name : ""
            verticalAlignment: Text.AlignVCenter
            anchors
            {
                left: title.right
                leftMargin: UM.Theme.getSize("default_margin").width
            }
            height: parent.height
            elide: Text.ElideRight
            font: UM.Theme.getFont("default")
            color: UM.Theme.getColor("text")
            renderType: Text.NativeRendering
        }
    }

    popupItem: Column
    {
        id: viewSelectorPopup
        width: viewSelector.width - 2 * viewSelector.popupPadding

        // For some reason the height/width of the column gets set to 0 if this is not set...
        Component.onCompleted:
        {
            height = implicitHeight
            width = viewSelector.width - 2 * viewSelector.popupPadding
        }

        Repeater
        {
            id: viewsList
            model: viewSelector.viewModel

            delegate: Button
            {
                id: viewsSelectorButton
                text: model.name
                width: parent.width
                height: UM.Theme.getSize("action_button").height
                leftPadding: UM.Theme.getSize("default_margin").width
                rightPadding: UM.Theme.getSize("default_margin").width
                checkable: true
                checked: viewSelector.activeView != null ? viewSelector.activeView.id == id : false

                contentItem: Label
                {
                    id: buttonText
                    text: viewsSelectorButton.text
                    color: UM.Theme.getColor("text")
                    font: UM.Theme.getFont("action_button")
                    renderType: Text.NativeRendering
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }

                background: Rectangle
                {
                    id: backgroundRect
                    color: viewsSelectorButton.hovered ? UM.Theme.getColor("action_button_hovered") : "transparent"
                    radius: UM.Theme.getSize("action_button_radius").width
                    border.width: UM.Theme.getSize("default_lining").width
                    border.color: viewsSelectorButton.checked ? UM.Theme.getColor("primary") : "transparent"
                }

                onClicked:
                {
                    viewSelector.togglePopup()
                    UM.Controller.setActiveView(id)
                }
            }
        }
    }
}