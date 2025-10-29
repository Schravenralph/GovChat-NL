"""
Unit tests for rate limiting and middleware functionality.
"""

import pytest
import asyncio
import time
from datetime import datetime

from open_webui.scraper.middleware import (
    RateLimiter,
    ExponentialBackoff,
    RetryMiddleware,
    UserAgentRotator,
    BotDetectionHandler,
    RobotsTxtParser,
)


class TestRateLimiter:
    """Test rate limiter functionality."""

    @pytest.mark.asyncio
    async def test_rate_limiter_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests_per_second=10)

        assert limiter.rate == 10
        assert limiter.tokens == 10
        assert limiter.max_tokens == 10

    @pytest.mark.asyncio
    async def test_rate_limiter_single_request(self):
        """Test acquiring single token."""
        limiter = RateLimiter(requests_per_second=10)

        start_time = time.monotonic()
        await limiter.acquire(1)
        elapsed = time.monotonic() - start_time

        # Should be nearly instant
        assert elapsed < 0.1
        assert limiter.tokens == 9

    @pytest.mark.asyncio
    async def test_rate_limiter_multiple_requests(self):
        """Test acquiring multiple tokens."""
        limiter = RateLimiter(requests_per_second=5)

        # Acquire all tokens
        for _ in range(5):
            await limiter.acquire(1)

        assert limiter.tokens == 0

    @pytest.mark.asyncio
    async def test_rate_limiter_blocking(self):
        """Test that rate limiter blocks when tokens exhausted."""
        limiter = RateLimiter(requests_per_second=10)

        # Exhaust all tokens
        for _ in range(10):
            await limiter.acquire(1)

        # Next request should block
        start_time = time.monotonic()
        await limiter.acquire(1)
        elapsed = time.monotonic() - start_time

        # Should have waited for token refill
        assert elapsed >= 0.05  # At least 50ms for 1 token at 10 req/s

    @pytest.mark.asyncio
    async def test_rate_limiter_reset(self):
        """Test resetting rate limiter."""
        limiter = RateLimiter(requests_per_second=10)

        # Exhaust tokens
        for _ in range(10):
            await limiter.acquire(1)

        assert limiter.tokens == 0

        # Reset
        limiter.reset()

        assert limiter.tokens == 10

    @pytest.mark.asyncio
    async def test_rate_limiter_refill(self):
        """Test token refilling over time."""
        limiter = RateLimiter(requests_per_second=10)

        # Use all tokens
        for _ in range(10):
            await limiter.acquire(1)

        # Wait for refill
        await asyncio.sleep(0.2)  # 200ms should refill ~2 tokens

        # Should be able to acquire at least 1 token without blocking
        start_time = time.monotonic()
        await limiter.acquire(1)
        elapsed = time.monotonic() - start_time

        assert elapsed < 0.05


class TestExponentialBackoff:
    """Test exponential backoff strategy."""

    def test_backoff_initialization(self):
        """Test backoff initialization."""
        backoff = ExponentialBackoff(
            base_delay=1.0,
            max_delay=60.0,
            exponential_base=2.0
        )

        assert backoff.base_delay == 1.0
        assert backoff.max_delay == 60.0
        assert backoff.exponential_base == 2.0

    def test_calculate_delay_first_attempt(self):
        """Test delay calculation for first attempt."""
        backoff = ExponentialBackoff(base_delay=1.0, jitter=False)

        delay = backoff.calculate_delay(0)

        assert delay == 1.0

    def test_calculate_delay_exponential_growth(self):
        """Test exponential growth of delay."""
        backoff = ExponentialBackoff(base_delay=1.0, jitter=False)

        delay0 = backoff.calculate_delay(0)
        delay1 = backoff.calculate_delay(1)
        delay2 = backoff.calculate_delay(2)

        assert delay0 == 1.0
        assert delay1 == 2.0
        assert delay2 == 4.0

    def test_calculate_delay_max_limit(self):
        """Test that delay doesn't exceed max."""
        backoff = ExponentialBackoff(
            base_delay=1.0,
            max_delay=10.0,
            jitter=False
        )

        # Large attempt number should still cap at max_delay
        delay = backoff.calculate_delay(100)

        assert delay == 10.0

    def test_calculate_delay_with_jitter(self):
        """Test jitter adds randomness."""
        backoff = ExponentialBackoff(base_delay=1.0, jitter=True)

        delays = [backoff.calculate_delay(0) for _ in range(10)]

        # All delays should be >= base_delay
        assert all(d >= 1.0 for d in delays)

        # Delays should vary (with high probability)
        # Note: There's a tiny chance this could fail due to randomness
        assert len(set(delays)) > 1

    @pytest.mark.asyncio
    async def test_wait(self):
        """Test waiting for calculated delay."""
        backoff = ExponentialBackoff(base_delay=0.1, jitter=False)

        start_time = time.monotonic()
        await backoff.wait(0)
        elapsed = time.monotonic() - start_time

        # Should wait approximately base_delay
        assert 0.08 <= elapsed <= 0.15


class TestUserAgentRotator:
    """Test User-Agent rotation."""

    def test_rotator_initialization(self):
        """Test rotator initialization."""
        rotator = UserAgentRotator()

        assert len(rotator.agents) > 0

    def test_get_random(self):
        """Test getting random User-Agent."""
        rotator = UserAgentRotator()

        ua1 = rotator.get_random()
        ua2 = rotator.get_random()

        assert ua1 is not None
        assert ua2 is not None
        assert isinstance(ua1, str)
        assert isinstance(ua2, str)

    def test_get_next(self):
        """Test getting next User-Agent in rotation."""
        custom_agents = ["Agent1", "Agent2", "Agent3"]
        rotator = UserAgentRotator(custom_agents=custom_agents)

        ua1 = rotator.get_next()
        ua2 = rotator.get_next()
        ua3 = rotator.get_next()
        ua4 = rotator.get_next()  # Should wrap around

        assert ua1 == "Agent1"
        assert ua2 == "Agent2"
        assert ua3 == "Agent3"
        assert ua4 == "Agent1"

    def test_custom_agents(self):
        """Test using custom User-Agent list."""
        custom_agents = ["Custom Agent 1", "Custom Agent 2"]
        rotator = UserAgentRotator(custom_agents=custom_agents)

        assert len(rotator.agents) == 2
        assert rotator.get_next() in custom_agents


class TestBotDetectionHandler:
    """Test bot detection handling."""

    def test_handler_initialization(self):
        """Test handler initialization."""
        handler = BotDetectionHandler()

        assert handler.block_count == 0
        assert handler.last_block_time is None

    def test_is_blocked_403(self):
        """Test detection of 403 Forbidden."""
        handler = BotDetectionHandler()

        # Mock response with 403 status
        class MockResponse:
            status = 403
            url = type('obj', (object,), {'path': '/test'})()

        response = MockResponse()
        assert handler.is_blocked(response)

    def test_is_blocked_429(self):
        """Test detection of 429 Too Many Requests."""
        handler = BotDetectionHandler()

        class MockResponse:
            status = 429
            url = type('obj', (object,), {'path': '/test'})()

        response = MockResponse()
        assert handler.is_blocked(response)

    def test_is_blocked_captcha(self):
        """Test detection of CAPTCHA redirect."""
        handler = BotDetectionHandler()

        class MockResponse:
            status = 200
            url = type('obj', (object,), {'path': '/captcha'})()

        response = MockResponse()
        assert handler.is_blocked(response)

    def test_is_not_blocked(self):
        """Test detection of normal response."""
        handler = BotDetectionHandler()

        class MockResponse:
            status = 200
            url = type('obj', (object,), {'path': '/test'})()

        response = MockResponse()
        assert not handler.is_blocked(response)

    @pytest.mark.asyncio
    async def test_handle_block_updates_headers(self):
        """Test that blocking triggers countermeasures."""
        handler = BotDetectionHandler()

        class MockResponse:
            status = 403
            url = type('obj', (object,), {'path': '/test'})()

        response = MockResponse()
        headers = await handler.handle_block(response, 0)

        assert 'User-Agent' in headers
        assert handler.block_count == 1
        assert handler.last_block_time is not None


class TestRobotsTxtParser:
    """Test robots.txt parsing."""

    def test_parser_initialization(self):
        """Test parser initialization."""
        parser = RobotsTxtParser()

        assert parser.crawl_delay is None
        assert len(parser.disallowed_paths) == 0

    def test_parse_crawl_delay(self):
        """Test parsing crawl-delay directive."""
        parser = RobotsTxtParser()

        robots_txt = """
User-agent: *
Crawl-delay: 2
        """

        parser._parse(robots_txt)

        assert parser.crawl_delay == 2.0

    def test_parse_disallow(self):
        """Test parsing disallow directives."""
        parser = RobotsTxtParser()

        robots_txt = """
User-agent: *
Disallow: /admin/
Disallow: /private/
        """

        parser._parse(robots_txt)

        assert '/admin/' in parser.disallowed_paths
        assert '/private/' in parser.disallowed_paths

    def test_is_allowed(self):
        """Test checking if path is allowed."""
        parser = RobotsTxtParser()

        robots_txt = """
User-agent: *
Disallow: /admin/
        """

        parser._parse(robots_txt)

        assert parser.is_allowed('/public/page')
        assert not parser.is_allowed('/admin/page')

    def test_get_crawl_delay(self):
        """Test getting crawl delay."""
        parser = RobotsTxtParser()

        robots_txt = """
User-agent: *
Crawl-delay: 3
        """

        parser._parse(robots_txt)

        assert parser.get_crawl_delay() == 3.0

    def test_parse_comments(self):
        """Test that comments are ignored."""
        parser = RobotsTxtParser()

        robots_txt = """
# This is a comment
User-agent: *
# Crawl-delay: 999  (commented out)
Crawl-delay: 2
        """

        parser._parse(robots_txt)

        assert parser.crawl_delay == 2.0
