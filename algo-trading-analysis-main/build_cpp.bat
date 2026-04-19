@echo off
echo ============================================
echo Building C++ Alpha Engine (HFT Module)
echo ============================================

REM Step 1: Generate Protobuf stubs for Python
echo [1/4] Generating Python protobuf stubs...
cd cpp_engine
python -m grpc_tools.protoc -I./protos --python_out=../src/backtesting --grpc_python_out=../src/backtesting ./protos/backtest.proto
if %errorlevel% neq 0 (
    echo [ERROR] Failed to generate Python stubs. Please ensure grpcio-tools is installed:
    echo    pip install grpcio-tools
    cd ..
    exit /b %errorlevel%
)
echo ✓ Python stubs generated
cd ..

REM Step 2: Create build directory
echo [2/4] Preparing build directory...
if not exist cpp_engine\build mkdir cpp_engine\build
cd cpp_engine\build

REM Step 3: CMake Configuration
echo [3/4] Running CMake configuration...
cmake .. -DCMAKE_BUILD_TYPE=Release
if %errorlevel% neq 0 (
    echo [ERROR] CMake configuration failed.
    echo Please ensure you have:
    echo   1. CMake installed (https://cmake.org/download/)
    echo   2. A C++ Compiler (Visual Studio 2019+ or MinGW)
    echo   3. gRPC and Protobuf libraries installed via vcpkg:
    echo      vcpkg install grpc:x64-windows protobuf:x64-windows
    cd ..\..
    exit /b %errorlevel%
)

REM Step 4: Build
echo [4/4] Building C++ engine...
cmake --build . --config Release
if %errorlevel% neq 0 (
    echo [ERROR] Build failed. Check compiler errors above.
    cd ..\..
    exit /b %errorlevel%
)

echo ============================================
echo [SUCCESS] ✓ C++ Engine Built Successfully!
echo ============================================
echo.
echo To run the C++ server:
echo   cd cpp_engine\build\Release
echo   alpha_engine_cpp.exe
echo.
echo The server will listen on port 50051
cd ..\..

