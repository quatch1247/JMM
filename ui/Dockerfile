# 기본 이미지를 설정합니다.
FROM tomcat:9.0.73-jdk17-temurin-jammy

# WAR 파일을 Tomcat 웹앱 디렉토리에 복사합니다.
COPY target/gun_ui-0.0.1-SNAPSHOT.war /usr/local/tomcat/webapps/

# 기본 포트를 설정합니다.
EXPOSE 8080

# Tomcat 서버를 실행합니다.
CMD ["catalina.sh", "run"]
