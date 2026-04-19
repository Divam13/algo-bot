@echo off
echo ============================================
echo Starting C++ Alpha Engine Server
echo ============================================

REM Check if binary exists
if not exist cpp_engine\build\Release\alpha_engine_cpp.exe (
    if not exist cpp_engine\build\Debug\alpha_engine_cpp.exe (
        echo [ERROR] C++ Engine binary not found!
        echo Please build it first by running: build_cpp.bat
        exit /b 1
    ) else (
        echo Running DEBUG build...
        cd cpp_engine\build\Debug
        alpha_engine_cpp.exe
    )
) else (
    echo Running RELEASE build...
    cd cpp_engine\build\Release
    alpha_engine_cpp.exe
)
