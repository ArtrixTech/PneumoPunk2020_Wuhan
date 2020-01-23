from back.main import all_urls, all_files
from back.classes.class_ShortLink import ShortLink
from back.classes.class_FileLink import FileLink

from bing_image.bing_refresh import upd_bing_links, flush_bing_img_cache
import time

check_interval = 2


class TimingTask:

    def __init__(self, do_function, check_delay):
        self.do_function = do_function
        self.check_delay = check_delay
        self.last_update = 0

    def check(self, trigger=False):

        # Self-calling to simplify the code.
        if trigger:
            if time.time() - self.last_update > self.check_delay:
                self.last_update = time.time()
                self.do_function()
        else:
            import threading
            tr = threading.Thread(target=self.check, args=(True,))
            tr.start()


def upd_main():
    out_links = "Links:"
    out_files = "Files:"
    all_urls.clear_outdated()
    all_files.clear_outdated()

    for obj in all_urls:
        assert isinstance(obj, ShortLink)
        out_links += obj.alias
        out_links += " -> "
        out_links += str(int(obj.time_remain())) + "s"
        out_links += " | "

    for obj in all_files:
        assert isinstance(obj, FileLink)
        out_files += obj.alias
        out_files += " -> "
        out_files += str(int(obj.time_remain())) + "s"
        out_files += " | "

    if not out_links == "Links:":
        print(out_links)
    if not out_files == "Files:":
        print(out_files)


def check():
    timingTask_main.check()
    timingTask_bing.check()
    timingTask_flush_bing.check()


timingTask_main = TimingTask(upd_main, 1)
timingTask_bing = TimingTask(upd_bing_links, 7200)
timingTask_flush_bing = TimingTask(flush_bing_img_cache, 86400 * 7)
