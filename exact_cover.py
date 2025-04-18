from collections import deque
from typing import Any, Generator, Iterable, Optional, Self

__all__ = ["ExactCover"]


class Data[Co, Ca]:
    def __init__(
        self,
        constraint: "Constraint[Co,Ca]",
        candidate: "Candidate[Co,Ca]",
        l: Optional[Self] = None,
        r: Optional[Self] = None,
        u: Optional[Self] = None,
        d: Optional[Self] = None,
    ):
        self.constraint = constraint
        self.candidate = candidate
        self.l = l or self
        self.r = r or self
        self.u = u or self
        self.d = d or self

    def right(self, skip_self=False):
        data = self
        if not skip_self:
            yield data
        while (data := data.r) is not self:
            yield data

    def left(self):
        data = self
        while (data := data.l) is not self:
            yield data

    def __repr__(self):
        return f"{self.__class__.__name__}(candidate={self.candidate.value!r}, constraint={self.constraint.value!r})"


class Constraint[Co, Ca](Data[Co, Ca]):
    l: Self
    r: Self
    d: Data[Co, Ca]
    u: Data[Co, Ca]

    def __init__(self, value: Co, l: Self, r: Self):
        super().__init__(constraint=None, candidate=None, l=l, r=r)
        self.value = value
        self.size = int(0)
        self.covered = False

    def down(self):
        data = self
        while (data := data.d) is not self:
            yield data

    def up(self):
        data = self
        while (data := data.u) is not self:
            yield data

    def cover(self):
        assert not self.covered, "Already covered"
        self.covered = True

        self.r.l = self.l
        self.l.r = self.r

        for i in self.down():
            for j in i.right(skip_self=True):
                j.d.u = j.u
                j.u.d = j.d
                j.constraint.size -= 1  # decrease counter for constraint

        return self

    def uncover(self):
        self.covered = False

        for i in self.up():
            for j in i.left():
                j.constraint.size += 1  # increase counter for constraint
                j.d.u = j.u.d = j

        self.r.l = self.l.r = self

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value!r}, size={self.size})"


class Candidate[Co, Ca](Data[Co, Ca]):
    u: Self
    d: Self
    r: Data[Co, Ca]
    l: Data[Co, Ca]

    def __init__(self, value: Ca, u: Self, d: Self):
        super().__init__(candidate=None, constraint=None, u=u, d=d)
        self.value = value

    def right(self):
        if self.r is not self:
            yield from self.r.right()

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}(value={self.value!r})"


class Root[Ca, Co](Data[Ca, Co]):
    u: Candidate[Ca, Co]
    d: Candidate[Ca, Co]
    l: Constraint[Ca, Co]
    r: Constraint[Ca, Co]

    def __init__(self):
        super().__init__(constraint=None, candidate=None)
        self.constraints = dict[Ca, Constraint[Ca, Co]]()
        self.candidates = dict[Co, Candidate[Ca, Co]]()

    def right(self):
        constraint = self
        while (constraint := constraint.r) is not self:
            yield constraint

    def down(self):
        candidate = self
        while (candidate := candidate.d) is not self:
            yield candidate

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class ExactCover[Co, Ca]:
    def __init__(self, constraints: Iterable[Co], candidates: dict[Ca, Iterable[Co]]):
        self.root = root = Root[Co, Ca]()

        con: Constraint[Co, Ca] = root
        for v in constraints:
            root.constraints[v] = con.r.l = con.r = con = Constraint[Co, Ca](
                value=v, l=con, r=con.r
            )

        can: Candidate[Co, Ca] = root
        for candidate, constraint_set in candidates.items():
            root.candidates[candidate] = can.d.u = can.d = can = Candidate(
                value=candidate, u=can, d=can.d
            )
            data: Data[Co, Ca] = can
            for v in constraint_set:
                con = self.root.constraints[v]
                con.u.d = con.u = data.r.l = data.r = data = Data(
                    candidate=can, constraint=con, u=con.u, d=con, l=data, r=data.r
                )
                con.size += 1

            can.l.r = can.r
            can.r.l = can.l

    def __search(self, O=deque[Ca]()) -> Generator[tuple[Ca], Any | None, Any | None]:
        if self.root.r == self.root:
            return (yield tuple(O))

        response = None
        constraint = min(self.root.right(), key=lambda e: e.size).cover()
        for row in constraint.down():
            for d in row.right(skip_self=True):
                d.constraint.cover()

            O.append(row.candidate.value)
            response = yield from self.__search(O)
            O.pop()

            for d in row.left():
                d.constraint.uncover()

            if response:
                break

        constraint.uncover()
        return response

    def search(
        self, initial: Iterable[Ca] = list[Ca]()
    ) -> Generator[tuple[Ca], Any | None, Any | None]:
        covered = deque(
            data.constraint.cover()
            for candidate in initial
            for data in self.root.candidates[candidate].right()
        )

        try:
            yield from self.__search(initial)
        finally:
            while covered:
                covered.pop().uncover()
