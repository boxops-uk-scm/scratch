import unittest

from chimera import Chimera, memoize, memoize_fix


class ChimeraTest(unittest.TestCase):
    def test_entries_are_computed_once_and_only_on_demand(self):
        calls = []

        def square(n):
            calls.append(n)
            return n * n

        table = Chimera(square)
        self.assertEqual([table[n] for n in [5, 0, 5, 1, 2 ** 20]], [25, 0, 25, 1, 2 ** 40])
        self.assertEqual(calls, [5, 0, 1, 2 ** 20])

    def test_every_index_up_to_a_power_of_two_lands_in_its_own_slot(self):
        table = memoize(lambda n: n)
        self.assertEqual([table(n) for n in range(1025)], list(range(1025)))

    def test_only_the_buckets_touched_are_allocated(self):
        table = Chimera(lambda n: n)
        table[2 ** 10]
        self.assertEqual([b is not None for b in table._buckets], [False] * 11 + [True])

    def test_negative_index(self):
        with self.assertRaises(IndexError):
            Chimera(lambda n: n)[-1]

    def test_self_dependency_is_reported(self):
        table = memoize_fix(lambda rec, n: rec(n))
        with self.assertRaisesRegex(ValueError, "entry 3 depends on itself"):
            table[3]

    def test_a_failed_entry_can_be_retried(self):
        attempts = []

        def flaky(n):
            attempts.append(n)
            if len(attempts) == 1:
                raise RuntimeError("first time")
            return n

        table = Chimera(flaky)
        with self.assertRaises(RuntimeError):
            table[4]
        self.assertEqual(table[4], 4)


class MemoizeFixTest(unittest.TestCase):
    def test_fibonacci_computes_each_entry_once(self):
        calls = []

        def fib(rec, n):
            calls.append(n)
            return n if n < 2 else rec(n - 1) + rec(n - 2)

        table = memoize_fix(fib)
        self.assertEqual(table(200), 280571172992510140037611932413038677189525)
        self.assertEqual(sorted(calls), list(range(201)))

    def test_recursion_into_larger_indices(self):
        # Collatz stopping times recurse on 3n + 1, so entries are filled far
        # beyond the indices asked for, in no particular order.
        def steps(rec, n):
            if n == 1:
                return 0
            return 1 + rec(n // 2 if n % 2 == 0 else 3 * n + 1)

        def plain(n):
            count = 0
            while n != 1:
                n = n // 2 if n % 2 == 0 else 3 * n + 1
                count += 1
            return count

        table = memoize_fix(steps)
        self.assertEqual([table(n) for n in range(1, 2000)], [plain(n) for n in range(1, 2000)])


if __name__ == "__main__":
    unittest.main()
