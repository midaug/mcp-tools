import requests
import os
import json
import threading
import concurrent.futures
from queue import Queue
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

def fetch_web_content(url, timeout=2):
    """
    抓取单个网页的文本内容
    
    Args:
        url: 要抓取的网页URL
        timeout: 超时时间（秒）
        
    Returns:
        网页的纯文本内容（最多4000字符），失败返回空字符串
    """
    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        
        # 发送HTTP请求，设置超时
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # 检查HTTP错误
        
        # 使用BeautifulSoup解析HTML并提取文本
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 移除脚本和样式标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 获取纯文本内容
        text = soup.get_text()
        
        # 清理文本：移除多余空白字符
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # 限制长度为4000字符
        if len(text) > 4000:
            text = text[:4000] + "...[内容截断]"
            
        return text
        
    except requests.exceptions.Timeout:
        print(f"抓取超时: {url}")
        return ""
    except requests.exceptions.RequestException as e:
        print(f"请求错误 {url}: {e}")
        return ""
    except Exception as e:
        print(f"处理错误 {url}: {e}")
        return ""

def fetch_urls_parallel(urls, max_workers=5, timeout=2):
    """
    使用线程池并行抓取多个URL的网页内容
    
    Args:
        urls: URL列表
        max_workers: 最大线程数
        timeout: 单个请求超时时间（秒）
        
    Returns:
        字典，key为URL，value为网页内容
    """
    results = {}
    
    # 使用ThreadPoolExecutor创建线程池
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_url = {executor.submit(fetch_web_content, url, timeout): url for url in urls}
        
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                content = future.result()
                results[url] = content
            except Exception as e:
                print(f"处理URL时发生异常 {url}: {e}")
                results[url] = ""
    
    return results

def search(query: str) -> str:
    """
    使用SearXNG进行搜索，并抓取搜索结果网页的文本内容
    
    Args:
        query: 搜索关键词
        
    Returns:
        包含网页内容的JSON格式搜索结果
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
            urls_to_fetch = []
            
            # 第一次遍历：收集所有URL
            for item in data.get("results", [])[:count]:
                url = item.get("url", "")
                if url:
                    urls_to_fetch.append(url)
                simplified_results.append({
                    "title": item.get("title", ""),
                    "url": url,
                    "content": item.get("content", "")[:4000]  # 限制内容长度
                })
            
            # 使用多线程并行抓取网页内容
            print(f"开始抓取 {len(urls_to_fetch)} 个网页的文本内容...")
            web_contents = fetch_urls_parallel(urls_to_fetch, max_workers=5, timeout=2)
            
            # 第二次遍历：将网页内容添加到结果中
            for result in simplified_results:
                url = result["url"]
                if url and url in web_contents and web_contents[url]:
                    result["web_content"] = web_contents[url]
                else:
                    result["web_content"] = ""  # 抓取失败或内容为空
            
            # 统计抓取结果
            successful_fetches = sum(1 for result in simplified_results if result["web_content"])
            print(f"网页内容抓取完成: 成功 {successful_fetches}/{len(simplified_results)}")
            
            # 返回包含网页内容的JSON
            return json.dumps({
                "query": query,
                "count": len(simplified_results),
                "web_content_success_count": successful_fetches,
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

# 测试函数
def test_search():
    """测试函数"""
    # 设置测试环境变量（如果不在环境中）
    if not os.getenv("SEARXNG_HOST"):
        os.environ["SEARXNG_HOST"] = "http://localhost:8080"
    
    # 测试搜索
    result = search("Python编程")
    print("搜索结果示例:")
    data = json.loads(result)
    
    if "results" in data:
        for i, item in enumerate(data["results"][:2]):  # 只显示前2个结果
            print(f"\n--- 结果 {i+1} ---")
            print(f"标题: {item.get('title', '')}")
            print(f"URL: {item.get('url', '')}")
            print(f"摘要: {item.get('content', '')[:100]}...")
            web_content = item.get('web_content', '')
            if web_content:
                print(f"网页内容: {web_content[:100]}...")
            else:
                print("网页内容: [抓取失败或为空]")
    
    print(f"\n总结果数: {data.get('count', 0)}")
    print(f"成功抓取网页内容: {data.get('web_content_success_count', 0)}")

if __name__ == "__main__":
    # 如果直接运行，进行测试
    test_search()