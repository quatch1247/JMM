<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>점심 메뉴 추천</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link href="${pageContext.request.contextPath}/css/styles.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="header d-flex justify-content-center mt-4">
            <button class="category-button" onclick="loadCategory('index', this)">
                <i class="bi bi-shuffle"></i>
            </button>
            <button class="category-button active" onclick="loadCategory('building', this)">
                <i class="bi bi-building"></i>
            </button>
            <button class="category-button" onclick="loadCategory('weather', this)">
                <i class="bi bi-cloud-sun"></i>
            </button>
        </div>
        <div class="menu-card">
            <div id="menuImageContainer" class="position-relative">
                <img id="menuImage" src="${pageContext.request.contextPath}/img/building_raccoon.png" alt="Gourmet Breakfast" class="menu-image">
                <div id="spinner" class="d-none position-absolute top-50 start-50 translate-middle">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </div>
            <div class="menu-content">
				<div id="businessName" class="price-tag">도렴빌딩 내 랜덤추천<br><br></div>
				<div id="menuDescription" class="menu-description">안녕하세요! 저는 도렴빌딩 건물안 식당을 랜덤으로 추천해드리는 라쿤입니다.<br><br>매일 어떤 맛집이 기다리고 있을지 궁금하신가요? 저와 함께 오늘의 점심을 즐겨보세요!<br><br><strong>주의:</strong> 메뉴와 가격은 매장 상황에 따라 변동될 수 있습니다.
				</div>
				<div id="html-content">
				</div>
            </div>
        </div>
        <div class="button-container">
            <button class="refresh-button" onclick="refreshBuildingMenu()">새로고침</button>
        </div>
    </div>
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Marked.js -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <!-- Custom JS -->
    <script src="${pageContext.request.contextPath}/js/scripts.js"></script>
</body>
</html>
