import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator
from .import_sm3 import ImportSM3


bl_info = {
    "name": "CBS Jericho import/export",
    "description": "import or export CBS Jericho .sm3 files",
    "author": "Glogow Poland Mariusz Szkaradek",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "category": "Import-Export"}


def import_sm3(context, filepath):
    print("Running read_some_data...")
    f = open(filepath, 'rb')
    mdl = ImportSM3(f, filepath)
    mdl.make_armature()
    print("Armature was built")
    mdl.readdata()
    mdl.draw_all()
    f.close()
    return {'FINISHED'}


class ImportJerichoSM3(Operator, ImportHelper):
    """Imported for Clive Baker's Jericho mesh format"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Jericho SM3"

    # ImportHelper mixin class uses this
    filename_ext = ".sm3"

    filter_glob: StringProperty(
        default="*.sm3",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return import_sm3(context, self.filepath)


# Only needed if you want to add into a dynamic menu.
def menu_func_import(self, context):
    self.layout.operator(ImportJerichoSM3.bl_idname, text="Import Jericho .sm3")


# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access).
def register():
    bpy.utils.register_class(ImportJerichoSM3)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportJerichoSM3)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
