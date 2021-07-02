import datetime as dt
from cetus_api import get_time

class AlarmMan:
    def __init__(self):
        self.first_night = get_time()
        self.night_gap = dt.timedelta(minutes=150)

    def refresh(self):
        self.first_night = get_time()
        return f'First night refresh to {self.first_night}'

    def alarm(self):
        left_min = int((self.next_night() - now()).total_seconds() // 60)
        state = '入夜' if left_min <= 100 else '日出'
        left_min -= 100 if left_min > 100 else 0
        msg = f'希圖斯還有 {left_min} 分鐘{state}\n下個夜晚：{self.next_night()}'

        return msg

    def next_night(self):
        today = dt.datetime.now()
        gap = today - self.first_night
        night_len = dt.timedelta(minutes=50)
        time = self.first_night + (gap // self.night_gap + 1) * self.night_gap

        return time

    def recent_night(self):
        result = []
        today = dt.datetime.now().replace(hour=0, minute=0)
        gap = today - self.first_night
        night_len = dt.timedelta(minutes=50)
        time = self.first_night + (gap // self.night_gap + 1) * self.night_gap
        tomorrow = today + dt.timedelta(days=1, hours=23, minutes=59)

        pre = time
        result.append('\n\n近期入夜時間\n')
        result.append('今天上午\n```')
        while time <= tomorrow:
            t2 = time + night_len
            a = time.strftime('%m/%d %H:%M')
            b = t2.strftime('%H:%M')
            result.append(f'{a}~{b}')
            pre = time
            time += self.night_gap
            if pre.hour < 12 and time.hour >= 12:
                if pre.day == today.day:
                    result.append('```\n今天下午```')
                else:
                    result.append('```\n明天下午```')
            if pre.day != time.day and time <= tomorrow:
                result.append('```\n明天上午```')

        result.append('```')

        return '\n'.join(result)

    def full_message(self):
        return self.alarm() + self.recent_night()

def now():
    return dt.datetime.now()

if __name__ == "__main__":
    am = AlarmMan()
    print(am.full_message())
    am.refresh()
