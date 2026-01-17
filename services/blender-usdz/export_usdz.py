#!/usr/bin/env python3
"""
Simple GLB to USDZ converter for Blender - exports GLB directly as USDZ
"""
import bpy
import sys
import os

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

    # Clear scene
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

    # Import GLB file
    bpy.ops.import_scene.gltf(filepath=input_glb)

    # Convert vertex colors to materials for USD export
    # Blender USD export doesn't support vertex colors, so we need to create materials
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH' and obj.data.vertex_colors:
            mesh = obj.data
            
            # Get the active vertex color layer
            if mesh.vertex_colors:
                vcol = mesh.vertex_colors.active
                
                # Create a new material
                mat = bpy.data.materials.new(name=f"{obj.name}_material")
                mat.use_nodes = True
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                
                # Get or create nodes
                bsdf = nodes.get("Principled BSDF")
                if not bsdf:
                    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
                
                output = nodes.get("Material Output")
                if not output:
                    output = nodes.new(type='ShaderNodeOutputMaterial')
                
                # Create attribute node for vertex colors
                attr_node = nodes.new(type='ShaderNodeAttribute')
                attr_node.attribute_name = vcol.name
                
                # Connect vertex color to principled BSDF base color
                links.new(attr_node.outputs['Color'], bsdf.inputs['Base Color'])
                links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
                
                # Assign material to the object
                if len(obj.material_slots) == 0:
                    obj.data.materials.append(mat)
                else:
                    obj.material_slots[0].material = mat

    # Export as USDZ - using default settings
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
