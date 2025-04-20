import bpy
import struct
import os
from struct import *
from mathutils import Matrix, Vector
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


bl_info = {
    "name": "CBS Jericho import/export",
    "description": "import or export CBS Jericho .sm3 files",
    "author": "Glogow Poland Mariusz Szkaradek",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "category": "Import-Export"}


def import_sm3(context, filepath):
    print("running read_some_data...")
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


class ImportSM3():
    def __init__(self, file, filepath):
        self.file = file
        self.filepath = filepath
        self.modelname = os.path.basename(filepath).split('.')[0]
        self.armature_ob = None
        self.newarm = None
        self.meshes = {}  # name | face indices + UV | groups | grupy - bone id?
        self.mesh_name = ""
        self.grupy = []
        self.groups = []
        self.namebone = ""
        self.bonenames = []
        self.id_object = 0
        self.mesh = None
        self.obj = None
        self.vertexy = None
        self.faceslist = None
        self.uvcoord = None

    def read_string(self, long):
        string = ''
        for j in range(0, long): 
            lit = struct.unpack('c', self.file.read(1))[0]
            if ord(lit) != 0:
                string += lit.decode('latin')
                if len(string) > 100:
                    break
        return string

    def read_byte(self, n):
        return struct.unpack(n*'b', self.file.read(n))

    def read_ubyte(self, n):
        return struct.unpack(n*'B', self.file.read(n))

    def read_short(self, n):
        return struct.unpack(n*'h', self.file.read(n*2))

    def read_ushort(self, n):
        return struct.unpack(n*'H', self.file.read(n*2))

    def read_int(self, n):
        return struct.unpack(n*'i', self.file.read(n*4))

    def read_float(self, n):
        return struct.unpack(n*'f', self.file.read(n*4))

    def create_material(self, m):
        # global mat
        self.read_string(8), self.read_int(1)  # MAT
        print('MATERIAL ', self.read_string(self.read_int(1)[0]))
        try:
            mat = bpy.data.materials[('mat-'+str(m))]
        except:
            mat = bpy.data.materials.new('mat-'+str(m))
        mat.use_nodes = True
        mat.blend_method = 'CLIP'
        self.read_ubyte(44), self.read_int(3)  # NOTHING
        return mat

    def make_armature(self):
        namefile = self.filepath.split(os.sep)[-1].split('.')[0]
        #global armobj,newarm
        #armobj=None
        #newarm=None
        #scn = Scene.GetCurrent()
        scene = bpy.context.scene
        #for object in scene.objects:
        #    if obj.type == 'ARMATURE':
        #        if object.name == namefile+'-armobj':
        #            scn.unlink(object)
        #for object in bpy.data.objects:
        #    if object.name == namefile+'-armobj':
        #        armobj = Blender.Object.Get(namefile+'-armobj')
        #        newarm = armobj.getData()
        #        newarm.makeEditable()		 
        #        for bone in newarm.bones.values():
        #            del newarm.bones[bone.name]
        #        newarm.update()
        #if armobj==None: 
        #    #armobj = Blender.Object.New('Armature',namefile+'-armobj')
        #    armature_ob = bpy.data.objects.new('Armature',namefile+'-armobj', armature)
        #if newarm==None: 
        #    #newarm = Armature.New(namefile+'-arm')
        #    armature = bpy.data.armatures.new(namefile+'-arm')
        #    armobj.link(newarm)
        #scn.link(armobj)
        armature = bpy.data.armatures.new(namefile+'-arm')
        self.armature_ob = bpy.data.objects.new(namefile + '-armobj', armature)
        bpy.context.collection.objects.link(self.armature_ob)
        bpy.context.view_layer.objects.active = self.armature_ob
        self.armature_ob.data.display_type = 'STICK'
        #newarm.drawType = Armature.STICK

        #test = bpy.data.objects[namefile +'-armobj']
        #for bone in armature.pose.bones:
        #    bone.draw_type = 'STICK'

    def make_bones(self):
        # global namebone
        bpy.ops.object.mode_set(mode='EDIT', toggle=False)
        self.newarm = self.armature_ob.data
        # newarm.makeEditable()
        ebs = self.newarm.edit_bones
        data = self.read_int(6)
        # print("bone data is {}".format(data))
        self.namebone = self.read_string(self.read_int(1)[0])[-25:]
        # print("namebone is {}".format(self.namebone))
        self.bonenames[data[1]] = self.namebone
        #eb = A.Editbone()
        eb = ebs.new(self.namebone)
        #newarm.bones[namebone] = eb
        #self.armature_ob.data.bones.append(eb)
        #newarm.update()
        #newarm.makeEditable()
        nameparent = self.read_string(self.read_int(1)[0])[-25:]
        # print("parent bone is {}".format(nameparent))
        if len(nameparent) > 0:
            parent = self.newarm.edit_bones[nameparent]
            self.newarm.edit_bones[self.namebone].parent = parent
        self.read_float(8)
        # bonematrix = Matrix([self.read_float(4), self.read_float(4), self.read_float(4), self.read_float(4)])
        x = self.read_float(4)
        y = self.read_float(4)
        z = self.read_float(4)
        w = self.read_float(4)
        imported_matrix = Matrix([x, y, z, w])
        bonematrix = imported_matrix.transposed()
        self.read_float(23)
        #newarm.update()
        #newarm.makeEditable()
        bone = self.newarm.edit_bones[self.namebone]
        bone.matrix = bonematrix
        bone.head = Vector((0, 0, 0))
        bone.tail = Vector((bone.head[0], bone.head[1], bone.head[2] + 0.01))
        # bone.head = Vector((w[0], w[1], w[2]))
        # bone.tail = Vector((bone.head[0], bone.head[1], bone.head[2] + 0.01))
        # print(dir(bone))
        bone.transform(bonematrix)
        # bone.matrix_basis (bonematrix)
        # bone.matrix = bonematrix
        # newarm.update()

    def read_mesh_data(self, num):
        # global grupy
        self.grupy = []
        print(self.namebone + '=' + str(num))
        self.meshes[self.namebone + '='+str(num)] = []
        print('ADD FACES')
        self.meshes[self.namebone + '='+str(num)].append(self.read_faces())
        self.read_string(4)
        print('ADD VERTEXES UVCOORD')
        self.meshes[self.namebone + '='+str(num)].append(self.read_vertexes())
        print('ADD VERTEX GROUPS')
        self.meshes[self.namebone + '='+str(num)].append(self.groups)
        data = self.read_int(2)
        print(self.namebone + '='+str(num))
        print('VERTEX GROUPS IS', data)
        for k in range(data[0]):
            vtx_groups = self.read_ushort(1)[0]
            self.grupy.append(vtx_groups)
        print('ADD GRUPY')
        self.meshes[self.namebone+'='+str(num)].append(self.grupy)
        self.read_int(2), self.read_int(2), self.read_int(2), self.read_int(2)
        data = self.read_int(2)
        if data[1] == 0:
            data1 = self.read_int(2)
            print('making limited groups', data1)
            for m in range(data1[0]):
                num_bones = self.read_ubyte(1)[0]
                vtx_groups = self.read_ubyte(3)
                weights = self.read_float(3)
                # num_bones 1-3, supports only 3 bones per vertex
                self.groups.append([num_bones, vtx_groups, weights])
        data = self.read_int(2)
        for m in range(data[0]):
            self.read_ubyte(data[1])
        mat_id = self.read_int(2)
        self.read_int(1)
        objectmatrix = self.read_float(16)
        # print(self.id_object)
        self.meshes[self.namebone+'='+str(num)].append(objectmatrix)
        # add id_mat
        self.meshes[self.namebone+'='+str(num)].append(mat_id[0])

    def read_materials(self):
        # global dir_images,name_image
        # dir_images = sys.dirname(filename)+os.sep+'dds'+os.sep
        dir_images = os.path.dirname(self.filepath) + os.sep+'dds' + os.sep
        dir_images = dir_images.lower()
        num_mat = self.read_int(1)[0]
        print('num_mat =', num_mat)
        for m in range(num_mat):
            mat = self.create_material(m)
            mat.use_nodes = True
            mat.blend_method = 'CLIP'
            shader_node_grp = mat.node_tree.nodes.get("Principled BSDF")
            link = mat.node_tree.links.new
            while (True):
                data = self.read_int(1)[0]
                if data == 0:
                    pass
                elif data == 1:
                    self.read_string(8), self.read_int(1)
                    name_image = self.read_string(self.read_int(1)[0]).split('/')[-1].split('.')[0]
                    name_image = name_image.lower()
                    texture_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                    try:
                        texture_node.image = bpy.data.images.load(dir_images+name_image+'.dds')
                    except:
                        print("no textures {}".format(dir_images+name_image+'.dds'))
                    if '-d' in name_image:
                        # Diffuse
                        link(texture_node.outputs['Color'], shader_node_grp.inputs['Base Color'])
                        link(texture_node.outputs['Alpha'], shader_node_grp.inputs['Alpha'])
                        texture_node.location = (-300, 350)
                    if '-m' in name_image:
                        # Specular
                        link(texture_node.outputs['Color'], shader_node_grp.inputs['Roughness'])
                        texture_node.location = (-300, -350)
                    if '-b' in name_image:
                        # Normal
                        # # RGB nodes
                        normal_separate = mat.node_tree.nodes.new('ShaderNodeSeparateRGB')
                        normal_separate.name = "separate_normal"
                        normal_separate.label = "Separate Normal"
                        normal_separate.location = (-600, 0)

                        normal_combine = mat.node_tree.nodes.new('ShaderNodeCombineRGB')
                        normal_combine.name = "combine_normal"
                        normal_combine.label = "Combine Normal"
                        normal_combine.location = (-400, 0)

                        # # Normal node
                        normal_map = mat.node_tree.nodes.new('ShaderNodeNormalMap')  # create normal map node
                        normal_map.inputs[0].default_value = 1.5
                        normal_map.location = (-200, 0)

                        link(texture_node.outputs['Color'], normal_separate.inputs[0])
                        link(texture_node.outputs['Alpha'], normal_combine.inputs['R'])
                        link(normal_separate.outputs['G'], normal_combine.inputs['G'])
                        link(normal_combine.outputs[0], normal_map.inputs['Color'])
                        link(normal_map.outputs['Normal'], shader_node_grp.inputs['Normal'])

                        texture_node.location = (-900, 0)
                    data = self.read_int(4)
                    if data[3] != 0:
                        break
                    self.read_ubyte(11)
                else:
                    seek = self.file.tell()
                    self.file.seek(seek-4)
                    break

    def readdata(self):
        # global bonenames,meshes,id_object
        self.bonenames = []
        id_object = 0
        magic_word = self.read_string(8)
        unk_bytes = self.read_ubyte(12)
        unk_str = self.read_string(4)
        unk_int = self.read_int(3)
        str_num = self.read_int(1)
        unk_str_01 = self.read_string(str_num[0])
        unk_int_01 = self.read_int(1)
        unk_str_02 = self.read_string(4)  # INI
        data = self.read_int(3)  # 0, 1 , 31
        print(data)
        for m in range(data[2]):
            long = (self.read_int(1)[0])
            print(self.read_string(long))
        print(self.read_float(15))
        self.read_materials()  # ---------------MATERIALS
        seek = self.file.tell()
        self.file.seek(seek-36)
        print(self.file.tell())
        data = self.read_int(2)
        print()
        print('==== MAKING NODES ====')
        print
        print('begin----------', data[0])
        print('num nodes------', data[1])
        for m in range(data[1]):
            self.bonenames.append('')
        for m in range(data[1]):
            self.make_bones()
            long = self.read_int(1)[0]
            # INI node?
            for n in range(long):
                unk_node_str = self.read_string(4)
                print("Unknows node id is ", unk_node_str)
                data = self.read_int(3)
                # Bone adjustments
                for k in range(data[2]):
                    long = self.read_int(1)[0]
                    node_str = self.read_string(long)
                    print("Node string is {}".format(node_str))
            long = self.read_int(1)[0]
            for n in range(long):
                id_object += 1
                self.read_int(1)
                num = 0
                self.groups = []
                while (True):
                    name = self.read_string(4)
                    if name == 'CAM':
                        self.read_int(5), self.read_float(14)
                        break
                    elif name == 'MD3D':
                        self.read_mesh_data(num)
                        data = self.read_int(1)[0]
                        if data == 0:
                            break
                        num += 1
                    else:
                        break
        print(struct.unpack('i', self.file.read(4))[0])
        print('KONIEC AT OFFSET ', self.file.tell())

    def read_faces(self):
        faceslist = []
        data = self.read_int(3)
        self.read_string(data[2])
        data = self.read_int(2)
        for m in range(data[0]):
            v = self.read_ushort(3)
            faceslist.append(v)
        return faceslist

    def read_vertexes(self):
        vertexes = []
        uvcoord = []
        data = self.read_int(6)
        print("read vertex data", data)
        if data[4] == 48:
            for m in range(data[5]):
                v = self.read_float(3)
                vertexes.append(v)
                self.read_float(3)
                u = self.read_float(1)[0]
                v = self.read_float(1)[0]
                uvcoord.append([u, 1-v])
                self.read_float(4)

        if data[4] == 80:
            for m in range(data[5]):
                v = self.read_float(3)
                vertexes.append(v)
                self.read_float(3)
                u = self.read_float(1)[0]
                v = self.read_float(1)[0]
                uvcoord.append([u, 1-v])
                self.read_float(6)
                self.read_float(2)
                self.read_float(4)

        return vertexes, uvcoord

    def draw_all(self):
        # global mesh_name, faceslist, vertexy, uvcoord, groups, grupy
        for self.mesh_name in self.meshes:
            mesh_data = self.meshes[self.mesh_name]
            self.faceslist = mesh_data[0]
            self.vertexy = mesh_data[1][0]
            self.uvcoord = mesh_data[1][1]
            self.groups = mesh_data[2]  # data for all vertices
            self.grupy = mesh_data[3]  # all vertices?
            mat_id = mesh_data[5]
            self.drawmesh(self.mesh_name)
            if len(self.groups) == 0:
                matrix = self.make_right_mesh_position()
                #self.obj.setMatrix(matrix)
                self.obj.matrix_world = matrix
                # parent mesh objects to the armature
                # self.armobj.makeParentBone([self.obj], mesh_name.split('=')[0], 0, 0)
                self.obj.parent = self.armature_ob
                self.obj.parent_type = 'BONE'
                self.obj.parent_bone = self.mesh_name.split('=')[0]

            else:
                self.make_vertex_group()
                #armobj.makeParentDeform([obj],1,0)
                armature_modifier = self.obj.modifiers.new(name="Armature Modifier", type='ARMATURE')
                armature_modifier.object = self.armature_ob
            print("Material name is", ('mat-'+str(mat_id)))
            material = bpy.data.materials.get('mat-'+str(mat_id))
            if material:
                self.mesh.materials.append(material)
            #self.mesh.materials[0] = bpy.data.materials.get('mat-'+str(mat_id))
            #Redraw()

    def drawmesh(self, name):
        # global obj,mesh
        self.mesh = bpy.data.meshes.new(name)
        self.mesh.from_pydata(self.vertexy, [], self.faceslist)
        #self.mesh.verts.extend(self.vertexy)
        #self.mesh.faces.extend(self.faceslist, ignoreDups=True)
        if len(self.uvcoord) != 0:
            self.uv()
        #scene = bpy.data.scenes.active
        #self.obj = scene.objects.new(self.mesh, name)
        self.obj = bpy.data.objects.new(name, self.mesh)
        bpy.context.collection.objects.link(self.obj)
        #mesh.recalcNormals()
        #mesh.update()
        #Redraw()

    def uv(self):
        if not self.mesh.uv_layers:
            self.mesh.uv_layers.new(name="uv")
        uv_layer = self.mesh.uv_layers.active.data
        # Assign UV coordinates to each loop
        for poly in self.mesh.polygons:
            for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
                vertex_index = self.mesh.loops[loop_index].vertex_index
                uv_layer[loop_index].uv = self.uvcoord[vertex_index]

    def make_vertex_group(self):
        for v_id in range(len(self.grupy)):
            data_id = self.grupy[v_id]
            #data = self.groups[data_id]
            num_bones, bone_ids, weights = self.groups[data_id]
            vertex_groups = self.obj.vertex_groups
            for i in range(num_bones):
                bone_id = bone_ids[i]
                weight = weights[i]
                bone_name = self.bonenames[bone_id]
                try:
                    vertex_groups[bone_name].add([v_id], weight, 'REPLACE')
                except KeyError:
                    self.obj.vertex_groups.new(name=bone_name)
                    vertex_groups[bone_name].add([v_id], weight, 'REPLACE')

            #for m in range(data[0]):
            #    gr = data[1][m]
            #    try:
            #        gr = self.bonenames[gr]
            #    except:
            #        gr = str(gr)
            #        pass
            #    w = data[2][m]
            #    try:
            #        vertex_groups[gr].add([v_id], w, 'REPLACE')
            #    except KeyError:
                    # print("There is no vertex group", sw.group_name)
             #       self.obj.vertex_groups.new(name=gr)
             #       vertex_groups[gr].add([v_id], w, 'REPLACE')
                #if gr not in mesh.getVertGroupNames():
                #    self.mesh.addVertGroup(gr)
                #    self.mesh.update()
                #mesh.assignVertsToGroup(gr,[v_id],w,1)
        # mesh.update()

    def make_right_mesh_position(self):
        name = self.mesh_name.split('=')[0]
        bone_mat_world = obj_matrix = self.obj.matrix_world
        # bones = self.newarm.bones.values()
        #bones = self.armature_ob.bones
        #bpy.ops.object.mode_set(mode='EDIT')
        bones = self.armature_ob.data.bones
        for bone in bones:
            if bone.name == name:
                # bone_mat = bone.matrix['ARMATURESPACE']
                bone_mat = bone.matrix_local
                bone_mat_world = bone_mat*obj_matrix
        return bone_mat_world


def read_string_test(plik,long):  # read string
    s=''
    for j in range(0, long):
        lit = struct.unpack('c', plik.read(1))[0]
        if ord(lit)!=0:
            s += lit.decode('latin')
            if len(s) > 100:
                break
    return s


def drawmesh(name): 
    global obj,mesh
    mesh = bpy.data.meshes.new(name)
    mesh.verts.extend(vertexy)
    mesh.faces.extend(faceslist,ignoreDups=True)
    if len(uvcoord)!=0:
        uv()
    scene = bpy.data.scenes.active
    obj = scene.objects.new(mesh,name)
    mesh.recalcNormals()
    mesh.update()
    Redraw()

def uv():
    for faceID in range(0,len(mesh.faces)):
            face = mesh.faces[faceID]
            index1 = faceslist[faceID][0]
            index2 = faceslist[faceID][1]
            index3 = faceslist[faceID][2]
            uv1 = Vector(uvcoord[index1])
            uv2 = Vector(uvcoord[index2])
            uv3 = Vector(uvcoord[index3])
            face.uv = [uv1, uv2, uv3]
            face.smooth=True

def make_armature(filename):
    namefile = filename.split(os.sep)[-1].split('.')[0]
    global armobj,newarm
    armobj=None
    newarm=None
    scn = Scene.GetCurrent()
    scene = bpy.data.scenes.active
    for object in scene.objects:
        if object.getType()=='Armature':
            if object.name == namefile+'-armobj':
                scn.unlink(object)
    for object in bpy.data.objects:
        if object.name == namefile+'-armobj':
            armobj = Blender.Object.Get(namefile+'-armobj')
            newarm = armobj.getData()
            newarm.makeEditable()		 
            for bone in newarm.bones.values():
                del newarm.bones[bone.name]
            newarm.update()
    if armobj==None: 
        armobj = Blender.Object.New('Armature',namefile+'-armobj')
    if newarm==None: 
        newarm = Armature.New(namefile+'-arm')
        armobj.link(newarm)
    scn.link(armobj)
    newarm.drawType = Armature.STICK

def create_material(m):
    #global mat
    read_string(8),read_int(1)#MAT
    print('MATERIAL ', read_string(read_int(1)[0]))
    try:
        mat = Material.Get('mat-'+str(m))
    except:
        mat = Material.New('mat-'+str(m))
    read_ubyte(44),read_int(3) # NOTHING

def create_texture_diffuse(m):
    try:
        tex = Texture.Get('tex-'+str(m))
    except:
        tex = Texture.New('tex-'+str(m))
    tex.setType('Image')
    try:
        img = Blender.Image.Load(dir_images+name_image+'.dds')
        tex.image = img 
        mat.setTexture(0,tex,Texture.TexCo.UV,Texture.MapTo.COL) 
    except:
        pass

def create_texture_specular(m):
    try:
        tex_alpha = Texture.Get('tex_alpha-'+str(m))
    except:
        tex_alpha = Texture.New('tex_alpha-'+str(m))
    tex_alpha.setType('Image')
    try:
        img = Blender.Image.Load(dir_images+name_image+'.alpha.dds')
        tex_alpha.image = img 
        mat.setTexture(1,tex_alpha,Texture.TexCo.UV,Texture.MapTo.COL) 
    except:
        pass

def create_texture_normal(m):
    try:
        tex_norm = Texture.Get('tex_norm-'+str(m))
    except:
        tex_norm = Texture.New('tex_norm-'+str(m))
    tex_norm.setType('Image')
    tex_norm.setImageFlags('NormalMap')  
    try:
        img = Blender.Image.Load(dir_images+name_image+'.dds')
        tex_norm.image = img 
        mat.setTexture(2,tex_norm,Texture.TexCo.UV,Texture.MapTo.NOR) 
    except:
        pass

def read_materials(filename): 
    global dir_images,name_image
    dir_images = sys.dirname(filename)+os.sep+'dds'+os.sep
    dir_images = dir_images.lower()
    num_mat = read_int(1)[0]
    print ('num_mat =',num_mat)
    for m in range(num_mat):
        create_material(m)
        while(True):
            data = read_int(1)[0]
            if data == 0:
                pass 
            elif data ==1: 
                read_string(8),read_int(1) 
                name_image = read_string(read_int(1)[0]).split('/')[-1].split('.')[0]
                name_image = name_image.lower() 
                # print name_image
                if '-d' in name_image:
                    create_texture_diffuse(m)
                if '-m' in name_image:
                    create_texture_specular(m)
                if '-b' in name_image:
                    create_texture_normal(m)

                data = read_int(4)
                if data[3]!=0:
                    break 
                read_ubyte(11) 
            else:
                seek = plik.tell()
                plik.seek(seek-4)
                break	  

def make_bones(m):
    global namebone 
    newarm.makeEditable()
    data = read_int(6)
    print(data)
    namebone = read_string(read_int(1)[0])[-25:]
    #print namebone
    bonenames[data[1]] = namebone
    eb = A.Editbone() 
    newarm.bones[namebone] = eb
    newarm.update()
    newarm.makeEditable()
    nameparent = read_string(read_int(1)[0])[-25:]		
    if len(nameparent)>0:
        parent = newarm.bones[nameparent]
        newarm.bones[namebone].parent = parent
    read_float(8)
    bonematrix = [(read_float(4),read_float(4),read_float(4),read_float(4))]
    print(bonematrix)
    read_float(23)
    newarm.update()
    newarm.makeEditable()
    bone = newarm.bones[namebone]
    bone.matrix = bonematrix
    newarm.update()

def read_mesh_data(num):
    global grupy
    grupy = []
    print(namebone+'='+str(num))
    meshes[namebone+'='+str(num)]=[]
    print ('ADD FACES')
    meshes[namebone+'='+str(num)].append(read_faces())
    read_string(4)
    print ('ADD VERTEXES UVCOORD')
    meshes[namebone+'='+str(num)].append(read_vertexes())
    #print 'ADD GROUPS'
    meshes[namebone+'='+str(num)].append(groups)
    data = read_int(2) 
    print(namebone+'='+str(num))
    print('ADD GROUPS',data)
    for k in range(data[0]):
        gr =  read_ushort(1)[0]
        grupy.append(gr)
    print ('ADD GRUPY')
    meshes[namebone+'='+str(num)].append(grupy)
    read_int(2),read_int(2),read_int(2),read_int(2)
    data = read_int(2)
    if data[1]==0:
        data1 = read_int(2)
        print ('making limited groups',data1)
        for m in range(data1[0]):
            num_gr = read_ubyte(1)[0]
            gr = read_ubyte(3) 
            w  = read_float(3) 
            #print num,gr,w
            groups.append([num_gr,gr,w])	
    data = read_int(2)
    for m in range(data[0]):
        read_ubyte(data[1])
    data = read_int(2)
    read_int(1) 
    objectmatrix = read_float(16)
    print (id_object)
    meshes[namebone+'='+str(num)].append(objectmatrix)
    #add id_mat
    meshes[namebone+'='+str(num)].append(data[0])

def readdata(file):
    #global bonenames,meshes,id_object
    bonenames = []
    meshes = {}
    id_object = 0
    magic_word = read_string(file,8)
    unk_bytes = read_ubyte(file,12)
    unk_str = read_string(file,4)
    unk_int = read_int(file,3)
    str_num = read_int(file,1)
    unk_str_01 = read_string(file,str_num[0])
    unk_int_01 =read_int(file,1)
    unk_str_02 =read_string(file,4) #  INI
    data = read_int(file,3) # 0, 1 , 31
    print (data)
    for m in range(data[2]):
        long = (read_int(file,1))[0]
        print (read_string(file, long))
    print (read_float(file, 15)) 
    read_materials(file)#----------------MATERIALS
    seek = plik.tell()
    plik.seek(seek-36)
    print (plik.tell())  
    data = read_int(2)
    print()
    print ('==== MAKING NODES ====')
    print
    print ('begin----------',data[0])
    print ('num nodes------',data[1])
    for m in range(data[1]):
        bonenames.append('')
    for m in range(data[1]):
    #for m in range(10):
        make_bones(m)
        long =  read_int(1)[0]
        for n in range(long):
            read_string(4)
            data = read_int(3)
            for k in range(data[2]):
                long = read_int(1)[0]
                read_string(long)
        long = read_int(1)[0]
        for n in range(long):
            id_object+=1
            read_int(1)
            num = 0 
            global groups
            groups = []
            while(True):
                name = read_string(4)
                if name == 'CAM':
                    read_int(5),read_float(14)
                    break
                elif name == 'MD3D':
                    read_mesh_data(num)
                    data = read_int(1)[0]
                    if data==0:
                        break
                    num+=1
                else: 
                    break
    print(struct.unpack('i',plik.read(4))[0])
    print('KONIEC AT OFFSET ',plik.tell())


def draw_all():
    global mesh_name,faceslist,vertexy,uvcoord,groups,grupy
    for mesh_name in meshes:
        mesh_data = meshes[mesh_name]
        faceslist = mesh_data[0]
        vertexy   = mesh_data[1][0]
        uvcoord   = mesh_data[1][1]
        groups	= mesh_data[2]
        grupy	 = mesh_data[3]
        mat_id	= mesh_data[5]
        drawmesh(mesh_name)
        if len(groups) == 0:
            matrix = make_right_mesh_position()
            obj.setMatrix(matrix)
            Redraw()
            armobj.makeParentBone([obj],mesh_name.split('=')[0],0,0) 
        else:
            make_vertex_group()
            armobj.makeParentDeform([obj],1,0)
        mesh.materials+=[Material.Get('mat-'+str(mat_id))]
        Redraw()
  

def text3d():
    try:
        text = Blender.Object.Get('Font')
        textdata = text.getData()
        textdata.setText(namemodel)
        text.makeDisplayList()
        Redraw()
    except:
        pass	 



def openfile(filename):
    global plik,namemodel
    plik = open(filename,'rb')
    make_armature(filename)
    namemodel = sys.basename(filename).split('.')[0]
    readdata(filename)
    draw_all() 
    text3d()


#Window.FileSelector(openfile)