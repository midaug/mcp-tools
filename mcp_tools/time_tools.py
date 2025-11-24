from datetime import datetime
import zhdate
from typing import Dict, Any

# 星期映射字典
weekday_map = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

# 农历月份和日期映射
lunar_months = ["正", "二", "三", "四", "五", "六", "七", "八", "九", "十", "冬", "腊"]
lunar_days = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
              "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
              "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]

def get_complete_calendar_info() -> Dict[str, Any]:
    """
    获取完整的日历信息，包括公历、农历、星期等
    
    Returns:
        dict: 包含完整日历信息的字典
    """
    try:
        # 获取当前时间
        now = datetime.now()
        
        # 公历信息
        gregorian_date = now.strftime("%Y年%m月%d日")
        gregorian_time = now.strftime("%H时%M分%S秒")
        weekday = weekday_map[now.weekday()]
        
        # 农历信息 - 修复属性名：使用 leap_month 而不是 is_leap_month
        zh_date = zhdate.ZhDate.today()
        lunar_year = zh_date.lunar_year
        lunar_month = zh_date.lunar_month
        lunar_day = zh_date.lunar_day
        is_leap = zh_date.leap_month  # 这是正确的属性名[6](@ref)
        
        # 格式化农历日期
        lunar_month_str = f"闰{lunar_months[lunar_month-1]}" if is_leap else lunar_months[lunar_month-1]
        lunar_day_str = lunar_days[lunar_day-1] if lunar_day <= 30 else "三十"
        lunar_date = f"农历{lunar_year}年{lunar_month_str}月{lunar_day_str}"
        
        # 天干地支和生肖
        heavenly_stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
        earthly_branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        zodiac_animals = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
        
        # 计算天干地支（简化算法）
        stem_index = (lunar_year - 4) % 10
        branch_index = (lunar_year - 4) % 12
        heavenly_stem = heavenly_stems[stem_index]
        earthly_branch = earthly_branches[branch_index]
        zodiac = zodiac_animals[branch_index]
        
        # 确保返回字典格式，这是MCP工具的要求[1,2,3](@ref)
        return {
            "success": True,
            "gregorian_date": gregorian_date,
            "gregorian_time": gregorian_time, 
            "weekday": weekday,
            "lunar_year": lunar_year,
            "lunar_month": lunar_month,
            "lunar_day": lunar_day,
            "lunar_date_display": lunar_date,
            "heavenly_stem": heavenly_stem,
            "earthly_branch": earthly_branch,
            "chinese_era": f"{heavenly_stem}{earthly_branch}",
            "zodiac": f"{zodiac}年",
            "timestamp": now.timestamp(),
            "complete_display": f"{gregorian_date} {gregorian_time} {weekday}，{lunar_date}（{heavenly_stem}{earthly_branch}年 {zodiac}年）"
        }
        
    except Exception as e:
        # 错误时也必须返回字典，而不是字符串
        return {
            "success": False,
            "error": f"获取日历信息时发生错误: {str(e)}",
            "error_type": type(e).__name__
        }

def get_current_calendar() -> Dict[str, Any]:
    """获取当前完整的日历信息，包括公历日期时间、星期几和农历信息
    
    Returns:
        dict: 包含完整日历信息的字典
    """
    try:
        return get_complete_calendar_info()
    except Exception as e:
        return {"error": f"获取日历信息时发生错误: {str(e)}"}

def get_formatted_datetime() -> str:
    """获取格式化的日期时间字符串，格式：2025年11月21日 16点44分05秒 星期五，农历十月初二
    
    Returns:
        str: 格式化后的日期时间字符串
    """
    try:
        info = get_complete_calendar_info()
        return info["complete_display"]
    except Exception as e:
        return f"错误: {str(e)}"

def get_gregorian_info() -> Dict[str, Any]:
    """获取公历日期和时间信息
    
    Returns:
        dict: 包含公历日期、时间和星期的字典
    """
    now = datetime.now()
    return {
        "date": now.strftime("%Y年%m月%d日"),
        "time": now.strftime("%H时%M分%S秒"),
        "weekday": weekday_map[now.weekday()],
        "iso_format": now.isoformat(),
        "timestamp": now.timestamp()
    }

def get_lunar_info() -> Dict[str, Any]:
    """获取详细的农历信息
    
    Returns:
        dict: 包含农历日期、天干地支、生肖等信息的字典
    """
    try:
        info = get_complete_calendar_info()
        return {
            "lunar_date": info["lunar_date_display"],
            "chinese_era": info["chinese_era"],
            "zodiac": info["zodiac"],
            "lunar_year": info["lunar_year"],
            "lunar_month": info["lunar_month"],
            "lunar_day": info["lunar_day"]
        }
    except Exception as e:
        return {"error": f"获取农历信息时发生错误: {str(e)}"}

def get_time_until_target(target_date: str) -> Dict[str, Any]:
    """计算距离目标日期的天数
    
    Args:
        target_date: 目标日期，格式为YYYY-MM-DD或YYYY年MM月DD日
        
    Returns:
        dict: 包含距离天数和相关信息的字典
    """
    try:
        # 处理日期格式
        if "年" in target_date:
            target = datetime.strptime(target_date, "%Y年%m月%d日")
        else:
            target = datetime.strptime(target_date, "%Y-%m-%d")
        
        now = datetime.now()
        # 确保目标日期的时间部分与当前时间一致，以便准确计算天数差
        target = target.replace(hour=now.hour, minute=now.minute, second=now.second)
        delta = target - now
        days = delta.days
        hours = delta.seconds // 3600
        
        return {
            "target_date": target_date,
            "days_until": days,
            "hours_until": hours,
            "is_past": days < 0,
            "absolute_days": abs(days)
        }
    except Exception as e:
        return {"error": f"日期计算错误: {str(e)}"}