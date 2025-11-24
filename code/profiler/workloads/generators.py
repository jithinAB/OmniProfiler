"""
Data Generators for Performance Testing

Provides generators for creating test data at various scales:
- Small: ~100 items
- Medium: ~10,000 items
- Large: ~1,000,000 items
- XLarge: ~10,000,000 items
"""

import random
import string
from typing import List, Dict, Any, Literal

ScaleType = Literal['small', 'medium', 'large', 'xlarge']


class WorkloadGenerator:
    """Generate test workloads at different scales"""

    # Scale definitions
    SCALES = {
        'small': 100,
        'medium': 10_000,
        'large': 1_000_000,
        'xlarge': 10_000_000
    }

    @classmethod
    def generate_list(cls, scale: ScaleType = 'small',
                     value_range: tuple = (0, 1000),
                     randomize: bool = True) -> List[int]:
        """
        Generate a list of integers.

        Args:
            scale: Size category ('small', 'medium', 'large', 'xlarge')
            value_range: Range of values (min, max)
            randomize: If True, random values; if False, sequential

        Returns:
            List of integers

        Example:
            >>> data = WorkloadGenerator.generate_list('medium', randomize=True)
            >>> len(data)
            10000
        """
        size = cls.SCALES[scale]

        if randomize:
            return [random.randint(*value_range) for _ in range(size)]
        else:
            return list(range(size))

    @classmethod
    def generate_strings(cls, scale: ScaleType = 'small',
                        str_length: int = 10) -> List[str]:
        """
        Generate a list of random strings.

        Args:
            scale: Size category
            str_length: Length of each string

        Returns:
            List of random strings
        """
        size = cls.SCALES[scale]
        chars = string.ascii_letters + string.digits

        return [''.join(random.choices(chars, k=str_length)) for _ in range(size)]

    @classmethod
    def generate_dict_list(cls, scale: ScaleType = 'small',
                          num_fields: int = 5) -> List[Dict[str, Any]]:
        """
        Generate a list of dictionaries.

        Args:
            scale: Size category
            num_fields: Number of fields per dict

        Returns:
            List of dictionaries

        Example:
            >>> data = WorkloadGenerator.generate_dict_list('small', num_fields=3)
            >>> len(data)
            100
            >>> 'field_0' in data[0]
            True
        """
        size = cls.SCALES[scale]
        result = []

        for i in range(size):
            record = {
                f'field_{j}': random.randint(0, 1000)
                for j in range(num_fields)
            }
            record['id'] = i
            result.append(record)

        return result

    @classmethod
    def generate_nested_structure(cls, depth: int = 3,
                                  width: int = 5,
                                  max_items: int = 1000) -> Dict[str, Any]:
        """
        Generate nested dict/list structures.

        Args:
            depth: How deep to nest
            width: How many items at each level
            max_items: Maximum total items (prevents explosion)

        Returns:
            Nested dictionary structure

        Example:
            >>> data = WorkloadGenerator.generate_nested_structure(depth=2, width=3)
            >>> isinstance(data, dict)
            True
        """
        items_created = [0]  # Mutable counter

        def _build_nested(current_depth):
            if current_depth == 0 or items_created[0] >= max_items:
                items_created[0] += 1
                return random.randint(0, 100)

            result = {}
            for i in range(min(width, max_items - items_created[0])):
                key = f'level_{current_depth}_item_{i}'
                result[key] = _build_nested(current_depth - 1)

                if items_created[0] >= max_items:
                    break

            return result

        return _build_nested(depth)

    @classmethod
    def generate_text_corpus(cls, scale: ScaleType = 'small',
                            words_per_doc: int = 100) -> List[str]:
        """
        Generate text documents.

        Args:
            scale: Number of documents
            words_per_doc: Words per document

        Returns:
            List of text documents
        """
        size = cls.SCALES[scale]

        # Sample words for corpus
        sample_words = [
            'the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog',
            'python', 'performance', 'profiling', 'optimization', 'algorithm',
            'data', 'structure', 'analysis', 'computation', 'memory', 'cpu'
        ]

        documents = []
        for _ in range(size):
            doc = ' '.join(random.choices(sample_words, k=words_per_doc))
            documents.append(doc)

        return documents

    @classmethod
    def generate_matrix(cls, scale: ScaleType = 'small') -> List[List[float]]:
        """
        Generate a 2D matrix.

        Args:
            scale: Determines matrix size (sqrt of scale)

        Returns:
            2D matrix

        Example:
            >>> matrix = WorkloadGenerator.generate_matrix('small')
            >>> len(matrix)
            10
            >>> len(matrix[0])
            10
        """
        size = cls.SCALES[scale]
        # Matrix size is sqrt of total elements
        dim = int(size ** 0.5)

        return [[random.random() for _ in range(dim)] for _ in range(dim)]

    @classmethod
    def generate_sorted_data(cls, scale: ScaleType = 'small',
                            reverse: bool = False) -> List[int]:
        """
        Generate sorted data (best/worst case for sorting algorithms).

        Args:
            scale: Size category
            reverse: If True, generate reverse-sorted (worst case)

        Returns:
            Sorted list
        """
        size = cls.SCALES[scale]
        data = list(range(size))

        if reverse:
            data.reverse()

        return data

    @classmethod
    def generate_nearly_sorted(cls, scale: ScaleType = 'small',
                               swap_percentage: float = 0.1) -> List[int]:
        """
        Generate nearly-sorted data.

        Args:
            scale: Size category
            swap_percentage: Fraction of elements to swap

        Returns:
            Nearly-sorted list
        """
        size = cls.SCALES[scale]
        data = list(range(size))

        # Swap some elements
        num_swaps = int(size * swap_percentage)
        for _ in range(num_swaps):
            i, j = random.sample(range(size), 2)
            data[i], data[j] = data[j], data[i]

        return data

    @classmethod
    def get_size(cls, scale: ScaleType) -> int:
        """Get the numeric size for a scale category"""
        return cls.SCALES[scale]
