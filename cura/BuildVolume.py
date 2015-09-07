# Copyright (c) 2015 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

from UM.View.Renderer import Renderer
from UM.Scene.SceneNode import SceneNode
from UM.Application import Application
from UM.Resources import Resources
from UM.Mesh.MeshData import MeshData
from UM.Mesh.MeshBuilder import MeshBuilder
from UM.Math.Vector import Vector
from UM.Math.Color import Color
from UM.Math.AxisAlignedBox import AxisAlignedBox
from UM.Math.Polygon import Polygon

import numpy

class BuildVolume(SceneNode):
    VolumeOutlineColor = Color(12, 169, 227, 255)

    def __init__(self, parent = None):
        super().__init__(parent)

        self._width = 0
        self._height = 0
        self._depth = 0

        self._material = None

        self._grid_mesh = None
        self._grid_material = None

        self._disallowed_areas = []
        self._disallowed_area_mesh = None

        self.setCalculateBoundingBox(False)

        self._active_instance = None
        Application.getInstance().getMachineManager().activeMachineInstanceChanged.connect(self._onActiveInstanceChanged)
        self._onActiveInstanceChanged()

    def setWidth(self, width):
        if width: self._width = width

    def setHeight(self, height):
        if height: self._height = height

    def setDepth(self, depth):
        if depth: self._depth = depth

    def getDisallowedAreas(self):
        return self._disallowed_areas

    def setDisallowedAreas(self, areas):
        self._disallowed_areas = areas

    def render(self, renderer):
        if not self.getMeshData():
            return True

        if not self._material:
            self._material = renderer.createMaterial(
                Resources.getPath(Resources.Shaders, "basic.vert"),
                Resources.getPath(Resources.Shaders, "vertexcolor.frag")
            )
            self._grid_material = renderer.createMaterial(
                Resources.getPath(Resources.Shaders, "basic.vert"),
                Resources.getPath(Resources.Shaders, "grid.frag")
            )
            self._grid_material.setUniformValue("u_gridColor0", Color(245, 245, 245, 255))
            self._grid_material.setUniformValue("u_gridColor1", Color(205, 202, 201, 255))

        renderer.queueNode(self, material = self._material, mode = Renderer.RenderLines)
        renderer.queueNode(self, mesh = self._grid_mesh, material = self._grid_material, force_single_sided = True)
        if self._disallowed_area_mesh:
            renderer.queueNode(self, mesh = self._disallowed_area_mesh, material = self._material)
        return True

    def rebuild(self):
        if self._width == 0 or self._height == 0 or self._depth == 0:
            return

        minW = -self._width / 2
        maxW = self._width / 2
        minH = 0.0
        maxH = self._height
        minD = -self._depth / 2
        maxD = self._depth / 2

        mb = MeshBuilder()

        mb.addLine(Vector(minW, minH, minD), Vector(maxW, minH, minD), color = self.VolumeOutlineColor)
        mb.addLine(Vector(minW, minH, minD), Vector(minW, maxH, minD), color = self.VolumeOutlineColor)
        mb.addLine(Vector(minW, maxH, minD), Vector(maxW, maxH, minD), color = self.VolumeOutlineColor)
        mb.addLine(Vector(maxW, minH, minD), Vector(maxW, maxH, minD), color = self.VolumeOutlineColor)

        mb.addLine(Vector(minW, minH, maxD), Vector(maxW, minH, maxD), color = self.VolumeOutlineColor)
        mb.addLine(Vector(minW, minH, maxD), Vector(minW, maxH, maxD), color = self.VolumeOutlineColor)
        mb.addLine(Vector(minW, maxH, maxD), Vector(maxW, maxH, maxD), color = self.VolumeOutlineColor)
        mb.addLine(Vector(maxW, minH, maxD), Vector(maxW, maxH, maxD), color = self.VolumeOutlineColor)

        mb.addLine(Vector(minW, minH, minD), Vector(minW, minH, maxD), color = self.VolumeOutlineColor)
        mb.addLine(Vector(maxW, minH, minD), Vector(maxW, minH, maxD), color = self.VolumeOutlineColor)
        mb.addLine(Vector(minW, maxH, minD), Vector(minW, maxH, maxD), color = self.VolumeOutlineColor)
        mb.addLine(Vector(maxW, maxH, minD), Vector(maxW, maxH, maxD), color = self.VolumeOutlineColor)

        self.setMeshData(mb.getData())

        mb = MeshBuilder()
        mb.addQuad(
            Vector(minW, minH, minD),
            Vector(maxW, minH, minD),
            Vector(maxW, minH, maxD),
            Vector(minW, minH, maxD)
        )
        self._grid_mesh = mb.getData()
        for n in range(0, 6):
            v = self._grid_mesh.getVertex(n)
            self._grid_mesh.setVertexUVCoordinates(n, v[0], v[2])

        disallowed_area_size = 0
        if self._disallowed_areas:
            mb = MeshBuilder()
            for polygon in self._disallowed_areas:
                points = polygon.getPoints()
                mb.addQuad(
                    Vector(points[0, 0], 0.1, points[0, 1]),
                    Vector(points[1, 0], 0.1, points[1, 1]),
                    Vector(points[2, 0], 0.1, points[2, 1]),
                    Vector(points[3, 0], 0.1, points[3, 1]),
                    color = Color(174, 174, 174, 255)
                )
                # Find the largest disallowed area to exclude it from the maximum scale bounds
                size = abs(numpy.max(points[:, 1]) - numpy.min(points[:, 1]))
                disallowed_area_size = max(size, disallowed_area_size)

            self._disallowed_area_mesh = mb.getData()
        else:
            self._disallowed_area_mesh = None

        self._aabb = AxisAlignedBox(minimum = Vector(minW, minH - 1.0, minD), maximum = Vector(maxW, maxH, maxD))

        skirt_size = 0.0

        #profile = Application.getInstance().getMachineManager().getActiveProfile()
        #if profile:
            #if profile.getSettingValue("adhesion_type") == "skirt":
                #skirt_size = profile.getSettingValue("skirt_line_count") * profile.getSettingValue("skirt_line_width") + profile.getSettingValue("skirt_gap")
            #elif profile.getSettingValue("adhesion_type") == "brim":
                #skirt_size = profile.getSettingValue("brim_line_count") * profile.getSettingValue("skirt_line_width")
            #else:
                #skirt_size = profile.getSettingValue("skirt_line_width")

            #skirt_size += profile.getSettingValue("skirt_line_width")

        scale_to_max_bounds = AxisAlignedBox(
            minimum = Vector(minW + skirt_size, minH, minD + skirt_size + disallowed_area_size),
            maximum = Vector(maxW - skirt_size, maxH, maxD - skirt_size - disallowed_area_size)
        )

        Application.getInstance().getController().getScene()._maximum_bounds = scale_to_max_bounds

    def _onActiveInstanceChanged(self):
        self._active_instance = Application.getInstance().getMachineManager().getActiveMachineInstance()

        if self._active_instance:
            self._width = self._active_instance.getMachineSettingValue("machine_width")
            self._height = self._active_instance.getMachineSettingValue("machine_height")
            self._depth = self._active_instance.getMachineSettingValue("machine_depth")

            disallowed_areas = self._active_instance.getMachineSettingValue("machine_disallowed_areas")
            areas = []
            if disallowed_areas:
                for area in disallowed_areas:
                    areas.append(Polygon(numpy.array(area, numpy.float32)))

            self._disallowed_areas = areas

            self.rebuild()
