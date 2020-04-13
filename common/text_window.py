#!/usr/bin/env python3
import os
import time
import subprocess
from common.basedir import BASEDIR


class TextWindow():
  def __init__(self, s):
    try:
      self.text_proc = subprocess.Popen(["./text", s],
                                        stdin=subprocess.PIPE,
                                        cwd=os.path.join(BASEDIR, "selfdrive", "ui", "text"),
                                        close_fds=True)
    except OSError:
      self.text_proc = None

  def get_status(self):
    if self.text_proc is not None:
      self.text_proc.poll()
      return self.text_proc.returncode

    return None

  def __enter__(self):
    return self

  def close(self):
    if self.text_proc is not None:
      self.text_proc.terminate()
      self.text_proc = None

  def wait_for_exit(self):
    while True:
      if self.get_status() == 1:
        return
      time.sleep(0.1)

  def __del__(self):
    self.close()

  def __exit__(self, type, value, traceback):
    self.close()


class FakeTextWindow():
  def __init__(self, s):
    pass

  def get_status(self):
    return 1

  def wait_for_exit(self):
    return

  def __enter__(self):
    return self

  def update(self, _):
    pass

  def __exit__(self, type, value, traceback):
    pass


if __name__ == "__main__":
  text = """Traceback (most recent call last):
  File "./controlsd.py", line 608, in <module>
    main()
  File "./controlsd.py", line 604, in main
    controlsd_thread(sm, pm, logcan)
  File "./controlsd.py", line 455, in controlsd_thread
    1/0
ZeroDivisionError: division by zero"""
  print(text)

  with TextWindow(text) as s:
    for _ in range(100):
      if s.get_status() == 1:
        print("Got exit button")
        break
      time.sleep(0.1)
  print("gone")
