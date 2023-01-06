#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from executor.safe_queue import Executor, Job
import time
from loguru import logger
from typing import Any


def test_exec(*args, **kwargs):
    time.sleep(3)
    logger.info(args)
    return [1, 2, 3]


def test_exec1(*args, **kwargs):
    logger.info(kwargs)
    time.sleep(2)
    return {"a": 1, "b": 2, "c": 3}


def call_back(result: Any):
    logger.info(result)


class TestSafeQueue(unittest.TestCase):
    def test_simple_safe_queue(self):
        engine = Executor(number_threads=2, max_queue_size=0)
        engine.send(Job(func=test_exec, args=(1, 2), kwargs={}, callback=None, block=False))
        engine.send(Job(func=test_exec1, args=(), kwargs={"time": 1}, callback=None, block=False))
        engine.send(Job(func=test_exec1, args=(), kwargs={}, callback=None, block=False))
        engine.send(Job(func=test_exec1, args=(), kwargs={}, callback=None, block=False))
        engine.send(Job(func=test_exec1, args=(), kwargs={}, callback=None, block=False))
        engine.wait()
        logger.info("done")

    def test_over_load(self):
        engine = Executor(number_threads=2, max_queue_size=3)
        for i in range(5):
            engine.send(Job(func=test_exec1, args=(), kwargs={"time": 1}, callback=None, block=False))
        engine.wait()
        logger.info("done")
        engine.send(Job(func=test_exec1, args=(), kwargs={"time": "over power"}, callback=None, block=False))
        engine.wait()
        logger.info("done2")

    def test_call_back(self):
        engine = Executor(number_threads=10, max_queue_size=0)
        for i in range(5):
            engine.send(Job(func=test_exec1, args=(), kwargs={"time": 1}, callback=call_back, block=False))
        engine.wait()

    def test_scale_up(self):
        engine = Executor(number_threads=2)
        for i in range(4):
            engine.send(Job(func=test_exec1, args=(), kwargs={"time": 1}, callback=None, block=False))
        engine.wait()
        engine.scale_up(3)
        for i in range(6):
            engine.send(Job(func=test_exec1, args=(), kwargs={"time": 1}, callback=None, block=False))
        engine.wait()

    def test_scale_down(self):
        engine = Executor(number_threads=4)
        for i in range(5):
            engine.send(Job(func=test_exec1, args=(), kwargs={"time": 1}, callback=None, block=False))
        engine.wait()
        engine.scale_down(3)
        for i in range(6):
            engine.send(Job(func=test_exec1, args=(), kwargs={"time": 1}, callback=None, block=False))
        time.sleep(10)
        # engine.wait()
