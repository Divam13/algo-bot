cmake_minimum_required(VERSION 3.15)
project(AlphaEngineCpp)

set(CMAKE_CXX_STANDARD 17)

# Dependencies: gRPC and Protobuf
find_package(gRPC CONFIG REQUIRED)
find_package(Protobuf CONFIG REQUIRED)
find_package(Threads REQUIRED)

# Include directories
include_directories(include)
include_directories(${CMAKE_CURRENT_BINARY_DIR})

# Generate GRPC/Proto sources
set(PROTO_FILE "protos/backtest.proto")
get_filename_component(PROTO_PATH ${PROTO_FILE} DIRECTORY)
get_filename_component(PROTO_NAME ${PROTO_FILE} NAME_WE)

set(PROTO_SRCS "${CMAKE_CURRENT_BINARY_DIR}/${PROTO_NAME}.pb.cc")
set(PROTO_HDRS "${CMAKE_CURRENT_BINARY_DIR}/${PROTO_NAME}.pb.h")
set(GRPC_SRCS "${CMAKE_CURRENT_BINARY_DIR}/${PROTO_NAME}.grpc.pb.cc")
set(GRPC_HDRS "${CMAKE_CURRENT_BINARY_DIR}/${PROTO_NAME}.grpc.pb.h")

add_custom_command(
  OUTPUT ${PROTO_SRCS} ${PROTO_HDRS} ${GRPC_SRCS} ${GRPC_HDRS}
  COMMAND ${_PROTOBUF_PROTOC}
  ARGS --grpc_out=${CMAKE_CURRENT_BINARY_DIR}
       --cpp_out=${CMAKE_CURRENT_BINARY_DIR}
       -I ${PROTO_PATH}
       --plugin=protoc-gen-grpc=$<TARGET_FILE:gRPC::grpc_cpp_plugin>
       ${PROTO_FILE}
  DEPENDS ${PROTO_FILE}
)

# Main Executable
add_executable(alpha_engine_cpp
  src/main.cpp
  src/strategy.cpp
  ${PROTO_SRCS}
  ${GRPC_SRCS}
)

target_link_libraries(alpha_engine_cpp
  gRPC::grpc++
  protobuf::libprotobuf
  Threads::Threads
)
