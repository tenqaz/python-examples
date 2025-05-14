import logging
import threading
import uuid
import weakref
from _weakref import ReferenceType
from typing import Optional, Union

from redis import RedisCluster


class RedisLock:

    def __init__(self, redis_client: RedisCluster, name: str, vid: Optional[str] = None, expire: Optional[int] = None,
                 auto_renewal: bool = False):
        """
        
        Args:
            redis_client: redis客户端
            name: key姓名
            vid: value的id值
            expire: 过期时间
            auto_renewal: 是否需要自动续约
        """
        self._client = redis_client
        self._name = name
        self._expire = expire

        # 续约间隔时间
        self._lock_renewal_interval = expire * 2 / 3 if auto_renewal else None

        if vid is None:
            self._id = str(uuid.uuid4())
        else:
            self._id = vid

        self._lock_renewal_thread: Union[threading.Thread, None] = None

    def acquire(self):
        is_ok = self._client.set(self._name, self._id, nx=True, ex=self._expire)
        if not is_ok:
            return False

        if self._lock_renewal_interval:
            self._start_lock_renewer()

        return True

    def release(self):
        if self._lock_renewal_thread is not None:
            self._stop_lock_renewer()
        logging.debug("Releasing Lock(%r).", self._name)
        self._client.delete(self._name)

    def extend(self, expire: int):
        self._client.expire(self._name, expire)

    def _start_lock_renewer(self):
        self._lock_renewal_stop = threading.Event()
        self._lock_renewal_thread = threading.Thread(
            target=self._lock_renewer,
            kwargs={
                'name': self._name,
                'lock_ref': weakref.ref(self),
                'interval': self._lock_renewal_interval,
                'stop': self._lock_renewal_stop,
            },
        )
        self._lock_renewal_thread.daemon = True
        self._lock_renewal_thread.start()

    @staticmethod
    def _lock_renewer(name: str, lock_ref: ReferenceType, interval: int, stop: threading.Event):
        while not stop.wait(timeout=interval):
            logging.debug("Refreshing Lock(%r).", name)
            lock: "RedisLock" = lock_ref()
            if lock is None:
                logging.debug("Stopping loop because Lock(%r) was garbage collected.", name)
                break
            lock.extend(expire=lock._expire)
            del lock

    def _stop_lock_renewer(self):
        if self._lock_renewal_thread is None or not self._lock_renewal_thread.is_alive():
            return
        logging.debug("Signaling renewal thread for Lock(%r) to exit.", self._name)
        self._lock_renewal_stop.set()
        self._lock_renewal_thread.join()
        self._lock_renewal_thread = None
        logging.debug("Renewal thread for Lock(%r) exited.", self._name)
