#!/usr/bin/env python3
"""
Print all registered routes in the Flask app
"""

from run import app

print("All registered routes:")
print("=" * 60)

for rule in app.url_map.iter_rules():
    endpoint = rule.endpoint
    methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
    path = str(rule)
    print(f"{methods:6} {path:40} -> {endpoint}")

print("=" * 60)
