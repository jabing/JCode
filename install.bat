@echo off
REM JCode OpenCode 安装脚本 (Windows Batch)
REM Usage: install.bat [--global|--project|--uninstall|--status]

setlocal EnableDelayedExpansion

echo.
echo ================================================
echo   JCode OpenCode Installer for Windows
echo ================================================
echo.

set "JCODE_ROOT=%~dp0"
set "JCODE_ROOT=%JCODE_ROOT:~0,-1%"
set "OPENCODE_GLOBAL=%USERPROFILE%\.config\opencode"
set "OPENCODE_PROJECT=%CD%\.opencode"

REM Parse arguments
set "SCOPE=interactive"
set "ACTION=install"

:parse_args
if "%~1"=="" goto :done_args
if /i "%~1"=="--global" set "SCOPE=global"
if /i "%~1"=="--project" set "SCOPE=project"
if /i "%~1"=="--uninstall" set "ACTION=uninstall"
if /i "%~1"=="--status" set "ACTION=status"
if /i "%~1"=="-h" goto :show_help
if /i "%~1"=="--help" goto :show_help
shift
goto :parse_args

:done_args

REM Run Python installer
python "%JCODE_ROOT%\install.py" %*
goto :eof

:show_help
echo Usage: install.bat [OPTIONS]
echo.
echo Options:
echo   --global      全局安装
echo   --project     项目安装
echo   --uninstall   卸载
echo   --status      查看状态
echo   -h, --help    显示帮助
echo.
echo Examples:
echo   install.bat              # 交互式安装
echo   install.bat --global     # 全局安装
echo   install.bat --uninstall  # 卸载
goto :eof
