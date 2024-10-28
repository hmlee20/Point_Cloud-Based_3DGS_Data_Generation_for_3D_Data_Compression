import numpy as np
import open3d as o3d

# Morton Code (Z-order curve) 계산 함수
def morton_encode(x, y, z, bits=10):
    def spread_bits(v):
        v = (v | (v << 16)) & 0x030000FF
        v = (v | (v << 8)) & 0x0300F00F
        v = (v | (v << 4)) & 0x030C30C3
        v = (v | (v << 2)) & 0x09249249
        return v
    
    x = spread_bits(x)
    y = spread_bits(y)
    z = spread_bits(z)
    return (x << 2) | (y << 1) | z

# 포인트 클라우드에서 Morton Code를 기반으로 정확히 num_points만큼 subsampling
def subsample_point_cloud_with_normals_and_rgb(point_cloud, num_points):
    # 포인트 클라우드의 좌표, 색상, 법선 벡터를 가져옴
    points = np.asarray(point_cloud.points)
    colors = np.asarray(point_cloud.colors)
    
    # 법선 정보가 있는지 확인
    has_normals = point_cloud.has_normals()
    
    if has_normals:
        normals = np.asarray(point_cloud.normals)
    
    # 좌표를 0-1 범위로 정규화
    min_bound = np.min(points, axis=0)
    max_bound = np.max(points, axis=0)
    normalized_points = (points - min_bound) / (max_bound - min_bound)

    # 정규화된 좌표를 bits 범위 안의 Morton Code로 변환 (bits=10이면 1024x1024x1024의 공간으로 매핑)
    morton_codes = [morton_encode(int(p[0] * 1024), int(p[1] * 1024), int(p[2] * 1024)) for p in normalized_points]

    # Morton Code로 정렬
    sorted_indices = np.argsort(morton_codes)
    sorted_points = points[sorted_indices]
    sorted_colors = colors[sorted_indices]
    if has_normals:
        sorted_normals = normals[sorted_indices]

    # 정확히 num_points 개수를 샘플링
    step = len(points) // num_points
    sampled_indices = sorted_indices[:num_points] if step == 0 else sorted_indices[::step][:num_points]

    sampled_points = points[sampled_indices]
    sampled_colors = colors[sampled_indices]
    if has_normals:
        sampled_normals = normals[sampled_indices]

    # subsampled 포인트 클라우드 생성
    sampled_pcd = o3d.geometry.PointCloud()
    sampled_pcd.points = o3d.utility.Vector3dVector(sampled_points)
    sampled_pcd.colors = o3d.utility.Vector3dVector(sampled_colors)
    if has_normals:
        sampled_pcd.normals = o3d.utility.Vector3dVector(sampled_normals)

    return sampled_pcd

# PLY 파일 로드
dense_ply_path = "./soldier_vox10_0690.ply"  # 여기에 원본 PLY 파일 경로 입력
dense_pcd = o3d.io.read_point_cloud(dense_ply_path)

# subsample할 포인트 개수 설정
num_sampled_points = 15000  # 원하는 포인트 개수 설정

# subsampling 수행 (RGB, 법선 벡터 포함)
sparse_pcd_with_normals_and_rgb = subsample_point_cloud_with_normals_and_rgb(dense_pcd, num_sampled_points)

# subsampled 결과 저장 (RGB, 법선 벡터 포함)
sparse_ply_path_with_normals_and_rgb = "./sparse_point_cloud.ply"  # 결과 PLY 파일 경로
o3d.io.write_point_cloud(sparse_ply_path_with_normals_and_rgb, sparse_pcd_with_normals_and_rgb)

print(f"Subsampled point cloud with normals and RGB saved to {sparse_ply_path_with_normals_and_rgb}")
