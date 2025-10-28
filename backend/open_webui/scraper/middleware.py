"""
Middleware for Policy Scanner scraper framework.

This module provides rate limiting, retry logic with exponential backoff,
and anti-bot detection handling for HTTP requests.
"""

import asyncio
import logging
import random
import time
from typing import Optional, List, Callable, Any
from datetime import datetime, timedelta

import aiohttp


logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for async requests.

    Implements a token bucket algorithm to limit the rate of HTTP requests
    to avoid overloading target servers and prevent bot detection.
    """

    def __init__(self, requests_per_second: int = 10):
        """
        Initialize rate limiter.

        Args:
            requests_per_second: Maximum number of requests per second
        """
        self.rate = requests_per_second
        self.tokens = requests_per_second
        self.max_tokens = requests_per_second
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

        logger.debug(f"RateLimiter initialized: {requests_per_second} req/s")

    async def acquire(self, tokens: int = 1):
        """
        Acquire token(s) from the bucket.

        This method will block until sufficient tokens are available.

        Args:
            tokens: Number of tokens to acquire (default: 1)
        """
        async with self._lock:
            while self.tokens < tokens:
                # Refill tokens based on elapsed time
                now = time.monotonic()
                elapsed = now - self.last_update
                self.tokens = min(
                    self.max_tokens,
                    self.tokens + elapsed * self.rate
                )
                self.last_update = now

                if self.tokens < tokens:
                    # Calculate wait time for next token
                    wait_time = (tokens - self.tokens) / self.rate
                    await asyncio.sleep(wait_time)

            # Consume tokens
            self.tokens -= tokens
            self.last_update = time.monotonic()

    def reset(self):
        """Reset the rate limiter to full capacity."""
        self.tokens = self.max_tokens
        self.last_update = time.monotonic()


class ExponentialBackoff:
    """
    Exponential backoff strategy for retries.

    Calculates wait time with jitter to avoid thundering herd problem.
    """

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize exponential backoff.

        Args:
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential calculation
            jitter: Whether to add random jitter
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            float: Delay in seconds
        """
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        if self.jitter:
            # Add random jitter (0-25% of delay)
            delay += delay * random.uniform(0, 0.25)

        return delay

    async def wait(self, attempt: int):
        """
        Wait for the calculated delay.

        Args:
            attempt: Attempt number (0-indexed)
        """
        delay = self.calculate_delay(attempt)
        logger.debug(f"Backing off for {delay:.2f}s (attempt {attempt})")
        await asyncio.sleep(delay)


class RetryMiddleware:
    """
    Retry middleware with exponential backoff.

    Automatically retries failed HTTP requests with configurable retry logic.
    """

    def __init__(
        self,
        max_retries: int = 3,
        retry_on_status: Optional[List[int]] = None,
        backoff_strategy: Optional[ExponentialBackoff] = None
    ):
        """
        Initialize retry middleware.

        Args:
            max_retries: Maximum number of retry attempts
            retry_on_status: HTTP status codes to retry on
            backoff_strategy: Custom backoff strategy
        """
        self.max_retries = max_retries
        self.retry_on_status = retry_on_status or [429, 500, 502, 503, 504]
        self.backoff = backoff_strategy or ExponentialBackoff()

    async def request(
        self,
        method: str,
        url: str,
        session: aiohttp.ClientSession,
        on_retry: Optional[Callable[[int], None]] = None,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            session: aiohttp session
            on_retry: Callback function called on retry (receives attempt number)
            **kwargs: Additional arguments for aiohttp request

        Returns:
            aiohttp.ClientResponse

        Raises:
            aiohttp.ClientError: If all retries fail
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await session.request(method, url, **kwargs)

                # Check if we should retry based on status code
                if response.status in self.retry_on_status and attempt < self.max_retries:
                    logger.warning(
                        f"Request failed with status {response.status}, "
                        f"retrying (attempt {attempt + 1}/{self.max_retries})"
                    )

                    if on_retry:
                        on_retry(attempt)

                    # Wait before retry
                    await self.backoff.wait(attempt)
                    continue

                return response

            except aiohttp.ClientError as e:
                last_exception = e

                if attempt < self.max_retries:
                    logger.warning(
                        f"Request failed with error: {e}, "
                        f"retrying (attempt {attempt + 1}/{self.max_retries})"
                    )

                    if on_retry:
                        on_retry(attempt)

                    await self.backoff.wait(attempt)
                else:
                    logger.error(f"Request failed after {self.max_retries} retries")

        # If we get here, all retries failed
        raise last_exception or aiohttp.ClientError("All retries failed")


class UserAgentRotator:
    """
    Rotate User-Agent headers to avoid bot detection.

    Provides a pool of realistic User-Agent strings for browsers.
    """

    # Common desktop browser User-Agents
    USER_AGENTS = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',

        # Firefox on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) '
        'Gecko/20100101 Firefox/121.0',

        # Edge on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',

        # Chrome on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',

        # Firefox on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) '
        'Gecko/20100101 Firefox/121.0',

        # Safari on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
        '(KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]

    def __init__(self, custom_agents: Optional[List[str]] = None):
        """
        Initialize User-Agent rotator.

        Args:
            custom_agents: Optional list of custom User-Agent strings
        """
        self.agents = custom_agents or self.USER_AGENTS
        self._index = 0

    def get_random(self) -> str:
        """
        Get a random User-Agent string.

        Returns:
            str: User-Agent string
        """
        return random.choice(self.agents)

    def get_next(self) -> str:
        """
        Get next User-Agent string in rotation.

        Returns:
            str: User-Agent string
        """
        agent = self.agents[self._index]
        self._index = (self._index + 1) % len(self.agents)
        return agent


class BotDetectionHandler:
    """
    Handle bot detection and blocking.

    Detects common bot detection patterns and implements countermeasures.
    """

    def __init__(self, user_agent_rotator: Optional[UserAgentRotator] = None):
        """
        Initialize bot detection handler.

        Args:
            user_agent_rotator: User-Agent rotation strategy
        """
        self.ua_rotator = user_agent_rotator or UserAgentRotator()
        self.block_count = 0
        self.last_block_time: Optional[datetime] = None

    def is_blocked(self, response: aiohttp.ClientResponse) -> bool:
        """
        Check if response indicates bot blocking.

        Args:
            response: HTTP response

        Returns:
            bool: True if blocked
        """
        # Check status codes
        if response.status == 403:  # Forbidden
            return True
        if response.status == 429:  # Too Many Requests
            return True

        # Check URL for CAPTCHA
        if 'captcha' in response.url.path.lower():
            return True

        return False

    async def handle_block(
        self,
        response: aiohttp.ClientResponse,
        attempt: int
    ) -> dict:
        """
        Handle bot blocking by implementing countermeasures.

        Args:
            response: Blocked response
            attempt: Attempt number

        Returns:
            dict: Updated headers to use for retry
        """
        self.block_count += 1
        self.last_block_time = datetime.now()

        logger.warning(
            f"Bot detection triggered (status {response.status}), "
            f"implementing countermeasures (attempt {attempt})"
        )

        headers = {}

        if attempt == 0:
            # First attempt: Rotate User-Agent
            headers['User-Agent'] = self.ua_rotator.get_next()
            logger.debug("Rotated User-Agent")

        elif attempt == 1:
            # Second attempt: Add more realistic headers
            headers['User-Agent'] = self.ua_rotator.get_random()
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            })
            logger.debug("Added realistic browser headers")

        else:
            # Third attempt: Longer backoff
            wait_time = 2 ** attempt * 30  # Exponential backoff in seconds
            logger.warning(f"Blocked, waiting {wait_time}s before retry")
            await asyncio.sleep(wait_time)

        return headers


class RobotsTxtParser:
    """
    Parse and respect robots.txt directives.

    Implements basic robots.txt parsing to respect crawl-delay and disallow rules.
    """

    def __init__(self):
        """Initialize robots.txt parser."""
        self.crawl_delay: Optional[float] = None
        self.disallowed_paths: List[str] = []
        self._cache: dict = {}

    async def fetch(self, base_url: str, session: aiohttp.ClientSession) -> bool:
        """
        Fetch and parse robots.txt from base URL.

        Args:
            base_url: Base URL of the website
            session: aiohttp session

        Returns:
            bool: True if robots.txt found and parsed
        """
        if base_url in self._cache:
            return True

        robots_url = f"{base_url.rstrip('/')}/robots.txt"

        try:
            async with session.get(robots_url) as response:
                if response.status != 200:
                    logger.debug(f"No robots.txt found at {robots_url}")
                    return False

                text = await response.text()
                self._parse(text)
                self._cache[base_url] = True
                logger.info(f"Parsed robots.txt: crawl_delay={self.crawl_delay}")
                return True

        except Exception as e:
            logger.debug(f"Failed to fetch robots.txt: {e}")
            return False

    def _parse(self, text: str):
        """
        Parse robots.txt content.

        Args:
            text: robots.txt content
        """
        for line in text.split('\n'):
            line = line.strip().lower()

            if not line or line.startswith('#'):
                continue

            if line.startswith('crawl-delay:'):
                try:
                    delay = float(line.split(':', 1)[1].strip())
                    self.crawl_delay = delay
                except ValueError:
                    pass

            elif line.startswith('disallow:'):
                path = line.split(':', 1)[1].strip()
                if path:
                    self.disallowed_paths.append(path)

    def is_allowed(self, path: str) -> bool:
        """
        Check if path is allowed by robots.txt.

        Args:
            path: URL path to check

        Returns:
            bool: True if allowed
        """
        for disallowed in self.disallowed_paths:
            if path.startswith(disallowed):
                return False
        return True

    def get_crawl_delay(self) -> Optional[float]:
        """
        Get crawl delay from robots.txt.

        Returns:
            Optional[float]: Crawl delay in seconds, or None
        """
        return self.crawl_delay
