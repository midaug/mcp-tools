import requests
import os
import json

def search(query: str) -> str:
    """
    使用SearXNG进行搜索
    
    Args:
        query: 搜索关键词
        
    Returns:
        精简的JSON格式搜索结果
    """
    # 从环境变量获取配置
    searxng_host = os.getenv("SEARXNG_HOST", "http://localhost:8080")
    count = int(os.getenv("SEARXNG_COUNT", "10"))
    language = os.getenv("SEARXNG_LANGUAGE", "zh")
    
    # 构建API URL
    api_url = f"{searxng_host}/search"
    
    try:
        # 设置请求参数
        params = {
            "q": query,
            "format": "json",
            "count": count,
            "language": language
        }
        
        # 发送GET请求
        response = requests.get(api_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # 提取并精简结果
            simplified_results = []
            for item in data.get("results", [])[:count]:
                simplified_results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", "")[:200000]  # 限制内容长度
                })
            
            # 返回精简的JSON
            return json.dumps({
                "query": query,
                "count": len(simplified_results),
                "results": simplified_results
            }, ensure_ascii=False)
            
        else:
            return json.dumps({
                "error": f"请求失败，状态码: {response.status_code}",
                "query": query
            }, ensure_ascii=False)
            
    except requests.exceptions.RequestException as e:
        return json.dumps({
            "error": f"请求异常: {str(e)}",
            "query": query
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "error": f"处理异常: {str(e)}",
            "query": query
        }, ensure_ascii=False)