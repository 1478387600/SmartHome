#!/bin/bash

# 脚本功能：一键启动 MCP server 和 client，用于快速测试/演示智能家居控制流程

echo "🚀 Starting SmartHome MCP Server and Client Demo"

# 启动 server（后台运行，保存 PID）
echo "👉 Launching MCP Server..."
python scripts/run_server.py > server_output.log 2>&1 &
SERVER_PID=$!

# 给 server 一点启动时间
sleep 1

# 启动 client
echo "👉 Running MCP Client (batch mode)..."
python scripts/run_client.py

# 停止后台 server
echo "🛑 Stopping MCP Server..."
kill $SERVER_PID

echo "✅ Demo complete. Server log saved to server_output.log"
