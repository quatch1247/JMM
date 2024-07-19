window.addEventListener('resize', adjustCardWidth);

function adjustCardWidth() {
    const width = window.innerWidth;
    const menuCards = document.querySelectorAll('.menu-card');
    menuCards.forEach(card => {
        if (width < 768) {
            card.style.width = '90%'; // 작은 화면에서는 카드의 폭을 90%로 설정
            card.style.minHeight = '300px'; // 작은 화면에서 카드의 최소 높이 조정
        } else {
            card.style.width = '100%'; // 큰 화면에서는 카드의 폭을 100%로 설정
            card.style.maxWidth = '600px'; // 최대 폭은 600px로 설정
            card.style.minHeight = '400px'; // 큰 화면에서 카드의 최소 높이 조정
        }
    });
}

function refreshRandomMenu() {
    const url = 'http://54.180.130.143:8000/recommendation/random-recommendation'; // URL을 확인하세요
    const spinner = document.getElementById('spinner');
    const menuImage = document.getElementById('menuImage');
    const businessNameElement = document.getElementById('businessName');
    const menuDescriptionElement = document.getElementById('menuDescription');
    const htmlContentElement = document.getElementById('html-content');
    const refreshButton = document.querySelector('.refresh-button');
    const menuContentElement = document.querySelector('.menu-content'); // menu-content 요소 선택

    // 버튼 비활성화
    refreshButton.disabled = true;

    // 데이터 로드 전 초기 상태 설정
    businessNameElement.innerHTML = '잠시 기다려 주세요..<br><br>&nbsp;<br>&nbsp;<br>';
    menuDescriptionElement.innerHTML = '&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>';
    htmlContentElement.innerHTML = '';

    spinner.classList.remove('d-none');
    menuImage.style.opacity = '0.5';

    // 데이터 초기화 시 스크롤 위치를 맨 위로 이동
    menuContentElement.scrollTop = 0;

    fetch(url)
        .then(response => {
            console.log('Response status:', response.status); // 응답 상태를 로그로 출력
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // JSON 형식으로 응답을 처리합니다.
        })
        .then(data => {
            console.log('Fetched data:', data); // 데이터를 로그로 출력

            // JSON 데이터에서 필요한 정보를 추출합니다.
            let businessName = data.business_name;
            let aiSummarize = data.ai_summarize;
            let imageData = data.image_data;

            // 데이터가 올바르게 존재하는지 확인합니다.
            if (!businessName || !aiSummarize || !imageData) {
                throw new Error('Required data not found in the fetched JSON');
            }

            // 데이터를 HTML 요소에 반영합니다.
            businessNameElement.textContent = businessName;
            menuDescriptionElement.innerHTML = '<br>' + marked.parse(aiSummarize);
            // menuDescriptionElement.innerHTML = aiSummarize;
            menuImage.src = imageData.replace('![image](', '').replace(')', '');

            // 이미지 로드 완료 후 스피너 숨기기 및 이미지 표시
            menuImage.onload = function() {
                spinner.classList.add('d-none');
                menuImage.style.opacity = '1';
                // 버튼 활성화
                refreshButton.disabled = false;
                // menu-content 스크롤 위치를 맨 위로 이동
                menuContentElement.scrollTop = 0;
            };
        })
        .catch(error => {
            console.error('Error fetching menu:', error);
            alert('메뉴 데이터를 불러오는 중 오류가 발생했습니다.');
            // 오류 발생 시 스피너 숨기기
            spinner.classList.add('d-none');
            menuImage.style.opacity = '1';
            // 버튼 활성화
            refreshButton.disabled = false;
        });
}

function refreshBuildingMenu() {
    const url = 'http://54.180.130.143:8000/recommendation/random-recommendation-is-in-building'; // URL을 확인하세요
    const spinner = document.getElementById('spinner');
    const menuImage = document.getElementById('menuImage');
    const businessNameElement = document.getElementById('businessName');
    const menuDescriptionElement = document.getElementById('menuDescription');
    const htmlContentElement = document.getElementById('html-content');
    const refreshButton = document.querySelector('.refresh-button');
    const menuContentElement = document.querySelector('.menu-content'); // menu-content 요소 선택

    // 버튼 비활성화
    refreshButton.disabled = true;

    // 데이터 로드 전 초기 상태 설정
    businessNameElement.innerHTML = '잠시 기다려 주세요..<br><br>&nbsp;<br>&nbsp;<br>';
    menuDescriptionElement.innerHTML = '&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>';
    htmlContentElement.innerHTML = '';

    spinner.classList.remove('d-none');
    menuImage.style.opacity = '0.5';

    // 데이터 초기화 시 스크롤 위치를 맨 위로 이동
    menuContentElement.scrollTop = 0;

    fetch(url)
        .then(response => {
            console.log('Response status:', response.status); // 응답 상태를 로그로 출력
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // JSON 형식으로 응답을 처리합니다.
        })
        .then(data => {
            console.log('Fetched data:', data); // 데이터를 로그로 출력

            // JSON 데이터에서 필요한 정보를 추출합니다.
            let businessName = data.business_name;
            let aiSummarize = data.ai_summarize;
            let imageData = data.image_data;

            // 데이터가 올바르게 존재하는지 확인합니다.
            if (!businessName || !aiSummarize || !imageData) {
                throw new Error('Required data not found in the fetched JSON');
            }

            // 데이터를 HTML 요소에 반영합니다.
            businessNameElement.textContent = businessName;
            menuDescriptionElement.innerHTML = '<br>' + marked.parse(aiSummarize);
            // menuDescriptionElement.innerHTML = aiSummarize;
            menuImage.src = imageData.replace('![image](', '').replace(')', '');

            // 이미지 로드 완료 후 스피너 숨기기 및 이미지 표시
            menuImage.onload = function() {
                spinner.classList.add('d-none');
                menuImage.style.opacity = '1';
                // 버튼 활성화
                refreshButton.disabled = false;
                // menu-content 스크롤 위치를 맨 위로 이동
                menuContentElement.scrollTop = 0;
            };
        })
        .catch(error => {
            console.error('Error fetching menu:', error);
            alert('메뉴 데이터를 불러오는 중 오류가 발생했습니다.');
            // 오류 발생 시 스피너 숨기기
            spinner.classList.add('d-none');
            menuImage.style.opacity = '1';
            // 버튼 활성화
            refreshButton.disabled = false;
        });
}
function refreshWeatherBasedMenu() {
    const url = 'http://54.180.130.143:8000/recommendation/recommendation_based_on_weather'; // URL을 확인하세요
    const spinner = document.getElementById('spinner');
    const menuImage = document.getElementById('menuImage');
    const businessNameElement = document.getElementById('businessName');
    const menuDescriptionElement = document.getElementById('menuDescription');
    const htmlContentElement = document.getElementById('html-content');
    const refreshButton = document.querySelector('.refresh-button');
    const menuContentElement = document.querySelector('.menu-content'); // menu-content 요소 선택

    // 버튼 비활성화
    refreshButton.disabled = true;

    // 데이터 로드 전 초기 상태 설정
    businessNameElement.innerHTML = '잠시 기다려 주세요..<br><br>&nbsp;<br>&nbsp;<br>';
    menuDescriptionElement.innerHTML = '&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>&nbsp;<br>';
    htmlContentElement.innerHTML = '';

    spinner.classList.remove('d-none');
    menuImage.style.opacity = '0.5';

    // 데이터 초기화 시 스크롤 위치를 맨 위로 이동
    menuContentElement.scrollTop = 0;

    fetch(url)
        .then(response => {
            console.log('Response status:', response.status); // 응답 상태를 로그로 출력
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // JSON 형식으로 응답을 처리합니다.
        })
        .then(data => {
            console.log('Fetched data:', data); // 데이터를 로그로 출력

            // JSON 데이터에서 필요한 정보를 추출합니다.
            let businessName = data.business_name;
            let weatherInfo = data.weather_info;
            let reason = data.reason
            let url = data.url
            let imageData = data.image_data;

            // 데이터가 올바르게 존재하는지 확인합니다.
            if (!businessName || !weatherInfo || !reason || !url || !imageData) {
                throw new Error('Required data not found in the fetched JSON');
            }

            // 데이터를 HTML 요소에 반영합니다.
            businessNameElement.textContent = businessName;
            menuDescriptionElement.innerHTML = marked.parse('[상세보기]'+'('+url+')')+ reason+ "&nbsp;<br><br>" + marked.parse(weatherInfo)  ;
            // menuDescriptionElement.innerHTML = aiSummarize;
            menuImage.src = imageData.replace('![image](', '').replace(')', '');

            // 이미지 로드 완료 후 스피너 숨기기 및 이미지 표시
            menuImage.onload = function() {
                spinner.classList.add('d-none');
                menuImage.style.opacity = '1';
                // 버튼 활성화
                refreshButton.disabled = false;
                // menu-content 스크롤 위치를 맨 위로 이동
                menuContentElement.scrollTop = 0;
            };
        })
        .catch(error => {
            console.error('Error fetching menu:', error);
            alert('메뉴 데이터를 불러오는 중 오류가 발생했습니다.');
            // 오류 발생 시 스피너 숨기기
            spinner.classList.add('d-none');
            menuImage.style.opacity = '1';
            // 버튼 활성화
            refreshButton.disabled = false;
        });
}

// Test if marked is loaded properly
document.addEventListener("DOMContentLoaded", function() {
    if (typeof marked !== 'undefined') {
        console.log('Marked.js is loaded');
    } else {
        console.log('Marked.js is not loaded');
    }
});

function loadCategory(category, button) {
    window.location.href = category + '.jsp';

    // 버튼 클릭 시 active 클래스 추가 및 이전 active 클래스 제거
    const buttons = document.querySelectorAll('.category-button');
    buttons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
}

// 초기 레이아웃 조정 호출
adjustCardWidth();
