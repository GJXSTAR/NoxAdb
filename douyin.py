
import os
import re
import time
import random


def open_app(device):
    """打开应用服务"""
    # 打开应用 com.ss.android.ugc.aweme.lite/com.ss.android.ugc.aweme.splash.SplashActivity
    os.system("adb -s {} shell am start -n com.ss.android.ugc.aweme.lite/com.ss.android.ugc.aweme.splash.SplashActivity".format(device))


class AutoRun(object):
    def __init__(self, run_time):
        self.run_time = run_time
        self.devices = []
        self.check = {}
    
    # 获取设备总数
    def get_all_devices(self):
        try:
            for device in os.popen("adb devices"):
                if "\t" in device:
                    self.devices.append(device.split("\t")[0])
        except Exception as e:
            print(e)
            # _ = e
            pass
        print("设备: {} \t数量: {}台".format(self.devices, len(self.devices)))

    # 获取设备屏幕 宽 高
    def get_screen_params(self):
        screen_w_h = {}
        for device in self.devices:
            # 获取分辨率
            f = os.popen("adb -s " + device + " shell wm size")
            w, h = re.search(r"(\d{3,4})x(\d{3,4})", f.read()).groups()
            screen_w_h[device] = [int(w), int(h)]
        return screen_w_h

    def check_ps(self):
        """打开应用服务"""

        # 检测后台应用服务 adb shell ps | find "aweme"
        # adb shell ps | grep "aweme"
        for device in self.devices:
            rsp = os.popen("adb -s {} shell ps | find \"aweme\"".format(device))
            rsp_io = rsp.__dict__["_stream"]
            rsp_ps = [i for i in rsp_io.readlines()]
            # print(rsp_ps, len(rsp_ps))
            if len(rsp_ps) == 6:
                self.check[device] = 1
            elif len(rsp_ps) > 6:
                self.check[device] = -1
            else:
                self.check[device] = 0

        return

    # 运行
    def run(self):
        # 获取所有设备
        self.get_all_devices()
        if not len(self.devices):
            print("没有发现设备，请检查......")
            return

        # 获取屏幕宽高
        screen_params = self.get_screen_params()
        print('屏幕参数: {}'.format(screen_params))

        for device in self.devices:
            open_app(device)
        # 等待软件打开
        time.sleep(7)

        # 打开软件时的时间
        app_start = time.time()
        count = 0
        
        while (time.time() - app_start) < self.run_time:
            if count % 7 == 1:
                print("第 {} 次执行成功\t剩余任务时间 {} 分钟.....".format(count, int((self.run_time - (time.time() - app_start)) / 60)))
                # 检测应用服务是否闪退
                self.check_ps()
                # 重启应用服务
                for device in self.devices:
                    if self.check[device] == 0:
                        open_app(device)
                        time.sleep(7)
                    elif self.check[device] == -1:
                        # 无响应，点击确定
                        w, h = screen_params[device][0], screen_params[device][1]
                        x = random.randint(int(w * 0.79), int(w * 0.80))
                        y = random.randint(int(h * 0.535), int(h * 0.545))
                        # print('{} 点击确定 {} {}'.format(device, x, y))
                        os.system("adb -s {} shell input tap {} {}".format(device, x, y))
                        time.sleep(7)
                        open_app(device)
                        time.sleep(7)

            count += 1

            # 随机停留时间
            time.sleep(random.randint(3, 7))

            # 屏幕中间 3/5 区域内模拟滑动
            swipe_params = {}
            for k in screen_params:
                v = screen_params[k]
                # 起点
                x1 = random.randint(int(v[0] * 0.2), int(v[0] * 0.8))
                y1 = random.randint(int(v[1] * 0.5), int(v[1] * 0.8))
                # 终点
                x2 = x1 + random.randint(-int(v[0] * 0.01), int(v[0] * 0.01))
                y2 = y1 + random.randint(-int(v[1] * 0.01), int(v[1] * 0.01)) - random.randint(int(v[1] * 0.3), int(v[1] * 0.4))
                # 向下滑动刷新
                if count < 7:
                    swipe_params[k] = [x2, y2, x1, y1]
                else:  # 向上滑动
                    swipe_params[k] = [x1, y1, x2, y2]
            # print(swipe_params)

            # 设备循环执行
            for device in self.devices:
                os.system("adb -s {} shell input swipe {} {} {} {} {} &".format(device, *swipe_params[device], random.randint(222, 777)))
                time.sleep(1)

                # # 随机点赞
                # if random.randint(0, 17) == 7:
                #     w, h = screen_params[device][0], screen_params[device][1]
                #     x = random.randint(int(w * 0.92), int(w * 0.97))
                #     y = random.randint(int(h * 0.60), int(h * 0.64))
                #     # print('{} 点赞 {} {}'.format(device, x, y))
                #     os.system("adb -s {} shell input tap {} {}".format(device, x, y))

        print("任务完成")

        # 关闭软件
        for device in self.devices:
            os.system("adb -s {} shell am force-stop com.ss.android.ugc.aweme.lite".format(device))


def main():
    # 运行时间 0.5 - 1 小时
    print('Starting......')
    r_time = 60 * random.randint(30, 60)
    print("任务总时间：{} 分钟".format(int(r_time / 60)))
    auto = AutoRun(r_time)
    auto.run()
    print('Ending......')


if __name__ == '__main__':
    main()
