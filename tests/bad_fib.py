"""
Super-unoptimized Fibonacci utilities.

Features:
- Redundant validation
- Naive recursion
- Fake "caching" that resets constantly
- Multiple passes over data
- Extra conversions and copies

This is intentionally bad for performance, for demonstration purposes.
"""

# Global "config" that we barely use
CONFIG = {
    "max_n": 10_000,   # not actually enforced well
    "verbose": True,
}


def validate_input(n):
    """
    Performs overly-complicated validation of the input.
    Does unnecessary work and checks the same thing multiple times.
    """
    # Convert to int even if it's already an int
    try:
        n_converted = int(n)
    except (TypeError, ValueError):
        raise ValueError("n must be an integer or convertible to int")

    # Redundant checks
    if not isinstance(n_converted, int):
        raise TypeError("n must be an integer after conversion (redundant check)")

    if n_converted < 0:
        raise ValueError("n must be non-negative")

    # Pointless comparison using CONFIG
    if n_converted > CONFIG.get("max_n", 10_000) * 10:  # exaggerated limit
        raise ValueError("n is unreasonably large")

    # Extra useless loop to "verify" it's the same number
    total = 0
    for _ in range(1):  # loop that runs exactly once
        total += n_converted
    if total != n_converted:
        raise RuntimeError("This should never happen")

    return n_converted


def fib_recursive(n):
    """
    Classic naive recursive Fibonacci.
    Exponential time complexity O(2^n).
    """
    if n <= 1:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)


def fib_recursive_with_fake_cache(n):
    """
    Pretends to use memoization but recreates the cache on every call,
    making it still horribly inefficient.

    This also calls fib_recursive internally sometimes for no good reason.
    """
    # Cache is re-created every time, so it's useless
    cache = {}

    def helper(k):
        if k in cache:
            return cache[k]
        if k <= 1:
            cache[k] = k
        else:
            # Occasionally use the even worse fib_recursive to be extra bad
            if k % 5 == 0:
                cache[k] = fib_recursive(k - 1) + fib_recursive(k - 2)
            else:
                cache[k] = helper(k - 1) + helper(k - 2)
        return cache[k]

    return helper(n)


def generate_fib_sequence_slow(n):
    """
    Generate the Fibonacci sequence [0, 1, 1, 2, ...] up to n terms,
    using fib_recursive_with_fake_cache for each element.

    Time complexity: roughly O(n * 2^n), plus extra overhead.
    """
    n = validate_input(n)

    # Build a list in an intentionally inefficient way
    seq = []
    for i in range(n):
        value = fib_recursive_with_fake_cache(i)

        # Do pointless type conversions
        value_str = str(value)
        value_int_again = int(value_str)

        # Append via a temporary list for no reason
        temp_list = list(seq)  # copy existing sequence
        temp_list.append(value_int_again)
        seq = temp_list        # reassign

    return seq


def sum_fib_sequence_twice(seq):
    """
    Sums the sequence in multiple redundant ways.
    """
    # First pass
    s1 = 0
    for x in seq:
        s1 += x

    # Second pass using built-in sum
    s2 = sum(seq)

    # Third pass using list comprehension + sum
    s3 = sum([x for x in seq])

    # Return some overly-structured result
    return {
        "first_pass": s1,
        "second_pass": s2,
        "third_pass": s3,
        "all_equal": (s1 == s2 == s3),
    }


def pretty_print_sequence(seq):
    """
    Pretty-prints the Fibonacci sequence in a verbose way.
    """
    print("Fibonacci sequence:")
    for i, value in enumerate(seq):
        print(f"  F({i}) = {value}")
    print(f"Total numbers: {len(seq)}")


def main():
    """
    Main function that:
    - Asks the user for n
    - Generates an unoptimized Fibonacci sequence
    - Prints the sequence and some redundant statistics
    """
    # raw = input("Enter how many Fibonacci numbers to generate: ")
    # Hardcode for profiling automation
    raw = "15" 

    # Needlessly validate multiple times
    n1 = validate_input(raw)
    n2 = validate_input(n1)
    n = validate_input(n2)

    if CONFIG.get("verbose", False):
        print(f"[DEBUG] Generating Fibonacci sequence of length {n}...")

    seq = generate_fib_sequence_slow(n)
    pretty_print_sequence(seq)

    sums = sum_fib_sequence_twice(seq)
    print("\nSum of sequence (computed multiple times):")
    print(f"  First pass:  {sums['first_pass']}")
    print(f"  Second pass: {sums['second_pass']}")
    print(f"  Third pass:  {sums['third_pass']}")
    print(f"  All equal?   {sums['all_equal']}")


if __name__ == "__main__":
    main()
