#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: DBQ(Du Baoqiang)

import os
import sys


BASIC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ADMIN_DIR = os.path.join(BASIC_DIR,'db','manager')
STUDENT_DIR = os.path.join(BASIC_DIR,'db','student')
TEACHER_DIR = os.path.join(BASIC_DIR,'db','teacher')
COURSE_DIR = os.path.join(BASIC_DIR,'db','course')
LOG_DIR = os.path.join(BASIC_DIR,'logs')
USER_STATUS = {'manager':False,'teacher':False,'student':False}