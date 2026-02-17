def test_example():
    """A simple example test to verify pytest is working."""
    assert 1 + 1 == 2

def test_project_imports():
    """Test that all project modules can be imported without errors."""
    try:
        import scraper
        import table_utils
        import main
        assert True
    except ImportError as e:
        assert False, f"Failed to import project modules: {e}"
