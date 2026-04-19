# 🚀 Quick Start Guide: C++ Engine

## One-Liner Build & Run
```bash
# Build everything
build_cpp.bat

# Run the server (in separate terminal)
run_cpp_server.bat

# Run Python backend (in separate terminal)
python main.py

# Run frontend (in separate terminal)
cd frontend && npm run dev
```

## Expected Output

### When Building:
```
============================================
Building C++ Alpha Engine (HFT Module)
============================================
[1/4] Generating Python protobuf stubs...
✓ Python stubs generated
[2/4] Preparing build directory...
[3/4] Running CMake configuration...
[4/4] Building C++ engine...
============================================
[SUCCESS] ✓ C++ Engine Built Successfully!
============================================
```

### When Running C++ Server:
```
🚀 C++ Alpha Engine listening on 0.0.0.0:50051
```

### When Running Backtest (Python logs):
```
🚀 Offloading computation to C++ High-Frequency Engine...
⚡ C++ Engine finished in 23.45ms
```

## Troubleshooting One-Liners

### Check if server is running:
```bash
netstat -an | findstr 50051
```

### Install Python gRPC:
```bash
pip install grpcio grpcio-tools
```

### Install C++ dependencies (vcpkg):
```bash
vcpkg install grpc:x64-windows protobuf:x64-windows
```

### Rebuild from scratch:
```bash
rmdir /s /q cpp_engine\build
build_cpp.bat
```

## Performance Check

Run a backtest and look for this in logs:
- ✅ **Good**: "C++ Engine finished in XX ms"
- ⚠️ **Fallback**: "C++ Engine unavailable, falling back to Python"

If you see fallback:
1. Check C++ server is running
2. Verify port 50051 is not blocked
3. Ensure `CPP_ENGINE_ENABLED=True` in config

## Success Criteria

You know it's working when:
1. Build completes without errors ✅
2. Server starts and shows "listening on 0.0.0.0:50051" ✅
3. Backend logs show "C++ Engine finished in X ms" ✅
4. Backtest results appear in UI ✅

---

**Need Help?** See `cpp_engine/README.md` for detailed troubleshooting
