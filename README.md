## 프로젝트 개요
도렴빌딩 주변 점심 메뉴를 랜덤, 건물 내, 날씨 기반으로 추천하는 웹 애플리케이션입니다.

## 프로젝트 데모
### 첫번째: 어플 실행 및 랜덤 추천
https://github.com/user-attachments/assets/c0aed8c1-91fc-4d85-b3f8-7fd9e5f26db2

### 두번째: 랜덤 추천 모드에서 상세보기
https://github.com/user-attachments/assets/3ec40434-8085-429c-8f14-bf0b99acf993

### 세번째: 회사 건물 내 랜덤 식당 추천
https://github.com/user-attachments/assets/0732f59b-d57d-4bb0-9a71-7f1aa520b429

### 네번째: 날씨 기반 식당 추천
https://github.com/user-attachments/assets/21a9d0d4-04b0-4ee7-ab4e-299d736f0b77

## 사용 기술
- **이클립스 IDE**: JSP를 이용한 서버 사이드 렌더링
- **Bootstrap**: UI 디자인
- **JavaScript**: 동적 콘텐츠 로딩 및 사용자 인터랙션 처리
- **FastAPI**: 백엔드 API 서버
- **Docker**: 컨테이너화 및 배포
- **AWS**: ECR, ECS, RDS를 이용한 배포 및 데이터베이스 관리
- **Swing2App**: 웹사이트를 모바일 앱으로 변환

## 주요 기능
- **카테고리 선택**: 사용자가 세 가지 카테고리 중 하나를 선택하여 다른 추천 방식으로 메뉴를 확인할 수 있습니다.
- **메뉴 추천**: 각 카테고리 페이지에서 서버로부터 데이터를 받아와 메뉴를 추천하고, 새로고침 기능을 통해 다른 메뉴를 확인할 수 있습니다.
- **화면 크기 대응**: 반응형 디자인을 적용하여 다양한 화면 크기에서 적절한 UI를 제공합니다.

## 기능 구현

### 프론트엔드 (JSP)
- **랜덤 메뉴 추천 페이지** : 랜덤으로 점심 메뉴를 추천합니다.
- **날씨 기반 메뉴 추천 페이지** : 날씨를 기반으로 메뉴를 추천합니다.
- **건물 내 메뉴 추천 페이지** : 특정 건물 내 식당을 랜덤으로 추천합니다.

### 백엔드 (FastAPI)
- **랜덤 메뉴 추천 API** (`/recommendation/random-recommendation`): 랜덤으로 점심 메뉴와 해당 메뉴를 제공하는 식당을 추천합니다.
- **건물 내 랜덤 메뉴 추천 API** (`/recommendation/random-recommendation-is-in-building`): 특정 건물 내에서 랜덤으로 점심 메뉴와 해당 메뉴를 제공하는 식당을 추천합니다.
- **날씨 기반 메뉴 추천 API** (`/recommendation/recommendation_based_on_weather`): 현재 날씨를 기반으로 점심 메뉴를 추천합니다.

### 스크립트 (`scripts.js`)
- **화면 크기 조절**: `adjustCardWidth` 함수로 화면 크기에 따라 메뉴 카드의 크기를 조절합니다.
- **랜덤 메뉴 새로고침**: `refreshRandomMenu` 함수로 서버에서 랜덤 메뉴를 불러와 화면에 표시합니다.
- **건물 내 메뉴 새로고침**: `refreshBuildingMenu` 함수로 도렴빌딩 내 식당 중 하나를 랜덤으로 불러와 화면에 표시합니다.
- **날씨 기반 메뉴 새로고침**: `refreshWeatherBasedMenu` 함수로 현재 날씨에 맞는 메뉴를 서버에서 불러와 화면에 표시합니다.
- **카테고리 로드 기능**: `loadCategory` 함수로 다른 카테고리 페이지로 이동하며, 선택한 버튼을 활성화 상태로 표시합니다.
- **초기 레이아웃 조정**: 페이지 로드 시 `adjustCardWidth` 함수를 호출하여 초기 레이아웃을 설정합니다.

## Docker 구성
### FastAPI 애플리케이션
- **Docker Compose**: FastAPI 애플리케이션을 정의하고, 포트 매핑을 설정하였습니다.
- **Dockerfile**: Python 3.11 이미지를 기반으로 의존성을 설치하고 애플리케이션을 복사하여 Uvicorn 서버를 시작합니다.

### 프론트엔드 Tomcat 서버
- **Dockerfile**: Tomcat 9.0 이미지를 기반으로 WAR 파일을 복사하고, 포트를 노출하여 Tomcat 서버를 시작합니다.

### Docker 멀티 플랫폼 이미지 빌드 및 AWS ECR 업로드
```bash
# Buildx 생성 및 사용
docker buildx create --use

# Buildx 초기화
docker buildx inspect --bootstrap

# 멀티 플랫폼 빌드
docker buildx build --platform linux/amd64,linux/arm64 -t [이미지명] .

```
### Docker 이미지 빌드 및 AWS ECR 업로드
- **AWS ECR 업로드**: 도커 이미지를 빌드하고 AWS ECR에 업로드하여 다양한 플랫폼에서 사용할 수 있도록 설정하였습니다.

### 배포 및 데이터베이스 마이그레이션
- **ECS Fargate 배포**: ECR에 업로드된 이미지를 사용하여 AWS ECS Fargate에 배포하여 외부 접근이 가능하도록 설정했습니다.
- **데이터베이스 마이그레이션**: 로컬에서 사용하던 MySQL 데이터베이스를 AWS RDS로 이전하였고, FastAPI 애플리케이션에서 RDS 데이터베이스와 연결하여 데이터를 관리합니다.

## Swing2App
웹뷰(WebView)를 이용하여 웹사이트를 모바일 앱으로 변환할 수 있는 기능을 제공합니다. 나는 스윙투앱으로 띄워놓은 서버를 APK로 빌드했습니다.

### 주요 특징
1. **웹뷰 앱 제작**:
    - 스윙투앱에서는 사용자가 지정한 웹사이트 URL을 입력하면 해당 사이트를 표시하는 웹뷰 앱을 생성할 수 있습니다. 이를 통해 네이티브 앱처럼 작동하는 모바일 앱을 쉽게 만들 수 있습니다.

### Docker 이미지 빌드 및 AWS ECR 업로드
- **AWS ECR 업로드**: 도커 이미지를 빌드하고 AWS ECR에 업로드하여 다양한 플랫폼에서 사용할 수 있도록 설정하였습니다.

### 배포 및 데이터베이스 마이그레이션
- **ECS Fargate 배포**: ECR에 업로드된 이미지를 사용하여 AWS ECS Fargate에 배포하여 외부 접근이 가능하도록 설정했습니다.
- **데이터베이스 마이그레이션**: 로컬에서 사용하던 MySQL 데이터베이스를 AWS RDS로 이전하였고, FastAPI 애플리케이션에서 RDS 데이터베이스와 연결하여 데이터를 관리합니다.

## Swing2App
웹뷰(WebView)를 이용하여 웹사이트를 모바일 앱으로 변환할 수 있는 기능을 제공합니다. 나는 스윙투앱으로 띄워놓은 서버를 APK로 빌드했습니다.

**웹뷰 앱 제작**:
    - 스윙투앱에서 지정한 웹사이트 URL을 입력하여 해당 사이트를 표시하는 웹뷰 앱을 생성하였습니다.
