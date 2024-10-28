import open3d as o3d
import numpy as np
import os

# 포인트 클라우드 로드
pcd = o3d.io.read_point_cloud("./soldier_vox10_0690.ply")

# 저장할 디렉토리 설정
output_dir = "output_images"
os.makedirs(output_dir, exist_ok=True)

# 시각화 창 생성 및 포인트 클라우드 추가
vis = o3d.visualization.Visualizer()
vis.create_window(visible=False, width=1600, height=900)  # 창을 띄우지 않고 1600x900 해상도로 설정
vis.add_geometry(pcd)

# 렌더링 옵션 설정
opt = vis.get_render_option()
opt.background_color = np.asarray([1, 1, 1])
opt.light_on = True  # 조명 효과 켜기
opt.point_size = 2
opt.mesh_color_option = o3d.visualization.MeshColorOption.Color
opt.show_coordinate_frame = True  # 좌표축 프레임 표시

# 카메라 파라미터 제어
ctr = vis.get_view_control()

# 이미지 저장을 위한 설정
def capture_image_and_save(vis, depth_txt_file, idx):
    # 장면 렌더링 및 이미지 캡처
    vis.poll_events()
    vis.update_renderer()
    image = vis.capture_screen_float_buffer(do_render=True)

    # 이미지 저장
    image_o3d = o3d.geometry.Image((np.asarray(image) * 255).astype(np.uint8))
    image_filename = os.path.join(output_dir, f"{idx:03d}.png")
    o3d.io.write_image(image_filename, image_o3d, 9)
    
    # Depth map 캡처
    depth = vis.capture_depth_float_buffer(do_render=True)
    depth_map = (np.asarray(depth) * 1000).astype(np.uint16)  # 밀리미터 단위로 변환하여 16-bit로 저장

    # Depth map에서 0은 그대로 두고 나머지는 1로 변경
    depth_map_binary = np.where(depth_map > 0, 1, 0).astype(np.uint8)

    # Depth map을 1차원 배열로 변환
    depth_map_binary_flat = depth_map_binary.flatten()
    
    # 이미지 id를 depth map의 첫 번째 값으로 추가하여 텍스트 파일에 저장 (1부터 시작)
    depth_map_with_id = np.concatenate(([idx + 1], depth_map_binary_flat))  # id는 1부터 시작
    np.savetxt(depth_txt_file, [depth_map_with_id], fmt='%d', delimiter=' ', newline='\n')

    # 카메라 파라미터 저장
    params = ctr.convert_to_pinhole_camera_parameters()
    param_filename = os.path.join(output_dir, f"{idx:03d}.json")
    o3d.io.write_pinhole_camera_parameters(param_filename, params)

    print(f"Saved image, binary depth map, and camera parameters for frame {idx}")
    
# Depth map 값을 저장할 텍스트 파일 생성
depth_txt_filename = os.path.join(output_dir, "occupancy_map.txt")
with open(depth_txt_filename, 'w') as depth_txt_file:
    # 각 설정에 따라 이미지 캡처
    num_images = 200

    for image_idx in range(num_images):
        # 무작위로 위도와 경도 각도 생성
        latitude = np.random.uniform(-90, 90)    # 위도는 -90도에서 90도 사이
        longitude = np.random.uniform(0, 360)    # 경도는 0도에서 360도 사이

        # 위도를 먼저 설정
        ctr.rotate(0, latitude)  # 수직(위도) 회전

        # 그 위도에서 경도를 추가 회전
        ctr.rotate(longitude, 0)  # 수평(경도) 회전

        # 이미지 및 파라미터 저장, 그리고 depth map을 텍스트 파일에 기록
        capture_image_and_save(vis, depth_txt_file, image_idx)

# 시각화 창 닫기
vis.destroy_window()

print(f"{num_images} images and their camera parameters have been saved to '{output_dir}'.")