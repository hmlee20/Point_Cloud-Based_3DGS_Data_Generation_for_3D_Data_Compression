import os
import numpy as np
from plyfile import PlyData

def fetchPly(path):
    """Read PLY file and return xyz and rgb data."""
    ply_data = PlyData.read(path)
    vertex = ply_data['vertex']
    xyz = np.vstack([vertex['x'], vertex['y'], vertex['z']]).T
    rgb = np.vstack([vertex['red'], vertex['green'], vertex['blue']]).T
    return xyz, rgb

def write_points3D_text(path, xyz, rgb, errors=None):
    """
    Writes the 3D points to a text file in the specified format.
    
    Parameters:
    - path: The path to save the text file.
    - xyz: A NumPy array of shape (N, 3) containing the 3D coordinates.
    - rgb: A NumPy array of shape (N, 3) containing the RGB colors.
    - errors: (Optional) A NumPy array of shape (N,) containing the reprojection errors.
    """
    with open(path, "w") as f:
        # Write the header
        f.write("# 3D point list with one line of data per point:\n")
        f.write("#   POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)\n")
        f.write(f"# Number of points: {xyz.shape[0]}, mean track length: N/A\n")  # Placeholder for track length

        for i in range(xyz.shape[0]):
            # Format: POINT3D_ID, X, Y, Z, R, G, B, ERROR
            # Here we assume POINT3D_ID is simply the index
            point3D_id = i + 1
            point_data = f"{point3D_id} {xyz[i, 0]} {xyz[i, 1]} {xyz[i, 2]} {rgb[i, 0]} {rgb[i, 1]} {rgb[i, 2]} 0"
            f.write(point_data + "\n")

# PLY 파일에서 데이터를 읽어와서 텍스트 파일로 저장
path = "./"
ply_path = os.path.join(path, "sparse_point_cloud.ply")
txt_path = os.path.join(path, "points3D.txt")

# PLY 파일에서 xyz와 rgb 읽기
xyz, rgb = fetchPly(ply_path)

# 텍스트 파일로 저장
write_points3D_text(txt_path, xyz, rgb)