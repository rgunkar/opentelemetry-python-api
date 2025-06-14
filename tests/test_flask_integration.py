"""
Integration tests for Flask framework support.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

from otel_tracer import setup_flask_tracing
from otel_tracer.frameworks.flask import instrument_flask, is_instrumented, reset_flask_instrumentation


@pytest.fixture
def flask_app():
    """Create a test Flask app."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    @app.route('/')
    def hello():
        return {'message': 'Hello World'}
    
    @app.route('/users/<int:user_id>')
    def get_user(user_id):
        return {'id': user_id, 'name': f'User {user_id}'}
    
    return app


@pytest.fixture(autouse=True)
def reset_flask_state():
    """Reset Flask instrumentation state between tests."""
    reset_flask_instrumentation()
    yield
    reset_flask_instrumentation()


class TestFlaskSetup:
    def test_setup_flask_tracing_basic(self, flask_app, sample_config):
        """Test basic Flask tracing setup."""
        with patch('otel_tracer.frameworks.flask.FlaskInstrumentor') as mock_instrumentor:
            mock_instance = MagicMock()
            mock_instrumentor.return_value = mock_instance
            
            tracer = setup_flask_tracing(flask_app, config=sample_config)
            
            assert tracer is not None
            assert is_instrumented()
            mock_instance.instrument_app.assert_called_once()

    def test_setup_flask_tracing_with_service_name(self, flask_app):
        """Test Flask setup with explicit service name."""
        with patch('otel_tracer.frameworks.flask.FlaskInstrumentor') as mock_instrumentor:
            mock_instance = MagicMock()
            mock_instrumentor.return_value = mock_instance
            
            tracer = setup_flask_tracing(
                flask_app, 
                service_name="test-flask-service"
            )
            
            assert tracer is not None
            assert is_instrumented()

    def test_setup_flask_tracing_with_excluded_urls(self, flask_app, sample_config):
        """Test Flask setup with excluded URLs."""
        with patch('otel_tracer.frameworks.flask.FlaskInstrumentor') as mock_instrumentor:
            mock_instance = MagicMock()
            mock_instrumentor.return_value = mock_instance
            
            excluded_urls = ['/health', '/metrics']
            setup_flask_tracing(
                flask_app, 
                config=sample_config,
                excluded_urls=excluded_urls
            )
            
            # Check that excluded URLs were passed as kwargs
            call_args = mock_instance.instrument_app.call_args
            assert 'excluded_urls' in call_args[1]
            assert call_args[1]['excluded_urls'] == 'health,metrics'

    def test_setup_flask_tracing_idempotent(self, flask_app, sample_config):
        """Test that Flask setup is idempotent."""
        with patch('otel_tracer.frameworks.flask.FlaskInstrumentor') as mock_instrumentor:
            mock_instance = MagicMock()
            mock_instrumentor.return_value = mock_instance
            
            # First setup
            tracer1 = setup_flask_tracing(flask_app, config=sample_config)
            assert is_instrumented()
            
            # Second setup should not instrument again
            tracer2 = setup_flask_tracing(flask_app, config=sample_config)
            
            assert tracer1 is not None
            assert tracer2 is not None
            # Should only be called once due to idempotent behavior
            assert mock_instance.instrument_app.call_count == 1

    def test_flask_import_error(self):
        """Test handling of Flask instrumentation import error."""
        with patch('otel_tracer.frameworks.flask.FlaskInstrumentor', None):
            with pytest.raises(ImportError, match="Flask instrumentation not available"):
                instrument_flask()

    def test_setup_with_database_tracing_disabled(self, flask_app, sample_config):
        """Test Flask setup with database tracing disabled."""
        with patch('otel_tracer.frameworks.flask.FlaskInstrumentor') as mock_instrumentor:
            mock_instance = MagicMock()
            mock_instrumentor.return_value = mock_instance
            
            with patch('otel_tracer.frameworks.flask.setup_database_tracing') as mock_db_setup:
                setup_flask_tracing(
                    flask_app, 
                    config=sample_config,
                    enable_database_tracing=False
                )
                
                # Database tracing should not be called
                mock_db_setup.assert_not_called()

    def test_setup_with_database_tracing_enabled(self, flask_app, sample_config):
        """Test Flask setup with database tracing enabled."""
        with patch('otel_tracer.frameworks.flask.FlaskInstrumentor') as mock_instrumentor:
            mock_instance = MagicMock()
            mock_instrumentor.return_value = mock_instance
            
            with patch('otel_tracer.frameworks.flask.setup_database_tracing') as mock_db_setup:
                setup_flask_tracing(
                    flask_app, 
                    config=sample_config,
                    enable_database_tracing=True
                )
                
                # Database tracing should be called
                mock_db_setup.assert_called_once()

    def test_flask_app_name_used_as_service_name(self, flask_app):
        """Test that Flask app name is used as service name when not provided."""
        flask_app.name = 'my-test-app'
        
        with patch('otel_tracer.frameworks.flask.FlaskInstrumentor') as mock_instrumentor:
            mock_instance = MagicMock()
            mock_instrumentor.return_value = mock_instance
            
            with patch('otel_tracer.frameworks.flask.TracingConfig') as mock_config:
                # Create a real TracingConfig instance instead of a mock
                from otel_tracer.tracer import TracingConfig
                from otel_tracer.exporters import ExporterType
                real_config = TracingConfig(
                    service_name='my-test-app',
                    exporter_type=ExporterType.CONSOLE
                )
                mock_config.from_env.return_value = real_config
                
                setup_flask_tracing(flask_app)
                
                # Should be called with app name as service name
                mock_config.from_env.assert_called_with(service_name='my-test-app') 