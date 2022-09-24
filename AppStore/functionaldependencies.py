from copy import deepcopy
from itertools import chain, combinations
from pprint import pprint
from typing import Iterable


class FD:
    """
    Encapsulates the lhs and rhs of an fd.
    """

    def __init__(self, lhs: Iterable[str], rhs: Iterable[str]):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self) -> str:
        return f"{'{' + ', '.join(self.lhs) + '}'}->{'{' + ', '.join(self.rhs) + '}'}"

    def is_trivial(self) -> bool:
        """
        Returns true if and only if rhs is a subset of lhs
        """
        return issubset(self.rhs, self.lhs)


def powerset(iterable) -> chain:
    """
    powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def issubset(lst1: Iterable[str], lst2: Iterable[str]) -> bool:
    """
    Checks if lst1's distinct elements are inside lst2.
    """
    return set(lst1).issubset(set(lst2))


def issameset(lst1: Iterable[str], lst2: Iterable[str]) -> bool:
    """
    Checks if lst1's distinct elements are the same as lst2's.
    """
    return issubset(lst1, lst2) and issubset(lst2, lst1)


def union(lst1: Iterable[str], lst2: Iterable[str]) -> list[str]:
    """
    Returns the set union of two lists.
    """
    return list(set(lst1).union(set(lst2)))


def closure(curr_closure: list[str], fd_set: list[FD]) -> list[str]:
    """
    Finds the full closure of `curr_closure`.
    E.g. if you want the closure of {'A', 'B'}, pass ['A', 'B'] into curr_closure.
    """
    curr_closure = curr_closure.copy()
    while True:
        init_size = len(curr_closure)
        for fd in fd_set:
            if issubset(fd.lhs, curr_closure):
                curr_closure = union(fd.rhs, curr_closure)

        if len(curr_closure) == init_size:
            break

    return curr_closure


def all_closures(attrs: list[str], fd_set: list[FD]) -> dict[tuple[str], list[str]]:
    """
    Given a list of attributes and a set of functional dependencies,
    find the closure of every subset of attrs.
    """
    res = {}
    for set in powerset(attrs):
        cls = closure(list(set), fd_set)
        res[set] = cls
    return res


def get_all_superkeys(
    schema: list[str], closures_of_subsets: dict[tuple[str], list[str]]
) -> list[tuple[str]]:
    """
    attrs represents your schema, e.g R = {A, B, C, D, E}.
    cls is the dict containing all the attribute closures from all_closures().
    """
    res = []
    for subset, closure in closures_of_subsets.items():
        if issameset(schema, closure):
            res.append(subset)

    return res


def get_candidate_keys(all_superkeys: list[tuple[str]]) -> list[tuple[str]]:
    """
    all_superkeys is a list of superkeys.
    It returns only the superkeys that are also candidate keys.
    """
    all_superkeys = all_superkeys.copy()
    superkeys_to_remove: set[int] = set()

    for i in range(len(all_superkeys)):
        for j in range(i + 1, len(all_superkeys)):
            if issubset(all_superkeys[i], all_superkeys[j]):
                superkeys_to_remove.add(j)
            elif issubset(all_superkeys[j], all_superkeys[i]):
                superkeys_to_remove.add(i)

    superkeys_to_remove: list[int] = list(superkeys_to_remove)
    superkeys_to_remove.sort(reverse=True)
    for index in superkeys_to_remove:
        all_superkeys.pop(index)

    return all_superkeys


def get_prime_attributes(candidate_keys: list[tuple[str]]) -> list[str]:
    """
    Given a list of candidate keys, e.g. [('A', 'E'), ('B', 'E')],
    return a list of the distinct attributes in those keys, e.g. ['A', 'B', 'E']
    """
    att_set: set[str] = set()
    for key in candidate_keys:
        for attribute in key:
            att_set.add(attribute)

    return list(att_set)


def get_minimal_cover(fd_set: list[FD], verbose: bool = False) -> list[FD]:
    # Simplify the right hand side of fds
    fd_copy = deepcopy(fd_set)
    single_rhs_fds: list[FD] = []
    for fd in fd_set:
        for attribute in fd.rhs:
            single_rhs_fds.append(FD(fd.lhs.copy(), [attribute]))

    if verbose:
        print("Simplified rhs")
        print(single_rhs_fds)

    # Simplify the left hand side of fds
    for fd in single_rhs_fds:
        while True:
            attr_removed = False
            for i in range(len(fd.lhs)):
                attribute_to_remove = fd.lhs.pop(i)
                if issubset(fd.rhs, closure(fd.lhs, fd_copy)):
                    attr_removed = True
                    break
                else:
                    fd.lhs.insert(i, attribute_to_remove)
            if not attr_removed:
                break

    if verbose:
        print("Simplified lhs")
        print(single_rhs_fds)

    # Remove redundant fds
    while True:
        initial_size = len(single_rhs_fds)
        for i in range(len(single_rhs_fds)):
            # Take out this fd
            fd = single_rhs_fds.pop(i)

            # If the left hand side still can determine the right hand side, this fd is redundant
            if issubset(fd.rhs, closure(fd.lhs, single_rhs_fds)):
                break
            else:
                single_rhs_fds.insert(i, fd)

        if initial_size == len(single_rhs_fds):
            break

    return single_rhs_fds


def is2NF(
    prime_attributes: list[str],
    candidate_keys: list[tuple[str]],
    fd_set: list[FD],
) -> bool:
    """
    A relation R with a set of functional dependencies Σ is in 2NF, 
    if and only if for every functional dependency X → {A} ∈ Σ+:
    1. X -> {A} is trivial or
    2. A is a prime attribute or
    3. X is not a proper subset of a candidate key
    """
    result = True
    for fd in fd_set:
        # Condition 1
        if fd.is_trivial():
            continue

        # If the rhs of the fd is not a singleton, raise an error
        if len(fd.rhs) != 1:
            raise Exception("fd rhs not simple")

        # Condition 2
        if fd.rhs[0] in prime_attributes:
            continue

        # Condition 3
        is_strict_subset_of_any_candidate_key = False
        for key in candidate_keys:
            if issubset(fd.lhs, key) and not issameset(fd.lhs, key):
                is_strict_subset_of_any_candidate_key = True
                break

        if not is_strict_subset_of_any_candidate_key:
            continue

        # If you reach this point, you have not satisfied any condition.
        result = False
        print(fd, "violates 2NF")

    return result


def is3NF(
    prime_attributes: list[str],
    superkeys: list[tuple[str]],
    fd_set: list[FD],
) -> bool:
    """
    A relation R with a set of functional dependencies Σ is in 3NF, 
    if and only if for every functional dependency X → {A} ∈ Σ+:
    1. X -> {A} is trivial or
    2. X is a superkey or
    3. A is a prime attribute.
    """
    result = True
    for fd in fd_set:
        # Condition 1
        if fd.is_trivial():
            continue

        # Condition 2
        is_in_superkeys = False
        for superkey in superkeys:
            if issameset(fd.lhs, superkey):
                is_in_superkeys = True
                break
        if is_in_superkeys:
            continue

        # If the rhs of the fd is not a singleton, raise an error
        if len(fd.rhs) != 1:
            raise Exception("fd rhs not simple")

        # Condition 3
        if fd.rhs[0] in prime_attributes:
            continue

        # If you reach this point, you have not satisfied any condition.
        result = False
        print(fd, "violates 3NF")

    return result


def isBCNF(
    superkeys: list[tuple[str]],
    fd_set: list[FD],
) -> bool:
    """
    A relation R with a set of functional dependencies Σ is in BCNF, 
    if and only if for every functional dependency X → {A} ∈ Σ+:
    1. X -> {A} is trivial or
    2. X is a superkey.
    """
    result = True
    for fd in fd_set:
        # Condition 1
        if fd.is_trivial():
            continue

        # Condition 2
        is_in_superkeys = False
        for superkey in superkeys:
            if issameset(fd.lhs, superkey):
                is_in_superkeys = True
                break
        if is_in_superkeys:
            continue

        # If the rhs of the fd is not a singleton, raise an error
        if len(fd.rhs) != 1:
            raise Exception("fd rhs not simple")

        # If you reach this point, you have not satisfied any condition.
        result = False
        print(fd, "violates BCNF")

    return result


# Sample usage
a = "A"
b = "B"
c = "C"
d = "D"
e = "E"
f = "F"
g = "G"
h = "H"
i = "I"
j = "J"
k = "K"
l = "L"
m = "M"
n = "N"
o = "O"
p = "P"
q = "Q"
r = "R"
s = "S"
t = "T"
u = "U"
v = "V"
w = "W"
x = "X"
y = "Y"
z = "Z"

fd_set = [
    FD([a], [a, b, c]),
    FD([a, b], [a]),
    FD([b, c], [a, d]),
    FD([b], [a, b]),
    FD([c], [d]),
]

schema = [a, b, c, d, e]

# Tutorial: Functional Dependencies
cls: dict[tuple[str], list[str]] = all_closures(schema, fd_set)
print("All closures:")
pprint(cls)

all_superkeys: list[tuple[str]] = get_all_superkeys(schema, cls)
print("All superkeys:")
pprint(all_superkeys)

candidate_keys: list[tuple[str]] = get_candidate_keys(all_superkeys)
print("Candidate keys:")
pprint(candidate_keys)

prime_attributes: list[str] = get_prime_attributes(candidate_keys)
print("Prime attributes:")
pprint(prime_attributes)

min_cover: list[FD] = get_minimal_cover(fd_set)
print("Minimal cover:")
pprint(min_cover)


# Tutorial: Normal Forms
is2NF(prime_attributes, candidate_keys, min_cover)

is3NF(prime_attributes, all_superkeys, min_cover)

isBCNF(all_superkeys, min_cover)
