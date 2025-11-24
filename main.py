from fastmcp import FastMCP
import os

from mcp_tools import time_tools

# 创建主MCP服务器实例
mcp = FastMCP("MD的工具箱")

# === 注册时间工具 ===
@mcp.tool()
def get_current_time() -> str:
    """获取当前时间格式化后的的日期时间字符串，格式：yyyy年MM月dd日 HH点mm分ss秒 星期，农历"""
    try:
        info = time_tools.get_complete_calendar_info()
        return f"今天日期信息为: {str(info["complete_display"])}"
    except Exception as e:
        return f"工具执行错误: {str(e)}"

if __name__ == "__main__":
    # 启动服务器（支持多种传输方式）
    
    # 方式1: STDIO（适合Claude Desktop等客户端）
    # mcp.run(transport="stdio")
    mcp.run(transport="stdio")
    
    # 方式2: HTTP（适合Web客户端）
    # mcp.run(transport="http", host="0.0.0.0", port=8000)
    
    # 方式3: SSE（Server-Sent Events）
    # mcp.run(transport="sse", host="0.0.0.0", port=8000)