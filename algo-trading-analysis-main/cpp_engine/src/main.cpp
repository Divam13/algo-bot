#include <iostream>
#include <memory>
#include <string>


#include "backtest.grpc.pb.h"
#include "strategy.hpp"
#include <grpcpp/grpcpp.h>


using alpha_engine::BacktestRequest;
using alpha_engine::BacktestResponse;
using alpha_engine::BacktestService;
using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;

// Logic Implementation
class BacktestServiceImpl final : public BacktestService::Service {
  Status RunBacktest(ServerContext *context, const BacktestRequest *request,
                     BacktestResponse *reply) override {
    std::cout << "Received backtest request for Job ID: " << request->job_id()
              << std::endl;

    Engine engine;
    *reply = engine.run(*request);

    std::cout << "Backtest completed. Return: " << reply->total_return() * 100
              << "%" << std::endl;
    return Status::OK;
  }
};

void RunServer() {
  std::string server_address("0.0.0.0:50051");
  BacktestServiceImpl service;

  ServerBuilder builder;
  builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
  builder.RegisterService(&service);

  std::unique_ptr<Server> server(builder.BuildAndStart());
  std::cout << "🚀 C++ Alpha Engine listening on " << server_address
            << std::endl;
  server->Wait();
}

int main(int argc, char **argv) {
  RunServer();
  return 0;
}
