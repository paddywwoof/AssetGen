import bpy, bmesh, time, random
from bpy.types import Operator

from .GA_shader import DEF_pointinessShader_add 
from .GA_shader import DEF_ambientocclusionShader_add
from .GA_shader import DEF_albedoShader_add
from .GA_shader import DEF_normalShader_add 
from .GA_shader import DEF_pbrShader_add
from .GA_shader import DEF_maskShader_add
from .GA_shader import DEF_bentShader_add
from .GA_shader import DEF_opacityShader_add
from .GA_shader import DEF_gradientShader_add
from .GA_shader import DEF_metallicShader_add
from .GA_shader import DEF_roughnessShader_add
from .GA_shader import DEF_emissiveShader_add

            
from .GA_material import DEF_image_save_Curvature          
from .GA_material import DEF_image_save_Denoising
from .GA_material import DEF_image_save 
from .GA_material import DEF_remove_all

from .GA_composite import DEF_NormalToCurvature
from .GA_composite import DEF_denoising


from progress_report import ProgressReport, ProgressReportSubstep


class GA_Start(Operator):
    """Will generate your game asset, high poly must be in layer0. Layer1 will be deleted (excepted hidden meshes, to allow you to cast AO from them). Open the terminal to follow the progress"""

    bl_idname = "scene.ga_start"
    bl_label = "Generate Asset (layer0)"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self,context, event):
        if bpy.data.is_saved == False:
           bpy.ops.wm.save_as_mainfile("INVOKE_AREA")
           return {'RUNNING_MODAL'}
        return self.execute(context)


    def execute(self, context):


        #REMOVE ALL Layer 1
        ######################################
        DEF_remove_all()

        #Load GA property
        ######################################

        myscene = context.scene.ga_property

        wm = bpy.context.window_manager #display progression
        tot = 1000
        wm.progress_begin(0, tot)
        for i in range(tot):
            wm.progress_update(i)        
        then = time.time() #Calculate time

        print("- GAME ASSET GENERATOR beta EXECUTED -\n")

        #Init value
        ######################################

        selected_to_active = myscene.D_selected_to_active

        LOD0 = myscene.D_LOD0
        LOD1 = myscene.D_LOD1
        LOD2 = myscene.D_LOD2
        LOD3 = myscene.D_LOD3
        name = myscene.D_name

        size = [1024, 1024]
        SIZE_DICT = {'256':256, '512':512, '1K':1024, '2K':2048, '4K':4096}
        if myscene.D_textureX in SIZE_DICT:
           size[0] = SIZE_DICT[myscene.D_textureX]
        if myscene.D_textureY in SIZE_DICT:
           size[1] = SIZE_DICT[myscene.D_textureY]

        greyscale = 0   #Will apply a diffuse grey 0.735 on the high poly (and remove every other material

        #to remove later
        sprite = 0

        samples = myscene.D_samples
        unfold_half = myscene.D_unfoldhalf #Unfold half for symmetrical assets TODO set symetry in decimate is set
        cage_size = myscene.D_cage_size

        edge_padding = myscene.D_edge_padding

        edge_split = 0

        auto_calculation = 0

        decimate_HP = 0

        custom_UV = 0

        uv_margin = myscene.D_uv_margin
        uv_angle = myscene.D_uv_angle

        ground_AO = myscene.D_groundAO
        rmv_underground = myscene.D_removeunderground

        T_enabled = 0

        GPU_baking = 1

        lightmap_UVs = 0


        #Create Shader
        ######################################

        DEF_pointinessShader_add(context, size, name)
        DEF_ambientocclusionShader_add(context, size, name)
        DEF_albedoShader_add(context, size, name)
        DEF_normalShader_add(context, size, name)
        DEF_maskShader_add(context, size, name)
        DEF_bentShader_add(context, size, name)
        DEF_opacityShader_add(context, size, name)
        DEF_gradientShader_add(context, size, name)
        DEF_metallicShader_add(context, size, name)
        DEF_roughnessShader_add(context, size, name)
        DEF_emissiveShader_add(context, size, name)


        ###########################################################
        #Game Asset Generation
        ###########################################################

        if sprite == 1:
            bpy.context.scene.frame_set(1)

        if auto_calculation == 1:

            #Calculate edge padding            
            if size[0] <= size[1]:
                edge_padding = size[0] / 128
            else:
                edge_padding = size[1] / 128

            #Calculate UV margin
            uv_margin = 1/size[0]*2

            print("Auto-calculation mode enabled:")
            print("LOD1", LOD1, "tris max")
            print("LOD2", LOD2, "tris max")
            print("LOD3", LOD3, "tris max")
            print("Texture res:", size[0], "px: UV margin at", uv_margin, "and edge padding at", edge_padding,"px\n")


        if GPU_baking == 0:
           bpy.context.scene.cycles.device = 'CPU'
        if GPU_baking == 1:
           bpy.context.scene.cycles.device = 'GPU'



        #todo: save original by moving it in another collection

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
        
        bpy.ops.object.move_to_layer(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.scene.layers[1] = True
        bpy.context.scene.layers[0] = False

        if selected_to_active == 1:
            print("> Selected to Active mode enabled\n")

            if len(bpy.context.selected_objects) > 1: 

               target_object = bpy.context.active_object.name
               bpy.context.active_object.select = False


               bpy.context.scene.objects.active = bpy.context.selected_objects[0]
               bpy.ops.object.join()

               bpy.data.objects[target_object].select = True
               bpy.context.scene.objects.active = bpy.data.objects[target_object ]


               if bpy.context.selected_objects[0].name  == target_object:              
                  #bpy.context.selected_objects[0].name = "old1"  # TODO old1 and old2 seem to be overwritten???
                  #bpy.context.selected_objects[1].name = "old2"  

                  bpy.context.selected_objects[1].name = "tmpHP"
                  bpy.context.selected_objects[0].name = "tmpLP"   

               else: 

                  #bpy.context.selected_objects[0].name = "old1"
                  #bpy.context.selected_objects[0].name = "old2"

                  bpy.context.selected_objects[1].name = "tmpLP"
                  bpy.context.selected_objects[0].name = "tmpHP"

               obj = bpy.context.active_object
               LOD0 = len(obj.data.polygons)


        #If we want to generate the low poly
        ###################################
        if selected_to_active == 0:
    
            #Prepare the high poly
            ######################
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.join()

            bpy.ops.object.shade_smooth()
            bpy.context.object.data.use_auto_smooth = False

            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

            if decimate_HP == 1:
                #Remove unnecessary edges of HP
                #####################
                bpy.ops.object.mode_set(mode = 'EDIT')

                bpy.ops.mesh.select_all(action = 'SELECT')

                bpy.ops.mesh.dissolve_limited(angle_limit=0.00174533, use_dissolve_boundaries=False)
                bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

                bpy.ops.object.mode_set(mode = 'OBJECT')


            bpy.context.object.name = "tmpHP"

            #creating the low poly
            ######################
            print("\n----- GENERATING THE LOW POLY (LOD0) -----\n")

            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

            #remove every material slot of the low poly

            for ob in bpy.context.selected_editable_objects:
                ob.active_material_index = 0
                for i in range(len(ob.material_slots)):
                    bpy.ops.object.material_slot_remove({'object': ob})

            #Remove parts of the mesh bellow the grid if enabled
            if rmv_underground == 1:
                print("\n> Removing parts of the low poly bellow the grid")
                bpy.ops.object.mode_set(mode = 'EDIT') 

                bpy.ops.mesh.select_all(action = 'SELECT')

                bpy.ops.mesh.bisect(plane_co=(0.00102639, 0.0334111, 0), plane_no=(0, 0, 0.999663), use_fill=False, clear_inner=True, xstart=295, xend=444, ystart=464, yend=461)

                bpy.ops.mesh.edge_face_add()

                bpy.ops.object.mode_set(mode = 'OBJECT')

            #Restauring sharp edges
            #####################
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'SELECT')

            bpy.ops.mesh.region_to_loop()
            bpy.ops.mesh.mark_sharp()
            bpy.ops.object.mode_set(mode = 'OBJECT')

            #Cleaning the doubles
            #####################
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.mode_set(mode = 'OBJECT')

            #Remove unnecessary edges
            #####################
            bpy.ops.object.mode_set(mode = 'EDIT')

            bpy.ops.mesh.select_all(action = 'SELECT')

            bpy.ops.mesh.dissolve_limited(angle_limit=0.00174533, use_dissolve_boundaries=False)
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

            bpy.ops.object.mode_set(mode = 'OBJECT')

            #Decimation 1
            #############
            self.decimate(LOD0)

            #Create envelop by doing an Union boolean between every meshes
            ##############################################################
            if myscene.D_create_envelop == 1:

                bpy.ops.object.mode_set(mode = 'EDIT') 
                bpy.ops.mesh.select_all(action = 'DESELECT')
                bpy.ops.mesh.select_mode(type="EDGE")

                bpy.ops.mesh.select_non_manifold()
                bpy.ops.mesh.edge_face_add()

                bpy.ops.mesh.select_all(action = 'DESELECT')

                bpy.ops.mesh.separate(type='LOOSE')
                bpy.ops.object.mode_set(mode = 'OBJECT')

                ######

                print("\n> Creating the envelop")

                i = 0

                for obj in bpy.context.selected_objects:
                    bpy.context.scene.objects.active = obj

                    i = i + 1
                    bpy.context.object.name = "tmpLP" + str(i)

                print("Info: Fusionning", i, "meshes")


                bpy.ops.object.select_all(action= 'DESELECT')
                bpy.ops.object.select_pattern(pattern="tmpLP" + str(i))
                bpy.context.scene.objects.active = bpy.data.objects["tmpLP" + str(i)]

                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.object.mode_set(mode = 'OBJECT')

                while i > 1:
                    i = i - 1
                    bpy.ops.object.select_pattern(pattern="tmpLP" + str(i))
                    bpy.ops.object.join()
                    bpy.ops.object.mode_set(mode = 'EDIT')

                    bpy.ops.mesh.intersect_boolean(operation='UNION')
                    bpy.ops.mesh.select_all(action = 'SELECT')
                    bpy.ops.object.mode_set(mode = 'OBJECT')


            bpy.context.object.name = "tmpLP"

            if unfold_half == 1:
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action = 'SELECT')

                bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), clear_inner=True, clear_outer=False, xstart=849, xend=849, ystart=637, yend=473)
                bpy.ops.object.mode_set(mode = 'OBJECT')

            #Remove underground a second time, but this time remove the botton face (was needed for the create envelop)
            if rmv_underground == 1:
                bpy.ops.object.mode_set(mode = 'EDIT') 

                bpy.ops.mesh.select_all(action = 'SELECT')

                bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 0, 1), use_fill=False, clear_inner=True, clear_outer=False, threshold=0.01, xstart=373, xend=525, ystart=363, yend=369)

                bpy.ops.mesh.delete(type='FACE')

                bpy.ops.object.mode_set(mode = 'OBJECT')

            #Decimation 2
            #############
            self.decimate(LOD0, unfold_half)

            #TODO check if this improves things
            ###################################
            #Shrinkwrap
            ###########
            bpy.ops.object.modifier_add(type='SHRINKWRAP')
            bpy.context.object.modifiers['Shrinkwrap'].target = bpy.data.objects['tmpHP']
            bpy.context.object.modifiers['Shrinkwrap'].offset = 0.0
            bpy.context.object.modifiers['Shrinkwrap'].use_keep_above_surface = True
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Shrinkwrap")

            #Unfold UVs 
            ###########
            print("\n> Performing Smart UVs Project at {:3.1f} degrees with {:6.4f} of margin".format(uv_angle, uv_margin))
            bpy.ops.uv.smart_project(angle_limit=uv_angle, island_margin=uv_margin)

            if unfold_half == 1:
                print("-> Half of the low poly has been unfolded\n") 
                bpy.ops.object.modifier_add(type='MIRROR')
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Mirror")

            #bpy.ops.object.mode_set(mode = 'EDIT')
            #bpy.ops.mesh.select_all(action = 'SELECT')
            #bpy.ops.mesh.remove_doubles()

            bpy.ops.object.mode_set(mode = 'OBJECT')


            HP_polycount = len(obj.data.polygons)
            print("\n> LOD0 generated with {} tris".format(HP_polycount))

            #Lightmap UVs
            if lightmap_UVs == 1:
                bpy.ops.mesh.uv_texture_add()
                bpy.ops.object.mode_set(mode = 'EDIT')

                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.uv.lightmap_pack()

                bpy.ops.object.mode_set(mode = 'OBJECT')




        #BAKING
        ##############################################################################################################################################################################################################

        print("\n----- BAKING TEXTURES IN {} * {} -----".format(size[0], size[1]))   

        if ground_AO == 1:
            print("\n> Adding ground plane") 
            bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.transform.resize(value=(100, 100, 100), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            bpy.context.object.name = "ground_AO"

        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.ops.object.select_pattern(pattern="tmpLP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpLP"]

        bpy.ops.object.modifier_add(type='ARMATURE')

        if bpy.data.objects.get("Armature") is not None:
            bpy.context.object.modifiers["Armature"].object = bpy.data.objects["Armature"]

        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        bpy.context.object.modifiers["EdgeSplit"].use_edge_angle = False


        #Check if the low poly has UVs
        if not len( bpy.context.object.data.uv_layers ):
            print("\n> Unwrapping: the low poly has no UV map, performing Smart UVs Project at {:3.1f} degrees with {:6.4f} of margin".format(uv_angle, uv_margin))
            bpy.ops.uv.smart_project(angle_limit=uv_angle, island_margin=uv_margin)

        bpy.ops.object.select_pattern(pattern="tmpHP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpLP"]

        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.samples = 1


        #Mask map

        if myscene.T_mask == 1:
            print("\n> Baking: mask map at 1 sample")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'MASK']
            bpy.ops.object.bake(type="DIFFUSE", use_selected_to_active = True, use_cage = False, cage_extrusion = cage_size, margin = edge_padding, use_clear = True, pass_filter=set({'COLOR'}))

        #Albedo map

        if myscene.T_albedo == 1:
            print("\n> Baking: albedo map")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'ALBEDO']
            bpy.ops.object.bake(type="DIFFUSE", use_selected_to_active = True, use_cage = False, cage_extrusion = cage_size, margin = edge_padding, use_clear = True, pass_filter=set({'COLOR'}))

 
        #Normal map

        if myscene.T_normal == 1:

            bpy.context.scene.cycles.samples = 16

            print("\n> Baking: normal map at 16 samples")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'NORMAL']
            bpy.ops.object.bake(type="NORMAL", normal_space ='TANGENT', use_selected_to_active = True, use_cage = False, cage_extrusion = cage_size, margin = edge_padding, use_clear = True)

            bpy.context.scene.cycles.samples = 1

        #Curvature map

        if myscene.T_curvature == 1:

            print("\n> Compositing: curvature map from normal map")

            DEF_NormalToCurvature(context,size,name)
            DEF_image_save_Curvature( name )

        #Bent map

        if myscene.T_bent == 1:

            bpy.context.scene.cycles.samples = 16

            print("\n> Baking: bent map at 16 samples")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'BENT']
            bpy.ops.object.bake(type="NORMAL", normal_space ='OBJECT', use_selected_to_active = True, use_cage = False, cage_extrusion = cage_size, margin = edge_padding, normal_r = 'POS_X', normal_g = 'POS_Z', normal_b = 'NEG_Y', use_clear = True)

            bpy.context.scene.cycles.samples = 1

        #Ambient Occlusion map

        if myscene.T_ao == 1:

            bpy.context.scene.cycles.samples = samples
            bpy.context.scene.world.light_settings.distance = 10

            print("\n> Baking: ambient occlusion map at {} samples".format(samples))

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'AMBIENT OCCLUSION']
            bpy.ops.object.bake(type="AO", use_selected_to_active = True, use_cage = False, cage_extrusion = cage_size, margin = edge_padding, use_clear = True)

            bpy.context.scene.cycles.samples = 1

        #DENOISING

        if myscene.T_ao_denoising == 1:

            print("\n> Compositing: denoising the ambient occlusion map\n")

            DEF_denoising(context,size,name)
            DEF_image_save_Denoising ( name,1 )
        else:
            DEF_image_save_Denoising ( name,0 )

        #Emissive map
        if myscene.T_emissive == 1:

            print("\n> Baking: emissive map at 1 sample")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'EMISSIVE']
            bpy.ops.object.bake(type="EMIT", use_selected_to_active = True, use_cage = False, cage_extrusion = cage_size, margin = edge_padding, use_clear = True)

        #remove every materials of the high poly
        print("> Removing every materials on the high poly")
        bpy.ops.object.select_all(action = 'DESELECT')

        bpy.ops.object.select_pattern(pattern="tmpHP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpHP"]

        for ob in bpy.context.selected_editable_objects:
            ob.active_material_index = 0
            for i in range(len(ob.material_slots)):
                bpy.ops.object.material_slot_remove({'object': ob})

        bpy.ops.object.select_pattern(pattern="tmpLP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpLP"]

        #Pointiness map

        if myscene.T_pointiness == 1:
            print("\n> Baking: pointiness map at 1 sample")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'POINTINESS']
            bpy.data.objects['tmpHP'].active_material = bpy.data.materials[name+"_"+'POINTINESS']        
            bpy.ops.object.bake(type="EMIT", use_selected_to_active = True, use_cage = False, cage_extrusion = cage_size, margin = edge_padding, use_clear = True)

        #Gradient map
        if myscene.T_gradient == 1:
            print("\n> Baking: gradient map at 1 sample")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'GRADIENT']
            bpy.data.objects['tmpHP'].active_material = bpy.data.materials[name+"_"+'GRADIENT']

            bpy.ops.object.bake(type="EMIT", use_selected_to_active = True, use_cage = False, cage_extrusion = cage_size, margin = edge_padding, use_clear = True, pass_filter=set({'COLOR'}))

        #Opacity map
        if myscene.T_opacity == 1:
            print("\n> Baking: opacity map at 1 sample")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'OPACITY']
            bpy.data.objects['tmpHP'].active_material = bpy.data.materials[name+"_"+'OPACITY']

            bpy.ops.object.bake(type="EMIT", use_selected_to_active = True, use_cage = False, cage_extrusion = cage_size, margin = edge_padding, use_clear = True, pass_filter=set({'COLOR'}))

        #Finalizing
        ####################
        print("\n----- FINALIZING-----\n")

        #Create the lighting
        ####################
        bpy.ops.object.lamp_add(type='HEMI', view_align=False, location=(0, 0, 5),      layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.data.energy = 0.5

        bpy.ops.object.lamp_add(type='HEMI', view_align=False, location=(0, 0, -5), layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

        bpy.ops.transform.rotate(value=-3.14159, axis=(-0, 1, 1.34359e-007), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.context.object.data.energy = 0.1

        bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=(0.5, -1.5, 2), layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

        #delete the high poly
        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.ops.object.select_pattern(pattern="tmpHP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpHP"]

        bpy.ops.object.delete(use_global=False)

        #delete the ground        
        if ground_AO == 1:
            bpy.ops.object.select_all(action = 'DESELECT')
            bpy.ops.object.select_pattern(pattern="ground_AO")
            bpy.context.scene.objects.active = bpy.data.objects["ground_AO"]

            bpy.ops.object.delete(use_global=False)

        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.ops.object.select_pattern(pattern="tmpLP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpLP"]




        #Create the PBR material, need to update it in the future for EEVEE
        #################################
        DEF_pbrShader_add(context,size,name)

        bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'PBR']

        bpy.context.object.name = name + "_LOD0"
        bpy.context.object.data.name = name + "_LOD0"


        #Generating the LODs
        ####################

        bpy.ops.object.mode_set(mode = 'EDIT')                        
        bpy.ops.mesh.select_all(action = 'SELECT')        
        bpy.ops.object.mode_set(mode = 'OBJECT')

        for lod, lod_ending in ((LOD1, "_LOD1"), (LOD2, "_LOD2"), (LOD3, "_LOD3")):
            if lod > 0:
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 3, 0), "constraint_axis":(False, True, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
                bpy.context.object.name = name + lod_ending
                bpy.context.object.data.name = name + lod_ending

                #decimation of the LODx
                #######################
                self.decimate(lod)
                #TODO: Export LODx in OBJ

                HP_polycount = len(obj.data.polygons)
                print("\n>{} generated with {} tris\n".format(lod_ending, HP_polycount))

        bpy.ops.object.select_all(action = 'DESELECT')

        bpy.ops.object.select_pattern(pattern= name + "_LOD0")
        bpy.context.scene.objects.active = bpy.data.objects[name + "_LOD0"]

        print("\n> Saving every texture")

        DEF_image_save( name )

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.viewport_shade = 'MATERIAL'
                        area.spaces[0].fx_settings.use_ssao = False

        bpy.context.scene.render.engine = 'BLENDER_RENDER'

        wm.progress_end()
        now = time.time() #Time after it finished

        print("\n----- GAME ASSET READY -----") 
        print("\nAsset generated in {:3.1f} seconds\n\n".format(now - then))

        return {'FINISHED'}

    def decimate(self, lod, unfold_half=0):
        bpy.ops.object.modifier_add(type='TRIANGULATE')
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")

        bpy.ops.object.modifier_add(type='DECIMATE')
        obj = bpy.context.active_object
        HP_polycount = len(obj.data.polygons)

        decimation = (lod / HP_polycount)
        if unfold_half == 1:
            decimation *= 0.5

        bpy.context.object.modifiers["Decimate"].ratio = decimation
        bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True
        if unfold_half == 1:
            bpy.context.object.modifiers["Decimate"].use_symmetry = True
            bpy.context.object.modifiers["Decimate"].symmetry_axis = "X"

        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

