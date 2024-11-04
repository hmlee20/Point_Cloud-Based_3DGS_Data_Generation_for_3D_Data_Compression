# Point Cloud-Based 3DGS Data Generation for 3D Data Compression

광운대학교 컴퓨터정보공학부 이혜미, 송유리, 황정원

이 프로젝트는 [3D Gaussian Splatting (3DGS)](https://github.com/graphdeco-inria/gaussian-splatting) 오픈소스를 기반으로 하여 SfM(Sparse from Motion) 과정을 생략하고 point cloud에서 직접 이미지와 카메라 파라미터를 추출하는 방식 및 배경 제거와 데이터 압축 기능을 추가하여 개발되었습니다.

본 저장소의 코드를 사용하기 위해서는 먼저 3DGS 오픈소스를 다운로드해야 하며, 이후 아래의 절차에 따라 코드를 설정하고 실행할 수 있습니다.

## 1. 3DGS 오픈소스 다운로드 및 수정

우선 [3D Gaussian Splatting (3DGS)](https://github.com/graphdeco-inria/gaussian-splatting)를 클론하여 다운로드합니다.

다운로드한 3DGS 코드에서 **다음 파일들과 폴더들을 본 저장소의 수정된 버전으로 대체**해야 합니다.

- `scene/` 폴더 및 `utils/` 폴더: 본 저장소의 `gaussian-splatting/scene`과 `gaussian-splatting/utils` 폴더로 덮어씌우기

- `metrics.py`, `render.py`, `train.py`: 본 저장소의 `gaussian-splatting` 폴더에 있는 파일로 대체

위 작업을 통해 기존 3DGS 코드에 커스텀 기능들이 적용됩니다.

## 2. 입력 데이터 준비

본 프로젝트는 SfM 과정을 생략하고 기존 point cloud 데이터로부터 직접 입력 데이터를 구성합니다.

다음과 같은 폴더 구조를 만들어야 합니다.

```plaintext

input_data/
├── occupancy_map/
│   └── occupancy_map.txt
└── train/
    ├── images/
    └── sparse/
        └── 0/
            ├── cameras.txt
            ├── images.txt
            └── points3D.txt

```

### (1) Point Cloud 이미지 렌더링, Occupancy Map 생성

- **`render_pointcloud.py`** (위치: `tools/`): dense한 point cloud를 입력하여 원하는 수의 이미지를 렌더링할 수 있습니다. 렌더링된 이미지는 `images/` 폴더에 저장합니다. 이 과정에서는 카메라 위치를 다르게 하여 다양한 각도의 이미지를 생성할 수 있습니다.
추가적으로 point cloud의 depth map을 사용하여 생성된 `occupancy_map.txt`를 `occupancy_map/` 폴더에 저장합니다.

### (2) 카메라 파라미터 파일 생성

- **`json2txt.py`** (위치: `tools/`): JSON 형식으로 저장된 카메라 파라미터 파일을 텍스트 파일인 `cameras.txt`로 변환하여 `sparse/0/` 폴더에 저장합니다. 이 파일은 각 이미지에 대한 카메라 위치와 방향 정보를 포함합니다.

### (3) Sparse Point Cloud 생성

- **`subsampling.py`** (위치: `tools/`): 초기의 dense한 point cloud를 입력하여 sub-sampling을 통해 sparse point cloud를 생성할 수 있습니다. 이를 통해 point 개수를 줄이고 필요한 정보만 남길 수 있습니다.

### (4) Point Cloud 파일 변환

- **`ply2txt.py`** (위치: `tools/`): 생성된 sparse point cloud의 `.ply` 파일을 `.txt` 형식으로 변환하여 `sparse/0/` 폴더에 `points3D.txt` 파일로 저장합니다. 이 파일은 3D point 위치 정보를 텍스트 형식으로 제공합니다.

## 3. 3DGS 실행

데이터 준비가 완료되면 기존 3DGS 오픈소스를 사용하는 방식과 유사하게 진행할 수 있습니다. 단, 본 프로젝트에서는 COLMAP을 사용하지 않으므로 `<path to COLMAP or NERF Synthetic dataset>` 경로 대신 `train/` 폴더 경로를 입력해야 합니다.

### 실행 절차

1. **Training**: `train.py` 를 통해 학습을 진행합니다.

2. **Rendering**: `render.py` 를 통해 이미지를 렌더링합니다.

3. **Evaluation**: `metrics.py` 를 통해 렌더링 결과의 PSNR을 측정할 수 있습니다.

자세한 실행 방법은 3DGS 오픈소스의 README를 참고하세요.
