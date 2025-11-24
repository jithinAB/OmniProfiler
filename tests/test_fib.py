#!/usr/bin/env python3
"""
Fibonacci Application
---------------------
A simple command-line tool to:
 - Generate a Fibonacci sequence
 - Compute the nth Fibonacci number
 - Check if a number is in the Fibonacci sequence

Usage:
    python fibonacci_app.py

Author: ChatGPT (GPT-5)
"""

import sys

def fibonacci_sequence(n):
    """Generate a Fibonacci sequence up to n terms."""
    if n <= 0:
        return []
    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]

def fibonacci_nth(n):
    """Return the nth Fibonacci number (0-indexed)."""
    if n < 0:
        raise ValueError("n must be non-negative.")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def is_fibonacci(num):
    """Check if a number belongs to the Fibonacci sequence."""
    if num < 0:
        return False
    a, b = 0, 1
    while b < num:
        a, b = b, a + b
    return b == num or num == 0

def menu():
    print("\n=== Fibonacci Application ===")
    print("1. Generate Fibonacci sequence")
    print("2. Find nth Fibonacci number")
    print("3. Check if a number is a Fibonacci number")
    print("4. Exit")

def main():
    while True:
        menu()
        try:
            choice = int(input("Enter your choice (1-4): ").strip())
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 4.")
            continue

        if choice == 1:
            try:
                n = int(input("How many terms? ").strip())
                print(f"Fibonacci sequence ({n} terms): {fibonacci_sequence(n)}")
            except ValueError:
                print("Please enter a valid integer.")
        elif choice == 2:
            try:
                n = int(input("Enter n (0-indexed): ").strip())
                print(f"The {n}th Fibonacci number is {fibonacci_nth(n)}")
            except ValueError:
                print("Please enter a valid integer.")
        elif choice == 3:
            try:
                num = int(input("Enter number to check: ").strip())
                if is_fibonacci(num):
                    print(f"{num} IS a Fibonacci number.")
                else:
                    print(f"{num} is NOT a Fibonacci number.")
            except ValueError:
                print("Please enter a valid integer.")
        elif choice == 4:
            print("Exiting. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
