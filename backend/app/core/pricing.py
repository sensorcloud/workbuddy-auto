"""
峰谷定价工具模块
根据时段判断峰/平/谷，计算价格系数
"""
from decimal import Decimal
from datetime import datetime
from dateutil import tz

# 峰谷时段定义（北京时间）
# 峰期: 08:00-11:00, 18:00-21:00
# 平期: 07:00-08:00, 11:00-18:00, 21:00-23:00
# 谷期: 23:00-07:00
PEAK_HOURS = [(8, 11), (18, 21)]
FLAT_HOURS = [(7, 8), (11, 18), (21, 23)]

# 价格系数
PEAK_MULTIPLIER = Decimal("1.5")
FLAT_MULTIPLIER = Decimal("1.0")
VALLEY_MULTIPLIER = Decimal("0.5")

def get_period_type(dt: datetime = None) -> str:
    """判断当前时段类型: peak/flat/valley"""
    if dt is None:
        dt = datetime.now(tz.gettz('Asia/Shanghai'))
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz.gettz('Asia/Shanghai'))

    hour = dt.hour

    for start, end in PEAK_HOURS:
        if start <= hour < end:
            return "peak"
    for start, end in FLAT_HOURS:
        if start <= hour < end:
            return "flat"
    return "valley"

def get_price_multiplier(dt: datetime = None) -> Decimal:
    """获取当前时段价格系数"""
    period = get_period_type(dt)
    if period == "peak":
        return PEAK_MULTIPLIER
    elif period == "flat":
        return FLAT_MULTIPLIER
    else:
        return VALLEY_MULTIPLIER

def calculate_adjusted_price(base_price: Decimal, dt: datetime = None) -> Decimal:
    """计算峰谷调整后的价格"""
    multiplier = get_price_multiplier(dt)
    return (base_price * multiplier).quantize(Decimal("0.01"))

def get_all_period_prices(base_price: Decimal) -> dict:
    """获取所有时段的价格"""
    return {
        "peak": (base_price * PEAK_MULTIPLIER).quantize(Decimal("0.01")),
        "flat": (base_price * FLAT_MULTIPLIER).quantize(Decimal("0.01")),
        "valley": (base_price * VALLEY_MULTIPLIER).quantize(Decimal("0.01")),
        "peak_hours": PEAK_HOURS,
        "flat_hours": FLAT_HOURS,
    }
