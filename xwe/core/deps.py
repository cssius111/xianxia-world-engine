try:
    import requests
except ImportError:
    import sys
    sys.path.insert(0, "./vendor/requests")
    import requests