import asyncio
import itertools
import random
import collections

class SongQueue(asyncio.Queue):

  def __init__(self):
    self._queue_all = collections.deque()
    self.current = None
    super().__init__()
  
  def __getitem__(self, item):
    if isinstance(item, slice):
      return list(itertools.islice(self._queue, item.start, item.stop, item.step))
    else:
      return self._queue[item]

  def _get(self):
    if self.__len__() > 0:
      self.current = self._queue[0]
    return super()._get()
  
  def __iter__(self):
    return self._queue.__iter__()

  def __len__(self):
    return self.qsize()

  def len_all(self):
    return len(self._queue_all)
  
  def get_all(self, item):
    if isinstance(item, slice):
      return list(itertools.islice(self._queue_all, item.start, item.stop, item.step))
    else:
      return self._queue_all[item]

  async def put(self, item):
    self._queue_all.append(item)
    await super().put(item)
  
  def clear(self):
    self._queue.clear()
    self._queue_all.clear()

  def shuffle(self):
    random.shuffle(self._queue_all)
    first_item = None
    for i, sng in enumerate(self._queue_all):
      if self._queue_all[i] == self.current:
        first_item = self._queue_all.copy()[i]
        del self._queue_all[i]
        break
    self._queue = self._queue_all.copy()
    if first_item is not None:
      self._queue_all.append(first_item)

  def remove(self, index: int, vc):
    song = self._queue_all.copy()[index]
    for i, sng in enumerate(self._queue):
      if self._queue[i] == song:
        del self._queue[i]
        break
    del self._queue_all[index]
    if self.current == song:
      vc.skip()
    return song
