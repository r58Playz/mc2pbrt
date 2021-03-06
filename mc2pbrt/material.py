import biome

class Foliage:
    def __init__(self, block):
        self.block = block

    def write(self, fout, face):
        tex = face["texture"]
        tint_color = biome.getFoliageColor(self.block.biome_id, 0)
        fout.write(('Material "translucent" "texture Kd" "%s-color" ' % tex) +
                   ('"rgb reflect" [%f %f %f] ' % tint_color) +
                   ('"rgb transmit" [%f %f %f] ' % tint_color))


class Grass:
    def __init__(self, block):
        self.block = block

    def write(self, fout, face):
        tex = face["texture"]
        tint_color = biome.getGrassColor(self.block.biome_id, 0)
        fout.write(('Material "translucent" "texture Kd" "%s-color" ' % tex) +
                   ('"rgb reflect" [%f %f %f] ' % tint_color) +
                   ('"rgb transmit" [%f %f %f] ' % tint_color))


class Matte:
    def __init__(self, block):
        self.block = block

    def write(self, fout, face):
        tex = face["texture"]
        if "tintindex" in face:
            if self.block._is("leaves"):
                tint_color = biome.getFoliageColor(self.block.biome_id, 0)
            else:
                tint_color = biome.getGrassColor(self.block.biome_id, 0)
            fout.write(('Material "matte" "texture Kd" "%s-color"' % tex) +
                       ('"rgb tintMap" [%f %f %f]\n' % tint_color))
        else:
            fout.write('Material "matte" "texture Kd" "%s-color"\n' % tex)


class Glass:
    def __init__(self, block):
        self.block = block

    def write(self, fout, face):
        tex = face["texture"]
        fout.write('Material "glass" "texture Kr" "%s-color"\n' % tex)


class Light:
    FULL_LIGHT = 5.
    def __init__(self, block):
        self.block = block

    def write(self, fout, face):
        tex = face["texture"]
        light = self.block.getLight()
        le = (light/15.)**2*Light.FULL_LIGHT
        fout.write(('AreaLightSource "texlight" "texture L" "%s-color"' % tex) +
                    '"rgb scale" [%f %f %f]\n' % (le, le, le))
