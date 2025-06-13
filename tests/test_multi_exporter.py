"""
Tests for multi-exporter functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from otel_tracer.exporters import ExporterType, create_exporter, _create_multi_exporter


class TestMultiExporter:
    @patch('otel_tracer.exporters.MultiSpanExporter')
    @patch('otel_tracer.exporters._create_jaeger_exporter')
    @patch('otel_tracer.exporters._create_otlp_http_exporter')
    def test_create_multi_exporter_success(self, mock_otlp, mock_jaeger, mock_multi):
        """Test successful creation of multi-exporter."""
        mock_jaeger_instance = MagicMock()
        mock_jaeger.return_value = mock_jaeger_instance
        
        mock_otlp_instance = MagicMock()
        mock_otlp.return_value = mock_otlp_instance
        
        mock_multi_instance = MagicMock()
        mock_multi.return_value = mock_multi_instance
        
        result = _create_multi_exporter()
        
        assert result == mock_multi_instance
        mock_jaeger.assert_called_once()
        mock_otlp.assert_called_once()
        mock_multi.assert_called_once_with([mock_jaeger_instance, mock_otlp_instance])

    @patch('otel_tracer.exporters.MultiSpanExporter')
    @patch('otel_tracer.exporters._create_jaeger_exporter')
    @patch('otel_tracer.exporters._create_otlp_http_exporter')
    @patch('otel_tracer.exporters._create_console_exporter')
    def test_create_multi_exporter_with_fallback(self, mock_console, mock_otlp, mock_jaeger, mock_multi):
        """Test multi-exporter creation with fallback to console when others fail."""
        # Make both exporters fail
        mock_jaeger.side_effect = ImportError("Jaeger not available")
        mock_otlp.side_effect = ImportError("OTLP not available")
        
        mock_console_instance = MagicMock()
        mock_console.return_value = mock_console_instance
        
        mock_multi_instance = MagicMock()
        mock_multi.return_value = mock_multi_instance
        
        result = _create_multi_exporter()
        
        assert result == mock_multi_instance
        mock_console.assert_called_once()
        mock_multi.assert_called_once_with([mock_console_instance])

    @patch('otel_tracer.exporters.MultiSpanExporter')
    @patch('otel_tracer.exporters._create_jaeger_exporter')
    @patch('otel_tracer.exporters._create_otlp_http_exporter')
    def test_create_multi_exporter_partial_success(self, mock_otlp, mock_jaeger, mock_multi):
        """Test multi-exporter creation when only one exporter succeeds."""
        # Make Jaeger fail but OTLP succeed
        mock_jaeger.side_effect = ImportError("Jaeger not available")
        
        mock_otlp_instance = MagicMock()
        mock_otlp.return_value = mock_otlp_instance
        
        mock_multi_instance = MagicMock()
        mock_multi.return_value = mock_multi_instance
        
        result = _create_multi_exporter()
        
        assert result == mock_multi_instance
        mock_multi.assert_called_once_with([mock_otlp_instance])

    def test_multi_exporter_via_create_exporter(self):
        """Test creating multi-exporter through main create_exporter function."""
        with patch('otel_tracer.exporters._create_multi_exporter') as mock_multi:
            mock_instance = MagicMock()
            mock_multi.return_value = mock_instance
            
            result = create_exporter(ExporterType.MULTI)
            
            assert result == mock_instance
            mock_multi.assert_called_once()

    def test_multi_exporter_string_type(self):
        """Test creating multi-exporter with string type."""
        with patch('otel_tracer.exporters._create_multi_exporter') as mock_multi:
            mock_instance = MagicMock()
            mock_multi.return_value = mock_instance
            
            result = create_exporter("multi")
            
            assert result == mock_instance
            mock_multi.assert_called_once()

    @patch('otel_tracer.exporters.MultiSpanExporter')
    def test_multi_exporter_import_error(self, mock_multi):
        """Test multi-exporter import error handling."""
        mock_multi.side_effect = ImportError("MultiSpanExporter not available")
        
        with pytest.raises(ImportError, match="MultiSpanExporter not available"):
            _create_multi_exporter()

    @patch('otel_tracer.exporters.MultiSpanExporter')
    @patch('otel_tracer.exporters._create_jaeger_exporter')
    @patch('otel_tracer.exporters._create_otlp_http_exporter')
    def test_multi_exporter_with_custom_endpoint_and_headers(self, mock_otlp, mock_jaeger, mock_multi):
        """Test multi-exporter creation with custom endpoint and headers."""
        mock_jaeger_instance = MagicMock()
        mock_jaeger.return_value = mock_jaeger_instance
        
        mock_otlp_instance = MagicMock()
        mock_otlp.return_value = mock_otlp_instance
        
        mock_multi_instance = MagicMock()
        mock_multi.return_value = mock_multi_instance
        
        endpoint = "http://custom:4317"
        headers = {"Authorization": "Bearer token"}
        
        result = _create_multi_exporter(endpoint=endpoint, headers=headers)
        
        assert result == mock_multi_instance
        # Check that custom parameters were passed to both exporters
        mock_jaeger.assert_called_once_with(endpoint=endpoint, headers=headers)
        mock_otlp.assert_called_once_with(endpoint=endpoint, headers=headers) 