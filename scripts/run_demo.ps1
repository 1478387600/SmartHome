# run_demo.ps1

Write-Host "🚀 MCP Client Demo (client will launch server subprocess)"

# 一步到位：client 内部会以 stdio 启动 server 子进程
python scripts/run_client.py

Write-Host "✅ Demo complete."
