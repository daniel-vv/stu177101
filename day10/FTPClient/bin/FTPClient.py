#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os,sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import modules


if __name__ == '__main__':
    Run = modules.Client()
    Run.client_run()






