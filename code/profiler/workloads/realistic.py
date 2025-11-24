"""
Realistic Data Generators

Uses Faker to generate production-like data for realistic profiling scenarios:
- E-commerce orders
- User/customer records
- Database transactions
- Log entries
- API requests/responses
"""

from faker import Faker
from typing import List, Dict, Any, Literal
import random
from datetime import datetime, timedelta

ScaleType = Literal['small', 'medium', 'large', 'xlarge']


class RealisticDataGenerator:
    """Generate production-like data using Faker"""

    # Scale definitions (same as WorkloadGenerator)
    SCALES = {
        'small': 100,
        'medium': 10_000,
        'large': 1_000_000,
        'xlarge': 10_000_000
    }

    def __init__(self, locale: str = 'en_US', seed: int = None):
        """
        Initialize the generator.

        Args:
            locale: Faker locale (e.g., 'en_US', 'en_GB', 'fr_FR')
            seed: Random seed for reproducible data
        """
        self.fake = Faker(locale)
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

    # ===== E-Commerce Data =====

    def generate_ecommerce_orders(self, scale: ScaleType = 'small') -> List[Dict[str, Any]]:
        """
        Generate realistic e-commerce orders.

        Returns:
            List of order dictionaries with customers, items, prices, addresses

        Example:
            >>> gen = RealisticDataGenerator()
            >>> orders = gen.generate_ecommerce_orders('small')
            >>> len(orders)
            100
            >>> 'customer_name' in orders[0]
            True
        """
        size = self.SCALES[scale]
        orders = []

        for i in range(size):
            num_items = random.randint(1, 5)
            items = []
            total = 0.0

            for _ in range(num_items):
                price = round(random.uniform(5.99, 499.99), 2)
                quantity = random.randint(1, 3)
                items.append({
                    'product_name': self.fake.catch_phrase(),
                    'sku': self.fake.bothify(text='???-########'),
                    'price': price,
                    'quantity': quantity,
                    'subtotal': round(price * quantity, 2)
                })
                total += price * quantity

            order = {
                'order_id': f'ORD-{i:08d}',
                'customer_id': f'CUST-{random.randint(1, size // 10):06d}',
                'customer_name': self.fake.name(),
                'customer_email': self.fake.email(),
                'order_date': self.fake.date_time_between(start_date='-1y', end_date='now').isoformat(),
                'items': items,
                'subtotal': round(total, 2),
                'tax': round(total * 0.08, 2),
                'shipping': round(random.uniform(0, 15.99), 2),
                'total': round(total * 1.08 + random.uniform(0, 15.99), 2),
                'status': random.choice(['pending', 'processing', 'shipped', 'delivered', 'cancelled']),
                'shipping_address': {
                    'street': self.fake.street_address(),
                    'city': self.fake.city(),
                    'state': self.fake.state_abbr(),
                    'zip': self.fake.zipcode(),
                    'country': self.fake.country_code()
                },
                'payment_method': random.choice(['credit_card', 'debit_card', 'paypal', 'bank_transfer'])
            }
            orders.append(order)

        return orders

    # ===== User/Customer Data =====

    def generate_user_records(self, scale: ScaleType = 'small',
                             include_pii: bool = True) -> List[Dict[str, Any]]:
        """
        Generate realistic user/customer records.

        Args:
            scale: Size category
            include_pii: Include personally identifiable information

        Returns:
            List of user dictionaries
        """
        size = self.SCALES[scale]
        users = []

        for i in range(size):
            user = {
                'user_id': f'USR-{i:08d}',
                'username': self.fake.user_name(),
                'email': self.fake.email(),
                'created_at': self.fake.date_time_between(start_date='-2y', end_date='now').isoformat(),
                'last_login': self.fake.date_time_between(start_date='-30d', end_date='now').isoformat(),
                'is_active': random.choice([True, True, True, False]),  # 75% active
                'role': random.choice(['user', 'user', 'user', 'premium', 'admin']),
                'preferences': {
                    'newsletter': random.choice([True, False]),
                    'notifications': random.choice([True, False]),
                    'theme': random.choice(['light', 'dark', 'auto'])
                }
            }

            if include_pii:
                user.update({
                    'full_name': self.fake.name(),
                    'date_of_birth': self.fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
                    'phone': self.fake.phone_number(),
                    'address': {
                        'street': self.fake.street_address(),
                        'city': self.fake.city(),
                        'state': self.fake.state(),
                        'zip': self.fake.zipcode()
                    },
                    'ssn': self.fake.ssn()
                })

            users.append(user)

        return users

    # ===== Database Transaction Records =====

    def generate_database_transactions(self, scale: ScaleType = 'small') -> List[Dict[str, Any]]:
        """
        Generate realistic database transaction records.

        Returns:
            List of transaction dictionaries (INSERT, UPDATE, DELETE, SELECT)
        """
        size = self.SCALES[scale]
        transactions = []

        tables = ['users', 'orders', 'products', 'inventory', 'customers', 'payments']
        operations = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        operation_weights = [60, 20, 15, 5]  # SELECT is most common

        for i in range(size):
            operation = random.choices(operations, weights=operation_weights)[0]
            table = random.choice(tables)
            duration_ms = random.uniform(0.1, 100) if operation == 'SELECT' else random.uniform(1, 500)

            transaction = {
                'transaction_id': f'TXN-{i:010d}',
                'timestamp': self.fake.date_time_between(start_date='-7d', end_date='now').isoformat(),
                'operation': operation,
                'table': table,
                'duration_ms': round(duration_ms, 2),
                'rows_affected': random.randint(1, 1000) if operation != 'DELETE' else random.randint(1, 10),
                'user_id': f'USR-{random.randint(1, 10000):08d}',
                'connection_id': random.randint(1, 50),
                'status': random.choice(['success', 'success', 'success', 'error']),  # 75% success
            }

            if transaction['status'] == 'error':
                transaction['error_code'] = random.choice([
                    'DEADLOCK_DETECTED',
                    'TIMEOUT',
                    'CONSTRAINT_VIOLATION',
                    'PERMISSION_DENIED'
                ])

            transactions.append(transaction)

        return transactions

    # ===== Log Entries =====

    def generate_log_entries(self, scale: ScaleType = 'small',
                            log_type: str = 'application') -> List[Dict[str, Any]]:
        """
        Generate realistic log file entries.

        Args:
            scale: Size category
            log_type: 'application', 'access', 'error', 'audit'

        Returns:
            List of log entry dictionaries
        """
        size = self.SCALES[scale]
        logs = []

        levels = {
            'application': ['DEBUG', 'INFO', 'INFO', 'INFO', 'WARNING', 'ERROR'],
            'access': ['INFO'],
            'error': ['ERROR', 'CRITICAL'],
            'audit': ['INFO', 'WARNING']
        }

        messages = {
            'application': [
                'User authentication successful',
                'Database connection established',
                'Cache miss for key',
                'API request processed',
                'Background job completed',
                'Configuration reloaded',
                'Connection pool exhausted',
                'Invalid input received'
            ],
            'access': [
                'GET /api/users',
                'POST /api/orders',
                'PUT /api/products',
                'DELETE /api/sessions'
            ],
            'error': [
                'Database connection failed',
                'Null pointer exception',
                'Out of memory error',
                'File not found',
                'Permission denied'
            ],
            'audit': [
                'User login',
                'User logout',
                'Data export',
                'Configuration change',
                'Permission grant'
            ]
        }

        for i in range(size):
            level = random.choice(levels[log_type])
            message = random.choice(messages[log_type])

            log = {
                'timestamp': self.fake.date_time_between(start_date='-7d', end_date='now').isoformat(),
                'level': level,
                'logger': f'{log_type}.{random.choice(["auth", "database", "api", "core"])}',
                'message': message,
                'thread_id': random.randint(1000, 9999),
            }

            # Add extra context for errors
            if level in ['ERROR', 'CRITICAL']:
                log['exception'] = random.choice([
                    'ValueError',
                    'TypeError',
                    'ConnectionError',
                    'TimeoutError'
                ])
                log['stack_trace'] = f'  File "app.py", line {random.randint(1, 500)}, in main'

            # Add request context for access logs
            if log_type == 'access':
                log['method'] = message.split()[0]
                log['path'] = message.split()[1]
                log['status_code'] = random.choice([200, 200, 200, 201, 204, 400, 404, 500])
                log['response_time_ms'] = round(random.uniform(1, 500), 2)
                log['ip_address'] = self.fake.ipv4()
                log['user_agent'] = self.fake.user_agent()

            logs.append(log)

        return logs

    # ===== API Request/Response Data =====

    def generate_api_requests(self, scale: ScaleType = 'small') -> List[Dict[str, Any]]:
        """
        Generate realistic API request/response data.

        Returns:
            List of API request/response dictionaries
        """
        size = self.SCALES[scale]
        requests = []

        endpoints = [
            ('GET', '/api/v1/users', [200, 200, 200, 404]),
            ('POST', '/api/v1/users', [201, 201, 400, 422]),
            ('GET', '/api/v1/orders', [200, 200, 401, 403]),
            ('PUT', '/api/v1/orders/{id}', [200, 200, 404, 422]),
            ('DELETE', '/api/v1/orders/{id}', [204, 204, 404, 403]),
            ('GET', '/api/v1/products', [200, 200, 200, 500]),
            ('POST', '/api/v1/auth/login', [200, 200, 401, 429]),
        ]

        for i in range(size):
            method, endpoint, status_codes = random.choice(endpoints)
            status_code = random.choice(status_codes)

            # Response time varies by method and status
            if method == 'GET' and status_code == 200:
                response_time = random.uniform(10, 200)
            elif method in ['POST', 'PUT', 'DELETE'] and status_code in [200, 201, 204]:
                response_time = random.uniform(50, 500)
            else:  # Errors are usually faster
                response_time = random.uniform(5, 50)

            request = {
                'request_id': self.fake.uuid4(),
                'timestamp': self.fake.date_time_between(start_date='-24h', end_date='now').isoformat(),
                'method': method,
                'endpoint': endpoint.replace('{id}', str(random.randint(1, 10000))),
                'status_code': status_code,
                'response_time_ms': round(response_time, 2),
                'ip_address': self.fake.ipv4(),
                'user_agent': self.fake.user_agent(),
                'user_id': f'USR-{random.randint(1, 1000):08d}' if status_code not in [401, 403] else None,
            }

            # Add query params for GET requests
            if method == 'GET':
                request['query_params'] = {
                    'page': random.randint(1, 10),
                    'limit': random.choice([10, 25, 50, 100])
                }

            # Add body for POST/PUT
            if method in ['POST', 'PUT']:
                request['request_size_bytes'] = random.randint(100, 10000)
                request['response_size_bytes'] = random.randint(50, 5000)

            requests.append(request)

        return requests

    # ===== Time-Series Data =====

    def generate_timeseries_metrics(self, scale: ScaleType = 'small',
                                    interval_seconds: int = 60) -> List[Dict[str, Any]]:
        """
        Generate time-series metrics data (CPU, memory, requests, etc.).

        Args:
            scale: Size category (number of data points)
            interval_seconds: Time between measurements

        Returns:
            List of metric dictionaries with timestamps
        """
        size = self.SCALES[scale]
        metrics = []

        start_time = datetime.now() - timedelta(seconds=size * interval_seconds)

        for i in range(size):
            timestamp = start_time + timedelta(seconds=i * interval_seconds)

            # Simulate realistic patterns (daily cycles, spikes)
            hour = timestamp.hour
            base_cpu = 30 + 20 * abs(hour - 12) / 12  # Higher during business hours
            base_memory = 60 + 10 * random.random()

            # Add random spikes
            spike = random.random() < 0.05  # 5% chance of spike
            cpu_multiplier = random.uniform(2, 4) if spike else 1
            mem_multiplier = random.uniform(1.5, 2.5) if spike else 1

            metric = {
                'timestamp': timestamp.isoformat(),
                'cpu_percent': min(100, round(base_cpu * cpu_multiplier + random.uniform(-5, 5), 2)),
                'memory_percent': min(100, round(base_memory * mem_multiplier + random.uniform(-3, 3), 2)),
                'disk_io_read_mb': round(random.uniform(0, 50), 2),
                'disk_io_write_mb': round(random.uniform(0, 30), 2),
                'network_rx_mb': round(random.uniform(0, 100), 2),
                'network_tx_mb': round(random.uniform(0, 80), 2),
                'active_connections': random.randint(10, 500),
                'request_rate': random.randint(50, 5000),
                'error_rate': round(random.uniform(0, 5), 2)
            }

            metrics.append(metric)

        return metrics

    # ===== Helper Methods =====

    @classmethod
    def get_size(cls, scale: ScaleType) -> int:
        """Get the numeric size for a scale category"""
        return cls.SCALES[scale]

    def generate_mixed_workload(self, scale: ScaleType = 'small') -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate a mixed workload with multiple data types.

        Returns:
            Dictionary with keys: 'orders', 'users', 'logs', 'api_requests'
        """
        return {
            'orders': self.generate_ecommerce_orders(scale),
            'users': self.generate_user_records(scale),
            'database_transactions': self.generate_database_transactions(scale),
            'logs': self.generate_log_entries(scale),
            'api_requests': self.generate_api_requests(scale),
            'metrics': self.generate_timeseries_metrics(scale)
        }
