import datetime

# 判断 2018年4月30号 是不是节假日
from chinese_calendar import is_workday, is_holiday
april_last = datetime.date(2018, 4, 30)
print(april_last)

# 或者在判断的同时，获取节日名
import chinese_calendar as calendar  # 也可以这样 import
on_holiday, holiday_name = calendar.get_holiday_detail(april_last)
print(on_holiday)
print(holiday_name)

# 还能判断法定节假日是不是调休
import chinese_calendar
print(chinese_calendar.is_in_lieu(datetime.date(2006, 1, 1)))
print(chinese_calendar.is_in_lieu(datetime.date(2006, 1, 2)))

# python -m test.test_workdays