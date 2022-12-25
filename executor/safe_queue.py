#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import threading
import queue
from dataclasses import dataclass
from loguru import logger  # noqa


@dataclass
class Job:
    """
    :param func - function to execute.

    :param args - arguments to pass to func.

    :param kwargs - keyword arguments to pass to func.

    :param callback - callback function to execute after func.

    :param block - block next job until the current job is done.
    """
    func: callable
    args: tuple = None
    kwargs: dict = None
    callback: callable = None
    block: bool = False


def send_signal_remove_thread():
    logger.info(f"remove thread {threading.get_ident()}")
    sys.exit(1)


class Executor:
    def __init__(self, number_threads=10, max_queue_size=0):
        """
        :param number_threads: number of threads to run concurrently.

        :param max_queue_size: If maxsize is <= 0, the queue size is infinite.
        """
        self.number_threads = number_threads
        self.max_queue_size = max_queue_size
        self.queue = queue.Queue(maxsize=max_queue_size)
        self.thread_start(number_threads)

    def send(self, job: Job) -> None:
        """
        Push a job to the queue

        if the queue is full, 'queue.put' will be block until there is a free space in the queue.

        :param job
        """
        if not job.func:
            raise Exception("executor required")
        self.queue.put(job)
        if job.block:
            self.queue.join()

    def thread_start(self, number_threads=0) -> None:
        if number_threads <= 0:
            number_threads = self.number_threads
        for i in range(number_threads):
            threading.Thread(target=self.worker, daemon=True).start()
        logger.info(f"initialize {number_threads} threads successfully")

    def worker(self) -> None:
        while True:
            try:
                job = self.queue.get(timeout=None)
                result = job.func(*job.args, **job.kwargs)
                if job.callback:
                    job.callback(result)
                self.queue.task_done()
            except Exception as e:
                raise Exception(e)

    def wait(self) -> None:
        """
        wait for all jobs to be completed without blocking each other
        :return:
        """
        self.queue.join()

    def scale_up(self, number_threads: int) -> None:
        """
        :param number_threads: number of threads to run coroutines.
        :return:
        """
        if number_threads == 0:
            raise Exception("number_threads must be greater than 0")
        if self.number_threads == number_threads:
            return
        if self.number_threads > number_threads:
            raise Exception(f"Current number of threads is {self.number_threads}, please use scale down function")
        threads_need_added: int = number_threads - self.number_threads
        self.thread_start(threads_need_added)
        self.number_threads = number_threads
        logger.info(f"scale up to {self.number_threads} threads")

    def scale_down(self, number_threads: int) -> None:
        """
        :param number_threads: number of threads to run coroutines.
        :return:
        """
        # if number_threads == 0:
        #     raise Exception("number_threads must be greater than 0")
        if self.number_threads == number_threads:
            return
        if self.number_threads < number_threads:
            raise Exception(f"Current number of threads is {self.number_threads}, please use scale up function")
        threads_need_removed: int = self.number_threads - number_threads
        self.__remove_threads(threads_need_removed)
        self.number_threads = number_threads
        logger.info(f"scale down to {self.number_threads} threads")

    def __remove_threads(self, number_threads: int) -> None:
        job = Job(func=send_signal_remove_thread, args=(), kwargs={}, callback=None, block=False)
        for i in range(number_threads):
            self.queue.put(job)
        logger.info(f"remove {number_threads} threads")
