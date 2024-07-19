// markdown.js
document.addEventListener('DOMContentLoaded', function () {
    // Markdown 텍스트를 가져옵니다.
    var markdownText = document.getElementById('markdown-content').innerText;

    // marked 라이브러리를 사용하여 Markdown 텍스트를 HTML로 변환합니다.
    var htmlContent = marked(markdownText);

    // 변환된 HTML을 HTML 컨테이너에 넣습니다.
    document.getElementById('html-content').innerHTML = htmlContent;
});
