import collections


def backtrace(parent, start, goal):
    """
        Trace path that tracks goal to start with endpoint being start.
        Start goal nodes are at the start to pop them effortlessly. Ie:
        path = [goal, node, node, start]
        path.pop()
        path = [goal, node, node]
    """

    path = [goal]
    while path[-1] != start:
        path.append(parent[path[-1]])
    path.pop()
    return path


def bfs(grid, start, goal):
    parent = {}
    w = h = len(grid)
    q = collections.deque([(start, tuple())])
    visited = {start}
    while q:
        for i in range(len(q)):
            (x, y), path = q.pop()
            if (x, y) == goal:
                return backtrace(parent, start, goal)

            # evaluation order is
            moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            moves += [(-1,-1), (-1, 1), (1, -1), (1, 1)]

            for dx, dy in moves:
                if dy == 0 and dx == 0:
                    continue
                nx = x + dx
                ny = y + dy
                if -1 < nx < w and -1 < ny < h and (nx, ny) not in visited:
                    parent[(nx, ny)] = x, y
                    visited.add((nx, ny))
                    q.appendleft(((nx, ny), path + (nx, ny)))
