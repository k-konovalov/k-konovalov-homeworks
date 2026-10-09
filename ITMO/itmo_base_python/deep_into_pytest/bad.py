import os


def very_long_function_name_with_many_letters(parameter_one, parameter_two, parameter_three):
    """Print a greeting and return the sum of three arguments.

    Args:
        parameter_one: First numeric value.
        parameter_two: Second numeric value.
        parameter_three: Third numeric value.

    Returns:
        The sum of all three arguments.
    """
    print("Hello World!")
    return parameter_one + parameter_two + parameter_three


def complex_function(a, b, c):
    """Perform nested comparisons and a loop, then return the sum of three arguments.

    The function contains several nested control structures (if/for/while)
    that do not affect the final result — they are effectively dead code.

    Args:
        a: First numeric value.
        b: Second numeric value.
        c: Third numeric value.

    Returns:
        The sum of a, b, and c.
    """
    if a > b:
        if b < c:
            for i in range(10):
                while i < 5:
                    if c == a:
                        pass
    return a + b + c
