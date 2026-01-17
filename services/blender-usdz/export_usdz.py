#!/usr/bin/env python3
"""
GLB to USDZ converter for Blender - bakes vertex colors to texture for USD export
"""
import bpy
import sys
import os
import math


def clear_scene():
    """Clear all objects and data from the current scene"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Clear orphan data blocks
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)
    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)
    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)


def create_uv_layer(obj):
    """Create a UV layer for the mesh using smart UV project"""
    mesh = obj.data
    
    # Create UV layer if it doesn't exist
    if not mesh.uv_layers:
        mesh.uv_layers.new(name='UVMap')
    
    # Select object and make active
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Enter edit mode and unwrap
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    print(f"  Created UV layer for {obj.name}")
    return mesh.uv_layers.active


def bake_vertex_colors_to_texture(obj, texture_size=2048):
    """Bake vertex colors to a texture image"""
    mesh = obj.data
    
    # Check if mesh has vertex colors
    if not mesh.color_attributes:
        print(f"  No vertex colors found on {obj.name}")
        return None
    
    vertex_color_name = mesh.color_attributes[0].name
    print(f"  Found vertex colors: {vertex_color_name}")
    
    # Ensure UV layer exists
    if not mesh.uv_layers:
        create_uv_layer(obj)
    
    # Create bake target image
    image_name = f"{obj.name}_baked"
    bake_image = bpy.data.images.new(image_name, texture_size, texture_size, alpha=False)
    bake_image.colorspace_settings.name = 'sRGB'
    
    # Get or create material
    if not obj.data.materials:
        mat = bpy.data.materials.new(name=f"{obj.name}_Material")
        mat.use_nodes = True
        obj.data.materials.append(mat)
    else:
        mat = obj.data.materials[0]
        if not mat.use_nodes:
            mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Find principled BSDF
    principled = None
    for node in nodes:
        if node.type == 'BSDF_PRINCIPLED':
            principled = node
            break
    
    if not principled:
        principled = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Create vertex color node and connect to base color
    vc_node = nodes.new('ShaderNodeVertexColor')
    vc_node.layer_name = vertex_color_name
    links.new(vc_node.outputs['Color'], principled.inputs['Base Color'])
    
    # Create image texture node for baking target
    tex_node = nodes.new('ShaderNodeTexImage')
    tex_node.image = bake_image
    tex_node.select = True
    nodes.active = tex_node
    
    # Select object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # Configure bake settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'CPU'
    bpy.context.scene.cycles.samples = 1
    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_pass_color = True
    bpy.context.scene.render.bake.margin = 16
    
    # Bake
    print(f"  Baking vertex colors to {texture_size}x{texture_size} texture...")
    bpy.ops.object.bake(type='DIFFUSE')
    
    # Remove vertex color node, keep texture node connected
    nodes.remove(vc_node)
    links.new(tex_node.outputs['Color'], principled.inputs['Base Color'])
    
    print(f"  Bake complete for {obj.name}")
    return bake_image


def main():
    """Main conversion function"""
    # Get input and output paths from command line arguments
    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1:]
        if len(argv) < 2:
            print("Usage: blender --background --python export_usdz.py -- <input_glb> <output_usdz>")
            sys.exit(1)

        input_glb = argv[0]
        output_usdz = argv[1]
        job_id = argv[2] if len(argv) > 2 else 'test'
    else:
        print("Usage: blender --background --python export_usdz.py -- <input_glb> <output_usdz> <job_id>")
        sys.exit(1)

    # Validate input file exists
    if not os.path.exists(input_glb):
        print(f"Error: Input file does not exist: {input_glb}")
        sys.exit(1)

    print(f"Converting {input_glb} to USDZ...")
    
    # Clear scene
    clear_scene()

    # Import GLB file
    bpy.ops.import_scene.gltf(filepath=input_glb)
    print(f"Imported GLB: {input_glb}")

    # Process each mesh object - bake vertex colors to textures
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            mesh = obj.data
            
            # Check if mesh has vertex colors but no textures
            has_vertex_colors = len(mesh.color_attributes) > 0
            has_uv = len(mesh.uv_layers) > 0
            
            if has_vertex_colors:
                print(f"Processing mesh: {obj.name}")
                bake_vertex_colors_to_texture(obj)

    # Export as USDZ
    bpy.ops.wm.usd_export(
        filepath=output_usdz,
        export_materials=True,
        export_uvmaps=True,
        export_normals=True,
        use_instancing=True,
        evaluation_mode='RENDER'
    )

    print(f"Successfully exported {input_glb} to {output_usdz}")


if __name__ == '__main__':
    main()
