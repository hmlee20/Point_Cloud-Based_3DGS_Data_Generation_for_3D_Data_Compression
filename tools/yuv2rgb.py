import numpy as np
from plyfile import PlyData, PlyElement

def yuv_to_rgb(yuv):
    """
    Convert a single YUV value or array of YUV values to RGB.
    
    Args:
        yuv (numpy array): Array of YUV values of shape (N, 3).
        
    Returns:
        rgb (numpy array): Array of RGB values of shape (N, 3).
    """
    Y = yuv[:, 0]
    U = yuv[:, 1]
    V = yuv[:, 2]

    R = Y + 1.403 * V
    G = Y - 0.344 * U - 0.714 * V
    B = Y + 1.770 * U

    rgb = np.stack((R, G, B), axis=1)
    return rgb

def modify_ply_yuv_to_rgb(input_ply, output_ply):
    """
    Modify the YUV coefficients in the PLY file back to RGB coefficients,
    restoring the 45 AC component fields in the header with RGB values.
    
    Args:
        input_ply (str): Path to the input PLY file to be modified.
        output_ply (str): Path to the output PLY file to save the modified content.
    """
    plydata = PlyData.read(input_ply)
    vertex_data = plydata['vertex'].data

    # Convert YUV DC to RGB DC
    yuv_dc = np.stack((vertex_data['f_dc_0'],
                       vertex_data['f_dc_1'],
                       vertex_data['f_dc_2']), axis=1)
    rgb_dc = yuv_to_rgb(yuv_dc)

    # Prepare the new vertex data dictionary in the required order
    new_vertex_data = {}

    # Add spatial and normal properties first
    for name in ['x', 'y', 'z', 'nx', 'ny', 'nz']:
        new_vertex_data[name] = vertex_data[name]

    # Add DC components converted to RGB
    new_vertex_data['f_dc_0'] = rgb_dc[:, 0]  # R component
    new_vertex_data['f_dc_1'] = rgb_dc[:, 1]  # G component
    new_vertex_data['f_dc_2'] = rgb_dc[:, 2]  # B component

    # Restore 45 AC fields with RGB data, setting U and V to 0 if missing
    num_ac_fields = 45
    for i in range(0, num_ac_fields, 3):
        y_component = vertex_data[f'f_rest_{i}'] if f'f_rest_{i}' in vertex_data.dtype.names else np.zeros(len(vertex_data))
        u_component = np.zeros_like(y_component)
        v_component = np.zeros_like(y_component)
        
        yuv_ac = np.stack((y_component, u_component, v_component), axis=1)
        rgb_ac = yuv_to_rgb(yuv_ac)

        new_vertex_data[f'f_rest_{i}'] = rgb_ac[:, 0]  # R component
        new_vertex_data[f'f_rest_{i+1}'] = rgb_ac[:, 1]  # G component
        new_vertex_data[f'f_rest_{i+2}'] = rgb_ac[:, 2]  # B component

    # Add other fields at the end in the specified order
    for name in ['opacity', 'scale_0', 'scale_1', 'scale_2', 'rot_0', 'rot_1', 'rot_2', 'rot_3']:
        new_vertex_data[name] = vertex_data[name]

    # Define new vertex array with required dtype in specified order
    vertex_dtype = [(name, np.float32) for name in new_vertex_data]
    new_vertex_array = np.zeros(len(vertex_data), dtype=vertex_dtype)

    # Fill the new vertex array with data
    for name in new_vertex_data:
        new_vertex_array[name] = new_vertex_data[name]

    # Create a new PlyElement with the updated vertex data
    new_vertex_element = PlyElement.describe(new_vertex_array, 'vertex')

    # Convert tuple to list and write to file
    elements = [new_vertex_element] + list(plydata.elements[1:])

    # Write the modified PLY data back to a new file
    with open(output_ply, 'wb') as f:
        PlyData(elements).write(f)

# Example usage
modify_ply_yuv_to_rgb('point_cloud_yuv.ply', 'point_cloud_rgb.ply')
