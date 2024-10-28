import json
import os
import numpy as np

# 경로 설정 (이미지 폴더와 JSON 파일 저장 경로)
output_dir = "output_images"
camera_file = os.path.join(output_dir, "cameras.txt")
images_file = os.path.join(output_dir, "images.txt")

# 카메라 파라미터 정보 추출 함수 (COLMAP 형식으로 변환)
def save_colmap_files(output_dir, camera_file, images_file):
    # 카메라 정보 저장
    camera_id = 1
    camera_model = "PINHOLE"
    width, height = 1600, 900  # 이미지 해상도 (1600x900)

    # 카메라 파라미터 JSON 파일에서 읽어오기
    param_files = [f for f in os.listdir(output_dir) if f.endswith(".json")]
    param_files.sort()  # 파일 이름 기준으로 정렬
    
    # 카메라 텍스트 파일 작성
    with open(camera_file, 'w') as cam_f:
        cam_f.write("# Camera list with one line of data per camera:\n")
        cam_f.write("#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n")
        
        # 첫 번째 JSON 파일을 읽어 내부 파라미터 추출
        with open(os.path.join(output_dir, param_files[0]), 'r') as f:
            camera_params = json.load(f)
            intrinsic = camera_params["intrinsic"]
            intrinsic_matrix = np.array(intrinsic["intrinsic_matrix"]).reshape(3, 3, order='F')  # 3x3 행렬로 재구성

            # 내부 파라미터 (fx, fy, cx, cy) 추출
            fx = intrinsic_matrix[0, 0]
            fy = intrinsic_matrix[1, 1]
            cx = intrinsic_matrix[0, 2]
            cy = intrinsic_matrix[1, 2]
            params = f"{fx} {fy} {cx} {cy}"

            cam_f.write(f"{camera_id} {camera_model} {width} {height} {params}\n")

    # 이미지 정보 저장
    with open(images_file, 'w') as img_f:
        img_f.write("# Image list with two lines of data per image:\n")
        img_f.write("#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, IMAGE_NAME\n")
        img_f.write("#   POINTS2D[] as (X, Y, POINT3D_ID)\n")
        
        for idx, param_file in enumerate(param_files):
            image_id = idx + 1
            image_name = f"{idx:03d}.png"
            
            with open(os.path.join(output_dir, param_file), 'r') as f:
                camera_params = json.load(f)
                extrinsic = np.array(camera_params["extrinsic"]).reshape(4, 4, order='F')  # 4x4 행렬로 재구성
                
                # Translation (TX, TY, TZ)
                T = extrinsic[:3, 3]
                tx, ty, tz = T[0], T[1], T[2]
                
                # Rotation (R -> Quaternion)
                R = extrinsic[:3, :3]
                qw, qx, qy, qz = rotation_matrix_to_quaternion(R)
                
                # 이미지 정보 저장
                img_f.write(f"{image_id} {qw} {qx} {qy} {qz} {tx} {ty} {tz} {camera_id} {image_name}\n")
                img_f.write("\n")  # POINTS2D는 생략 가능

# Rotation Matrix -> Quaternion 변환 함수
def rotation_matrix_to_quaternion(R):
    q = np.empty((4,))
    trace = np.trace(R)
    
    if trace > 0.0:
        s = np.sqrt(trace + 1.0) * 2
        q[0] = 0.25 * s
        q[1] = (R[2, 1] - R[1, 2]) / s
        q[2] = (R[0, 2] - R[2, 0]) / s
        q[3] = (R[1, 0] - R[0, 1]) / s
    else:
        if (R[0, 0] > R[1, 1]) and (R[0, 0] > R[2, 2]):
            s = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2
            q[0] = (R[2, 1] - R[1, 2]) / s
            q[1] = 0.25 * s
            q[2] = (R[0, 1] + R[1, 0]) / s
            q[3] = (R[0, 2] + R[2, 0]) / s
        elif R[1, 1] > R[2, 2]:
            s = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2
            q[0] = (R[0, 2] - R[2, 0]) / s
            q[1] = (R[0, 1] + R[1, 0]) / s
            q[2] = 0.25 * s
            q[3] = (R[1, 2] + R[2, 1]) / s
        else:
            s = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2
            q[0] = (R[1, 0] - R[0, 1]) / s
            q[1] = (R[0, 2] + R[2, 0]) / s
            q[2] = (R[1, 2] + R[2, 1]) / s
            q[3] = 0.25 * s
    return q

# 변환 및 저장 실행
save_colmap_files(output_dir, camera_file, images_file)
