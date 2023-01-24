import collections


def bfs(grid, start, goal):
    w = h = len(grid)
    q = collections.deque([(start, tuple())])
    visited = {start}
    while q:
        for i in range(len(q)):
            (x, y), path = q.pop()
            if (x, y) == goal:
                return
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dy == 0 and dx == 0:
                        continue
                    nx = x + dx
                    ny = y + dy
                    if -1 < nx < w and -1 < ny < h and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        q.appendleft(((nx, ny), path + (nx, ny)))
