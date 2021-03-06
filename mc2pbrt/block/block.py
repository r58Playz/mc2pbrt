from resource import ResourceManager
from material import Matte

from util import pt_map
from tuple_calculation import plus, mult, minus 

class BlockBase:
    SOLID_BLOCK = set([
        "stone", "podzol", "clay",
    ])
    SOLID_TYPE = [
        "ore", "granite", "diorite", "andesite", "planks", "dirt", "block",
        "wood"
    ]
    LONG_PLANT = set(["tall_seagrass", "sunflower", "lilac", "rose_bush",
                      "peony", "tall_grass", "large_fern"])

    NORMAL_LIGHT_MAP = {
        "beacon" : 15,
        "end_portal" : 15,
        "fire" : 15,
        "glowstone" : 15,
        "jack_o_lantern" : 15,
        "lava" : 15,
        "sea_lantern" : 15,
        "conduit" : 15,
        "end_rod" : 14,
        "torch" : 14*8,
        "wall_torch" : 14*8,
        "nether_portal" : 11,
        "ender_chest" : 7,
        "magma_block" : 3,
        "brewing_stand" : 1,
        "brown_mushroom" : 1,
        "dragon_egg" : 1,
        "end_portal_frame" : 1,
    }

    # Sea pickle's light
    def sea_pickle(b):
        if b.state["waterlogged"] == "false":
            return 0
        return [0, 6, 9, 12, 15][int(b.state["pickles"])]

    # Return a lambda that just determine whether the block's "lit" is on
    lit = lambda l: (lambda b: [0, l][b.state["lit"] == "true"])

    CONDITION_LIGHT_MAP = {
        "sea_pickle" : sea_pickle,
        "furnace" : lit(13),
        "redstone_ore" : lit(9),
        "redstone_lamp" : lit(15),
        "redstone_torch" : lit(7),
    }
    
    def __init__(self, name, state, biome_id):
        self.name = name
        self.state = state
        self.biome_id = biome_id

        # [(Model, Transform)]
        self.models = []

        # Default Material
        self.material = Matte(self) 
        self.type = ""

        self.build()

    def _is(self, y):
        return self.name == y or self.name[-len(y)-1:] == "_" + y

    def getLight(self):
        if self.name in BlockBase.NORMAL_LIGHT_MAP:
            return BlockBase.NORMAL_LIGHT_MAP[self.name]

        if self.name in BlockBase.CONDITION_LIGHT_MAP:
            return BlockBase.CONDITION_LIGHT_MAP[self.name](self)

        return 0

    def canPass(self):
        if self.name in BlockBase.SOLID_BLOCK:
            return False
        for t in BlockBase.SOLID_TYPE:
            if self._is(t):
                return False
        return True

    def empty(self):
        return not self.models

    def _getModel(self, name):
        model, par = ResourceManager().model_loader.getModel("block/" + name)
        if "elements" not in model:
            return None, None
        return model, par

    def addModel(self, name, _transforms=None, _material = None):
        mdl, par = self._getModel(name)
        if not mdl:
            return
        transforms = _transforms or []
        material = _material or self.material
        self.models.append((mdl, transforms, material))
        self.type = par[6:]

    def build(self):
        raise NotImplementedError("BlockBase._build")

    def _writeElement(self, fout, ele, material):
        from_pt = ele["from"]
        to_pt = ele["to"]
        cube = minus(to_pt, from_pt)
        mid = mult(plus(from_pt, to_pt), .5)

        fout.write('AttributeBegin\n')
        fout.write('Translate %f %f %f\n' % mid)
        if "rotation" in ele:
            import math
            rot = ele["rotation"]
            axis = rot["axis"]
            org = minus(mid, mult(rot["origin"], 1./16))
            ang = rot["angle"]
            rxyz = {"x" : (1, 0, 0), "y" : (0, 1, 0), "z" : (0, 0, 1)}
            sxyz = {"x" : (0, 1, 1), "y" : (1, 0, 1), "z" : (1, 1, 0)}
            fout.write("Translate %f %f %f\n" % mult(org, -1))
            fout.write(("Rotate %f " % ang) + ("%d %d %d\n" % rxyz[axis]))
            if "rescale" in rot and rot["rescale"]:
                scale = 1/math.cos(ang/180.*math.pi)
                fout.write("Scale %f %f %f\n" % plus(mult(sxyz[axis], scale), rxyz[axis]))
            fout.write("Translate %f %f %f\n" % org)

        for facename in ele["faces"]:
            face = ele["faces"][facename]
            tex = face["texture"]
            uv = face["uv"]
            delta_f, l_f, dir_, shape = pt_map[facename]
            delta = delta_f(cube)
            l1, l2 = l_f(cube)
            fout.write('AttributeBegin\n')

            if "rotation" in face:
                rxyz = {"x" : (1, 0, 0), "y" : (0, 1, 0), "z" : (0, 0, 1)}
                # shape[-1] should be "x", "y" or "z"
                fout.write(("Rotate %f " % (face["rotation"]*dir_)) + ("%d %d %d\n" % rxyz[shape[-1]]))

            if material:
                material.write(fout, face)

            fout.write('  Translate %f %f %f\n' % delta)
            if ResourceManager().hasAlpha(tex + ".png"):
                fout.write('  Shape "%s" "float l1" [%f] "float l2" [%f] ' % (shape, l1, l2) +
                           '  "float dir" [%d] "texture alpha" "%s-alpha"' % (dir_, tex) +
                           '  "float u0" [%f] "float v0" [%f] "float u1" [%f] "float v1" [%f]\n' % uv)
            else:
                fout.write('  Shape "%s" "float l1" [%f] "float l2" [%f] ' % (shape, l1, l2) +
                           '  "float dir" [%d] ' % (dir_, ) +
                           '  "float u0" [%f] "float v0" [%f] "float u1" [%f] "float v1" [%f]\n' % uv)
            fout.write('AttributeEnd\n')

        fout.write('AttributeEnd\n')

    def _writeRotate(self, fout, axis, ang):
        org = (.5, .5, .5)
        fout.write("Translate %f %f %f\n" % org)
        rxyz = {"x" : (1, 0, 0), "y" : (0, 1, 0), "z" : (0, 0, 1)}
        fout.write(("Rotate %f " % ang) + ("%d %d %d\n" % rxyz[axis]))
        fout.write("Translate %f %f %f\n" % mult(org, -1))

    def _writeScale(self, fout, axis, s):
        org = (.5, .5, .5)
        fout.write("Translate %f %f %f\n" % org)
        axis_v = {"x" : (1, 0, 0), "y" : (0, 1, 0), "z" : (0, 0, 1)}
        sixa_v = {"x" : (0, 1, 1), "y" : (1, 0, 1), "z" : (1, 1, 0)}
        fout.write(("Scale %f %f %f\n" % plus(mult(axis_v[axis], s), sixa_v[axis])))
        fout.write("Translate %f %f %f\n" % mult(org, -1))

    def write(self, fout):
        """Write file with pbrt format
        
        Args:
            fout: file object
        Returns:
            Number of render block(0 or 1)
        """

        if self.empty():
            return 0

        fout.write('AttributeBegin\n')
        if "axis" in self.state and self.name != "nether_portal":
            axis = self.state["axis"]
            if axis == "x":
                self._writeRotate(fout, "z", 90)
            elif axis == "z":
                self._writeRotate(fout, "x", 90)

        if "facing" in self.state:
            facing = self.state["facing"]
            if self.type == "orientable":
                mp = {"north" : 0, "east" : 1, "south" : 2, "west" : 3}
            elif self.type == "template_piston":
                mp = {"north" : 2, "east" : 3, "south" : 0, "west" : 1}
            else:
                mp = {"north" : 1, "east" : 0, "south" : 3, "west" : 2}

            if facing in mp:
                self._writeRotate(fout, "y", mp[facing]*90)
            elif facing == "down":
                self._writeRotate(fout, "z", -90)
            elif facing == "top":
                self._writeRotate(fout, "z", 90)
        
        for model, transforms, material in self.models:
            for t in transforms:
                if t["type"] == "rotate":
                    self._writeRotate(fout, t["axis"], t["angle"])
                elif t["type"] == "scale":
                    self._writeScale(fout, t["axis"], t["value"])
            for ele in model["elements"]:
                self._writeElement(fout, ele, material)
            for t in transforms[::-1]:
                if t["type"] == "rotate":
                    self._writeRotate(fout, t["axis"], -t["angle"])
                elif t["type"] == "scale":
                    self._writeScale(fout, t["axis"], 1/t["value"])
        fout.write('AttributeEnd\n')
        return 1

    def getUsedTexture(self):
        used_texture = set()
        for model, transform, material in self.models:
            for ele in model["elements"]:
                for facename in ele["faces"]: 
                    face = ele["faces"][facename]
                    tex = face["texture"]
                    if tex[0] == '#':
                        raise KeyError("Texture name not resolve")
                    used_texture.add(tex)
        return used_texture
