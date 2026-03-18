import bpy
import os

def render_stl_to_images(stl_filepath, output_dir):
    # Clear existing scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Import STL file
    bpy.ops.import_mesh.stl(filepath=stl_filepath)
    target = bpy.context.selected_objects[0]
    
    # Set origin to geometry
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    
    # Calculate camera position
    cam_x_pos = max([v[0] for v in target.bound_box]) * 2.5
    cam_y_pos = max([v[1] for v in target.bound_box]) * 2.5
    cam_z_pos = max([v[2] for v in target.bound_box]) * 2.5
    
    # Create rotation center
    rot_centre = bpy.data.objects.new('rot_centre', None)
    bpy.context.scene.collection.objects.link(rot_centre)
    rot_centre.location = target.location
    
    # Create camera
    camera = bpy.data.objects.new('camera', bpy.data.cameras.new('camera'))
    bpy.context.scene.collection.objects.link(camera)
    camera.location = (cam_x_pos, cam_y_pos, cam_z_pos)
    camera.parent = rot_centre
    m = camera.constraints.new('TRACK_TO')
    m.target = target
    m.track_axis = 'TRACK_NEGATIVE_Z'
    m.up_axis = 'UP_Y'
    
    # Set up rendering
    bpy.context.scene.camera = camera
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Render images
    for frame in range(1, 101):
        rot_centre.rotation_euler.z = radians((frame - 1) * 3.6)
        bpy.context.scene.render.filepath = os.path.join(output_dir, f'image_{frame:03d}.png')
        bpy.ops.render.render(write_still=True)

# Example usage
render_stl_to_images('path/to/your/file.stl', 'path/to/output/directory')




"""import bpy
scn = bpy.context.scene

bpy.ops.import_scene.obj(filepath='obj1.obj')
target = bpy.context.selected_objects[0]
scn.objects.active = target
# centring the origin gives a better bounding box and rotation point
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

cam_x_pos = max([v[0] for v in target.bound_box]) * 2.5
cam_y_pos = max([v[1] for v in target.bound_box]) * 2.5
cam_z_pos = max([v[2] for v in target.bound_box]) * 2.5

rot_centre = bpy.data.objects.new('rot_centre', None)
scn.objects.link(rot_centre)
rot_centre.location = target.location

camera = bpy.data.objects.new('camera', bpy.data.cameras.new('camera'))
scn.objects.link(camera)
camera.location = (cam_x_pos, cam_y_pos, cam_z_pos)
camera.parent = rot_centre
m = camera.constraints.new('TRACK_TO')
m.target = target
m.track_axis = 'TRACK_NEGATIVE_Z'
m.up_axis = 'UP_Y'

rot_centre.rotation_euler.z = 0.0
rot_centre.keyframe_insert('rotation_euler', index=2, frame=1)
rot_centre.rotation_euler.z = radians(360.0)
rot_centre.keyframe_insert('rotation_euler', index=2, frame=101)
# set linear interpolation for constant rotation speed
for c in rot_centre.animation_data.action.fcurves:
    for k in c.keyframe_points:
        k.interpolation = 'LINEAR'
scn.frame_end = 100
"""