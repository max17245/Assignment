@ECHO OFF
REM Minimal stub gradlew.bat for SCA testing only
SET DIR=%~dp0
java -cp "%DIR%gradle\wrapper\gradle-wrapper.jar" org.gradle.wrapper.GradleWrapperMain %*
