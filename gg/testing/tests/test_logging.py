from ..microtest import TestCase
from ...logging.Log import LOG_LEVEL, logger, LOG_LEVELS
import logging

class TestLogging(TestCase):
    def test_logger_configuration(self):
        """Test logger is configured correctly"""
        self.assertTrue(logger is not None)
        self.assertTrue(len(logger.handlers) > 0)
        
    def test_log_level_setting(self):
        """Test that log level can be changed"""
        original_level = logger.level
        try:
            logger.setLevel(logging.WARNING)
            self.assertEqual(logger.level, logging.WARNING)
        finally:
            logger.setLevel(original_level)
        
    def test_default_level(self):
        """Test that default log level is set correctly"""
        from config import LogConfig
        expected_level = LOG_LEVELS.get(LogConfig.LOG_LEVEL, logging.INFO)
        self.assertEqual(LOG_LEVEL, expected_level)
        self.assertEqual(logger.level, LOG_LEVEL) 