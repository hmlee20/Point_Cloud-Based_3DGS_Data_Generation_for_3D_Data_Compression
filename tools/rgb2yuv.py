import numpy as np
from plyfile import PlyData, PlyElement

def rgb_to_yuv(rgb):
    """
    Convert a single RGB value or array of RGB values to YUV.
    
    Args:
        rgb (numpy array): Array of RGB values of shape (N, 3).
        
    Returns:
        yuv (numpy array): Array of YUV values of shape (N, 3).
    """
    R = rgb[:, 0]
    G = rgb[:, 1]
    B = rgb[:, 2]

    Y = 0.299 * R + 0.587 * G + 0.114 * B
    U = (B - Y) * 0.565
    V = (R - Y) * 0.713

    yuv = np.stack((Y, U, V), axis=1)
    return yuv

def modify_ply_rgb_to_yuv_remove_ac(input_ply, output_ply):
    """
    Modify the RGB coefficients (both DC and AC) in the PLY file to YUV coefficients,
    and remove the U and V AC components from the header and data.
    
    Args:
        input_ply (str): Path to the input PLY file to be modified.
        output_ply (str): Path to the output PLY file to save the modified content.
    """
    plydata = PlyData.read(input_ply)
    vertex_data = plydata['vertex'].data

    # Convert RGB DC coefficients to YUV
    rgb_dc = np.stack((vertex_data['f_dc_0'],
                       vertex_data['f_dc_1'],
                       vertex_data['f_dc_2']), axis=1)
    yuv_dc = rgb_to_yuv(rgb_dc)

    # Update DC components in vertex_data
    new_vertex_data = {}
    new_vertex_data['f_dc_0'] = yuv_dc[:, 0]  # Y component
    new_vertex_data['f_dc_1'] = yuv_dc[:, 1]  # U component
    new_vertex_data['f_dc_2'] = yuv_dc[:, 2]  # V component

    # Keep spatial and normal properties first
    for name in ['x', 'y', 'z', 'nx', 'ny', 'nz']:
        new_vertex_data[name] = vertex_data[name]

    # Add other fields except U, V components in AC fields
    for name in vertex_data.dtype.names:
        if name not in new_vertex_data and not name.startswith('f_rest_'):
            new_vertex_data[name] = vertex_data[name]

    # Process and keep only the Y component for each AC field
    num_ac_fields = 45
    for i in range(0, num_ac_fields, 3):
        rgb_ac = np.stack((vertex_data[f'f_rest_{i}'],
                           vertex_data[f'f_rest_{i+1}'],
                           vertex_data[f'f_rest_{i+2}']), axis=1)
        yuv_ac = rgb_to_yuv(rgb_ac)
        new_vertex_data[f'f_rest_{i}'] = yuv_ac[:, 0]  # Y component only

    # Define the new structure with the required field order
    vertex_dtype = [(name, vertex_data[name].dtype) for name in ['x', 'y', 'z', 'nx', 'ny', 'nz', 'f_dc_0', 'f_dc_1', 'f_dc_2'] + [f'f_rest_{i}' for i in range(0, num_ac_fields, 3)]]
    for name in new_vertex_data:
        if name not in ['x', 'y', 'z', 'nx', 'ny', 'nz', 'f_dc_0', 'f_dc_1', 'f_dc_2'] + [f'f_rest_{i}' for i in range(0, num_ac_fields, 3)]:
            vertex_dtype.append((name, vertex_data[name].dtype))

    # Create new vertex array with reordered fields
    new_vertex_array = np.zeros(len(vertex_data), dtype=vertex_dtype)
    for name in new_vertex_data:
        new_vertex_array[name] = new_vertex_data[name]

    # Write the modified PLY file with updated element order
    new_vertex_element = PlyElement.describe(new_vertex_array, 'vertex')
    elements = list(plydata.elements[1:])  # Keep other elements if they exist
    elements.insert(0, new_vertex_element)

    PlyData(elements, text=False).write(output_ply)

# Example usage
modify_ply_rgb_to_yuv_remove_ac('point_cloud.ply', 'point_cloud_yuv.ply')
