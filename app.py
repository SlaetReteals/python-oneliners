import ast
import io
import os
import sys
import time
import traceback
from contextlib import redirect_stdout
# pyrefly: ignore [missing-import]
from pyscript import document, window
# pyrefly: ignore [missing-import]
import js
# pyrefly: ignore [missing-import]
from pyodide.ffi import create_proxy

# ----------------------------------------------------
# 1. DATABASE OF PYTHON ONE-LINERS
# ----------------------------------------------------
ONE_LINERS = [
    {
        "id": "fizzbuzz",
        "title": "FizzBuzz Generator",
        "category": "comprehensions",
        "code": "print('\\n'.join(['Fizz'*(i%3==0) + 'Buzz'*(i%5==0) or str(i) for i in range(1, limit + 1)]))",
        "description": "Generates the classic FizzBuzz game up to a limit. It concatenates 'Fizz' (if divisible by 3) and 'Buzz' (if divisible by 5). If both are empty, it defaults to the number string itself using the 'or' short-circuit fallback.",
        "variables": [
            {"name": "limit", "default": "20", "label": "Limit"}
        ]
    },
    {
        "id": "qsort",
        "title": "Inline Quick Sort",
        "category": "algorithms",
        "code": "qsort = lambda l: l if len(l) <= 1 else qsort([x for x in l[1:] if x < l[0]]) + [l[0]] + qsort([x for x in l[1:] if x >= l[0]]); print(qsort(array))",
        "description": "A functional implementation of the Quick Sort algorithm. It uses list comprehensions to partition the array into elements smaller than the pivot (the first element) and elements larger than or equal to the pivot, then recursively sorts and merges them.",
        "variables": [
            {"name": "array", "default": "[3, 6, 8, 10, 1, 2, 1]", "label": "List to Sort"}
        ]
    },
    {
        "id": "fibonacci",
        "title": "Fibonacci Sequence Generator",
        "category": "algorithms",
        "code": "from functools import reduce; fib = lambda n: reduce(lambda x, _: x + [x[-1] + x[-2]], range(n - 2), [0, 1]); print(fib(terms))",
        "description": "Generates a list of Fibonacci numbers up to the specified number of terms. It uses 'functools.reduce' to iteratively append the sum of the last two elements of the list, starting with the base list [0, 1].",
        "variables": [
            {"name": "terms", "default": "10", "label": "Terms (>= 2)"}
        ]
    },
    {
        "id": "primes",
        "title": "Prime Number Sieve",
        "category": "algorithms",
        "code": "primes = [x for x in range(2, limit) if all(x % y != 0 for y in range(2, int(x**0.5) + 1))]; print(primes)",
        "description": "Finds all prime numbers up to a specified limit. For each number in the range, it verifies if it is divisible by any number up to its square root. If none divide it, the number is prime.",
        "variables": [
            {"name": "limit", "default": "50", "label": "Upper Limit"}
        ]
    },
    {
        "id": "transpose",
        "title": "Matrix Transposition",
        "category": "math",
        "code": "transposed = list(zip(*matrix)); print(transposed)",
        "description": "Transposes a 2D matrix (swapping rows and columns). The asterisk (*) unpacks the matrix rows as individual positional arguments to 'zip', which then groups the corresponding columns together.",
        "variables": [
            {"name": "matrix", "default": "[[1, 2, 3], [4, 5, 6], [7, 8, 9]]", "label": "2D Matrix"}
        ]
    },
    {
        "id": "anagram",
        "title": "Anagram Checker",
        "category": "strings",
        "code": "is_anagram = lambda s1, s2: sorted(s1.replace(' ', '').lower()) == sorted(s2.replace(' ', '').lower()); print(is_anagram(word1, word2))",
        "description": "Checks if two strings are anagrams of each other (contain the exact same letters in a different order). It normalizes the casing, strips spaces, and compares their sorted lists of characters.",
        "variables": [
            {"name": "word1", "default": "'Listen'", "label": "First Word"},
            {"name": "word2", "default": "'Silent'", "label": "Second Word"}
        ]
    },
    {
        "id": "palindrome",
        "title": "Palindrome Checker",
        "category": "strings",
        "code": "is_palindrome = lambda s: s.lower() == s.lower()[::-1]; print(is_palindrome(text))",
        "description": "Determines if a string reads the same backward as forward. It converts the text to lowercase and checks if it is equal to its slice reversed [::-1].",
        "variables": [
            {"name": "text", "default": "'A nut for a jar of tuna'", "label": "Text"}
        ]
    },
    {
        "id": "flatten",
        "title": "Flatten Nested List",
        "category": "comprehensions",
        "code": "flat = [item for sublist in nested_list for item in sublist]; print(flat)",
        "description": "Flattens a list of lists into a single flat list. It uses a double-nested list comprehension that loops through each sublist and then loops through each item in the sublist.",
        "variables": [
            {"name": "nested_list", "default": "[[1, 2], [3, 4, 5], [6]]", "label": "Nested List"}
        ]
    },
    {
        "id": "most_frequent",
        "title": "Most Frequent List Item",
        "category": "utilities",
        "code": "most_common = max(set(items), key=items.count); print(most_common)",
        "description": "Finds the element that appears most frequently in a list. It converts the list to a set of unique items, then finds the item that maximizes the frequency count using the list's 'count' method as the sorting key.",
        "variables": [
            {"name": "items", "default": "[1, 2, 3, 3, 2, 3, 4, 4, 3, 1]", "label": "List Items"}
        ]
    },
    {
        "id": "merge_dicts",
        "title": "Merge Two Dictionaries",
        "category": "utilities",
        "code": "merged = {**dict1, **dict2}; print(merged)",
        "description": "Merges two dictionary objects. In case of duplicate keys, values from the second dictionary override the first dictionary.",
        "variables": [
            {"name": "dict1", "default": "{'a': 1, 'b': 2}", "label": "Dictionary A"},
            {"name": "dict2", "default": "{'b': 99, 'c': 4}", "label": "Dictionary B"}
        ]
    },
    {
        "id": "password_gen",
        "title": "Random Password Generator",
        "category": "utilities",
        "code": "import random, string; password = ''.join(random.choices(string.ascii_letters + string.digits + '!@#$', k=length)); print(password)",
        "description": "Generates a random password of a specific length. It uses 'random.choices' to select characters from lowercase, uppercase letters, digits, and basic special symbols.",
        "variables": [
            {"name": "length", "default": "16", "label": "Length"}
        ]
    },
    {
        "id": "gcd",
        "title": "Greatest Common Divisor (GCD)",
        "category": "math",
        "code": "gcd = lambda a, b: a if b == 0 else gcd(b, a % b); print(gcd(num1, num2))",
        "description": "Calculates the Greatest Common Divisor (GCD) of two numbers using the Euclidean algorithm recursively.",
        "variables": [
            {"name": "num1", "default": "48", "label": "Number A"},
            {"name": "num2", "default": "18", "label": "Number B"}
        ]
    },
    {
        "id": "base64_encode",
        "title": "Base64 String Encoder",
        "category": "strings",
        "code": "import base64; encoded = base64.b64encode(plain_text.encode('utf-8')).decode('utf-8'); print(encoded)",
        "description": "Encodes a plaintext UTF-8 string into Base64 format. It encodes the string to bytes, runs 'b64encode', and then decodes the bytes back to a printable string.",
        "variables": [
            {"name": "plain_text", "default": "'Hello World!'", "label": "Plain Text"}
        ]
    },
    {
        "id": "invert_dict",
        "title": "Invert Dictionary Keys/Values",
        "category": "comprehensions",
        "code": "inverted = {value: key for key, value in original_dict.items()}; print(inverted)",
        "description": "Swaps the keys and values of a dictionary. This assumes all values in the original dictionary are unique.",
        "variables": [
            {"name": "original_dict", "default": "{'apple': 'red', 'banana': 'yellow', 'lime': 'green'}", "label": "Original Dict"}
        ]
    },
    {
        "id": "factorial",
        "title": "One-Line Factorial",
        "category": "math",
        "code": "from functools import reduce; fact = lambda n: reduce(lambda x, y: x * y, range(1, n + 1) or [1]); print(fact(number))",
        "description": "Computes the factorial of a number using 'functools.reduce' on the range of numbers. A fallback to [1] ensures it works for 0.",
        "variables": [
            {"name": "number", "default": "5", "label": "Number"}
        ]
    },
    {
        "id": "http_server",
        "title": "Instant Web Server",
        "category": "web",
        "code": "import http.server, socketserver; print(f'Serving HTTP on port {port}...'); socketserver.TCPServer(('', port), http.server.SimpleHTTPRequestHandler).serve_forever()",
        "description": "Launches a simple, zero-configuration HTTP server in the current directory on the specified port. Note: This command starts a blocking network service.",
        "variables": [
            {"name": "port", "default": "8000", "label": "Port"}
        ]
    },
    {
        "id": "cgi_server",
        "title": "CGI Script Web Server",
        "category": "web",
        "code": "import http.server, socketserver; print(f'Serving CGI on port {port}...'); socketserver.TCPServer(('', port), http.server.CGIHTTPRequestHandler).serve_forever()",
        "description": "Launches an HTTP server that supports executing CGI scripts (placed in a local 'cgi-bin' directory). Useful for hosting legacy scripts.",
        "variables": [
            {"name": "port", "default": "8000", "label": "Port"}
        ]
    },
    {
        "id": "threaded_server",
        "title": "Threaded Concurrency Server",
        "category": "web",
        "code": "from socketserver import ThreadingTCPServer; from http.server import SimpleHTTPRequestHandler; print(f'Serving Threaded HTTP on port {port}...'); ThreadingTCPServer(('', port), SimpleHTTPRequestHandler).serve_forever()",
        "description": "Starts a threaded HTTP server that handles multiple client connections concurrently, preventing slow assets from blocking other requests.",
        "variables": [
            {"name": "port", "default": "8000", "label": "Port"}
        ]
    },
    {
        "id": "flask_app",
        "title": "Flask Web Application",
        "category": "web",
        "code": "from flask import Flask; app = Flask(__name__); app.route('/')(lambda: 'Flask One-Liner app running!'); print('Starting Flask app...'); app.run(port=port)",
        "description": "Runs a minimal single-route Flask application. Requires the flask package: 'pip install flask'.",
        "variables": [
            {"name": "port", "default": "8080", "label": "Port"}
        ]
    },
    {
        "id": "fastapi_app",
        "title": "FastAPI Web Application",
        "category": "web",
        "code": "import uvicorn; from fastapi import FastAPI; app = FastAPI(); app.get('/')(lambda: {'status': 'FastAPI running'}); print('Starting Uvicorn...'); uvicorn.run(app, port=port)",
        "description": "Runs a minimal FastAPI application with a JSON response endpoint served via Uvicorn. Requires 'fastapi' and 'uvicorn' packages.",
        "variables": [
            {"name": "port", "default": "8000", "label": "Port"}
        ]
    },
    {
        "id": "header_inspector",
        "title": "Request Headers Inspector",
        "category": "web",
        "code": "from http.server import BaseHTTPRequestHandler, HTTPServer; H = type('H', (BaseHTTPRequestHandler,), {'do_GET': lambda s: (s.send_response(200), s.end_headers(), s.wfile.write(str(s.headers).encode()))}); print(f'Headers Inspector on port {port}...'); HTTPServer(('', port), H).serve_forever()",
        "description": "Launches an HTTP server that captures incoming client requests and echoes all HTTP request headers back to the browser. Uses dynamic class generation to enable single-line execution without compound syntax errors.",
        "variables": [
            {"name": "port", "default": "8000", "label": "Port"}
        ]
    },
    {
        "id": "wsgi_server",
        "title": "WSGI Web Application Server",
        "category": "web",
        "code": "from wsgiref.simple_server import make_server; print(f'Serving WSGI app on port {port}...'); make_server('', port, lambda env, start: (start('200 OK', [('Content-Type', 'text/plain')]), [b'WSGI One-Liner Active!'])[1]).serve_forever()",
        "description": "Starts a standard built-in WSGI web server (PEP 3333) hosting a minimal dynamic web application using Python's standard library without requiring external dependencies.",
        "variables": [
            {"name": "port", "default": "8000", "label": "Port"}
        ]
    },
    {
        "id": "raw_socket_server",
        "title": "Raw TCP Socket Web Server",
        "category": "web",
        "code": "import socket; s = socket.socket(); s.bind(('', port)); s.listen(1); print(f'Raw Socket Web Server on port {port}...'); conn, addr = s.accept(); conn.recv(1024); conn.sendall(b'HTTP/1.1 200 OK\\r\\nContent-Type: text/plain\\r\\n\\r\\nRaw Socket Response!')",
        "description": "A low-level socket server. It binds to a port, listens for a single incoming connection, reads the header, sends a raw text HTTP response, and exits.",
        "variables": [
            {"name": "port", "default": "9000", "label": "Port"}
        ]
    },
    {
        "id": "https_server",
        "title": "Secure HTTPS Web Server",
        "category": "web",
        "code": "import http.server, ssl, socketserver; httpd = socketserver.TCPServer(('', port), http.server.SimpleHTTPRequestHandler); httpd.socket = ssl.wrap_socket(httpd.socket, certfile='server.pem', server_side=True); print(f'HTTPS Serving on {port}...'); httpd.serve_forever()",
        "description": "Starts a secure HTTP server using SSL/TLS. Requires a certificate file named 'server.pem' in the directory.",
        "variables": [
            {"name": "port", "default": "4443", "label": "Port"}
        ]
    },
    {
        "id": "pyscript_host",
        "title": "WASM PyScript Boilerplate",
        "category": "web",
        "code": "html = '<html><head><script type=\"module\" src=\"https://pyscript.net/releases/2024.1.1/core.js\"></script></head><body><script type=\"py\">print(\"Hello from PyScript WASM!\")</script></body></html>'; print(html)",
        "description": "Prints a complete single-file HTML skeleton that embeds PyScript to execute Python code client-side inside standard browsers. No backend server required.",
        "variables": []
    },
    {
        "id": "port_scanner",
        "title": "Basic TCP Port Scanner",
        "category": "security",
        "code": "import socket; print([p for p in ports if socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex((host, p)) == 0])",
        "description": "Scans a host for open TCP ports using socket connection tests. Returns a list of ports that completed a full handshake (code == 0). Keep ports list short to avoid browser blocking.",
        "variables": [
            {"name": "host", "default": "'127.0.0.1'", "label": "Target Host"},
            {"name": "ports", "default": "[22, 80, 443, 8000]", "label": "Ports List"}
        ]
    },
    {
        "id": "recursive_search",
        "title": "Recursive File Finder",
        "category": "files",
        "code": "import glob; print(glob.glob(f'./**/{glob_pattern}', recursive=True))",
        "description": "Recursively searches directories under the current folder matching a specific glob pattern or filename. Uses wildcards (**) to find files at any nested folder depth.",
        "variables": [
            {"name": "glob_pattern", "default": "*.*", "label": "Glob Pattern / File Name", "type": "glob"}
        ]
    },
    {
        "id": "hash_gen",
        "title": "SHA-256 Hash Generator",
        "category": "security",
        "code": "import hashlib; print(hashlib.sha256(data.encode('utf-8')).hexdigest())",
        "description": "Generates a SHA-256 cryptographic hash of a given text input. Useful for integrity checks, checksum validation, or password hashing simulations.",
        "variables": [
            {"name": "data", "default": "'SecurePassword123'", "label": "Data Text"}
        ]
    },
    {
        "id": "ip_extractor",
        "title": "Log IP Address Extractor",
        "category": "security",
        "code": "import re; print(list(set(re.findall(r'(?:[0-9]{1,3}\\.){3}[0-9]{1,3}', log_data))))",
        "description": "Extracts unique IP address patterns from a string block (such as an Apache or system access log file) using regular expressions.",
        "variables": [
            {"name": "log_data", "default": "'192.168.1.10 - - [04/Aug/2026] \"GET /index.html\" 200 450\\n192.168.1.25 - - [04/Aug/2026] \"POST /login\" 401 120\\n192.168.1.10 - - [04/Aug/2026] \"GET /style.css\" 200 80'", "label": "Log String"}
        ]
    },
    {
        "id": "pw_strength",
        "title": "Password Strength Checker",
        "category": "security",
        "code": "is_strong = lambda p: len(p) >= 8 and any(c.isupper() for c in p) and any(c.islower() for c in p) and any(c.isdigit() for c in p); print(is_strong(password))",
        "description": "Validates if a password meets minimum complexity requirements: length >= 8, containing at least one uppercase letter, one lowercase letter, and one digit.",
        "variables": [
            {"name": "password", "default": "'P@ssword123'", "label": "Password"}
        ]
    },
    {
        "id": "ir_webshell_hunter",
        "title": "Incident Response: Web Shell & Backdoor Hunter",
        "category": "security",
        "code": "import os; print('\\n'.join([os.path.join(r, f) for r, _, fs in os.walk(directory) for f in fs if f.endswith(ext) and any(k in open(os.path.join(r, f), 'r', errors='ignore').read() for k in keywords.split(','))]))",
        "description": "Recursively scans a directory for files of a specific extension containing suspicious keywords often associated with web shells, backdoors, or unauthorized remote execution.",
        "variables": [
            {"name": "directory", "default": "'.'", "label": "Search Directory"},
            {"name": "ext", "default": "'.php'", "label": "File Extension (e.g. .php, .py)"},
            {"name": "keywords", "default": "'eval,exec,system,subprocess,socket'", "label": "Keywords (comma-separated)"}
        ]
    },
    {
        "id": "ir_exploit_scanner",
        "title": "Incident Response: Exploit Signature Log Scanner",
        "category": "security",
        "code": "import re; logs = open(filepath, 'r', errors='ignore').readlines(); attacks = [f'Line {i+1}: {line.strip()}' for i, line in enumerate(logs) if re.search(pattern, line, re.IGNORECASE)]; print(f'Detected {len(attacks)} potential exploits:\\n' + '\\n'.join(attacks[:limit]))",
        "description": "Scans access logs or general system logs for regular expression signatures of web exploits like SQL Injection (SQLi), Cross-Site Scripting (XSS), and Path Traversal.",
        "variables": [
            {"name": "filepath", "default": "'server.log'", "label": "Log File", "type": "file"},
            {"name": "pattern", "default": "'union\\\\s+select|select\\\\s+.*\\\\s+from|\\\\.\\\\./|<script>|%27|etc/passwd'", "label": "Regex Pattern"},
            {"name": "limit", "default": "20", "label": "Max Lines to Print"}
        ]
    },
    {
        "id": "ir_timeline_auditor",
        "title": "Incident Response: Modified File Auditor",
        "category": "security",
        "code": "import os, time; now = time.time(); print('\\n'.join([f'{os.path.join(r, f)} - {time.ctime(os.path.getmtime(os.path.join(r, f)))}' for r, _, fs in os.walk(directory) for f in fs if now - os.path.getmtime(os.path.join(r, f)) < timeframe_hours * 3600]))",
        "description": "Recursively lists all files in a directory that were modified within the last N hours. Essential for post-compromise timeline reconstruction and identifying newly created or modified backdoor files.",
        "variables": [
            {"name": "directory", "default": "'.'", "label": "Search Directory"},
            {"name": "timeframe_hours", "default": "24", "label": "Timeframe (Hours)"}
        ]
    },
    {
        "id": "ir_http_status",
        "title": "Incident Response: HTTP Status Summarizer",
        "category": "security",
        "code": "import re, collections; codes = re.findall(r'\"\\s+([1-5][0-9]{2})\\s+', open(filepath, 'r', errors='ignore').read()); print('\\n'.join([f'HTTP {code}: {count} occurrences' for code, count in collections.Counter(codes).most_common()]))",
        "description": "Parses web server logs to count and summarize HTTP response status codes. A high volume of 404 or 401/403 errors can indicate vulnerability scanning or credential brute-forcing.",
        "variables": [
            {"name": "filepath", "default": "'server.log'", "label": "Log File", "type": "file"}
        ]
    },
    {
        "id": "csv_to_json",
        "title": "CSV to JSON Converter & Inspector",
        "category": "files",
        "code": "import csv, json; data = [dict(row) for row in csv.DictReader(open(filepath, 'r', encoding='utf-8', errors='ignore'))]; print(json.dumps(data, indent=2))",
        "description": "Reads an uploaded CSV file from the WebAssembly virtual filesystem, maps each row to a dictionary using DictReader, and formats the dataset into clean JSON.",
        "variables": [
            {"name": "filepath", "default": "'sample.csv'", "label": "CSV Filename", "type": "file"}
        ]
    },
    {
        "id": "log_ip_analyzer",
        "title": "Log File IP Address Frequency Counter",
        "category": "files",
        "code": "import re, collections; print('\\n'.join([f'{ip}: {count} occurrences' for ip, count in collections.Counter(re.findall(r'(?:[0-9]{1,3}\\.){3}[0-9]{1,3}', open(filepath, 'r', encoding='utf-8', errors='ignore').read())).most_common()]))",
        "description": "Scans any log or text file for IPv4 addresses using regex, tallies frequency using collections.Counter, and prints a sorted list of active network hosts.",
        "variables": [
            {"name": "filepath", "default": "'server.log'", "label": "Log Filename", "type": "file"}
        ]
    },
    {
        "id": "md_toc_extractor",
        "title": "Markdown TOC & Headings Extractor",
        "category": "files",
        "code": "print('\\n'.join([f'{\"  \" * (len(line.split()[0]) - 1)}• {line.lstrip(\"#\").strip()}' for line in open(filepath, 'r', encoding='utf-8', errors='ignore') if line.strip().startswith('#')]))",
        "description": "Parses a Markdown (.md) document line-by-line, identifies heading structures (#, ##, ###), and generates an indented Table of Contents hierarchy.",
        "variables": [
            {"name": "filepath", "default": "'notes.md'", "label": "Markdown Filename", "type": "file"}
        ]
    },
    {
        "id": "doc_word_stats",
        "title": "Document Word, Line & Character Counter",
        "category": "files",
        "code": "text = open(filepath, 'r', encoding='utf-8', errors='ignore').read(); print(f'📄 File: {filepath}\\n───\\nLines: {len(text.splitlines()):,}\\nWords: {len(text.split()):,}\\nCharacters (no spaces): {len(text.replace(\" \", \"\")):,}\\nTotal Bytes: {len(text.encode(\"utf-8\")):,}')",
        "description": "Performs a complete structural analysis on any text, log, or data document, calculating exact lines, vocabulary words, non-space character metrics, and file sizes.",
        "variables": [
            {"name": "filepath", "default": "'notes.md'", "label": "File Path", "type": "file"}
        ]
    },
    {
        "id": "csv_filter_query",
        "title": "Filter & Query CSV Rows by Column Value",
        "category": "files",
        "code": "import csv, json; matches = [row for row in csv.DictReader(open(filepath, 'r', encoding='utf-8', errors='ignore')) if str(row.get(col_name, '')).strip().lower() == str(query_val).strip().lower()]; print(f'Found {len(matches)} matching records:\\n', json.dumps(matches, indent=2))",
        "description": "Queries a CSV file in memory without loading pandas or heavy databases, filtering for specific text or value matches inside a named database column.",
        "variables": [
            {"name": "filepath", "default": "'sample.csv'", "label": "CSV File", "type": "file"},
            {"name": "col_name", "default": "Role", "label": "Target Column", "type": "string"},
            {"name": "query_val", "default": "Admin", "label": "Search Value", "type": "string"}
        ]
    },
    {
        "id": "search_grep_regex",
        "title": "Regex Line Matcher with Line Numbers (Like grep -n)",
        "category": "search",
        "code": "import re; print('\\n'.join([f'Line {i+1}: {line.strip()}' for i, line in enumerate(open(filepath, 'r', encoding='utf-8', errors='ignore')) if re.search(pattern, line)]))",
        "description": "Scans a file line-by-line for a regular expression pattern, outputting matching line numbers and contents exactly like the command-line utility grep -n.",
        "variables": [
            {"name": "filepath", "default": "'server.log'", "label": "Target Document", "type": "file"},
            {"name": "pattern", "default": "POST|401", "label": "Regex Pattern", "type": "regex"}
        ]
    },
    {
        "id": "search_substring_nocase",
        "title": "Case-Insensitive Keyword Locator",
        "category": "search",
        "code": "keyword = search_term.lower(); print('\\n'.join([f'L{i+1}: {line.strip()}' for i, line in enumerate(open(filepath, 'r', encoding='utf-8', errors='ignore')) if keyword in line.lower()]))",
        "description": "Searches any document for a specific text string regardless of upper or lower case capitalization, showing exact matching rows with line numbers.",
        "variables": [
            {"name": "filepath", "default": "'notes.md'", "label": "Target Document", "type": "file"},
            {"name": "search_term", "default": "anomalous", "label": "Search Term", "type": "string"}
        ]
    },
    {
        "id": "search_extract_emails",
        "title": "Email Address Harvester & Extractor",
        "category": "search",
        "code": "import re; print('\\n'.join(sorted(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}', open(filepath, 'r', encoding='utf-8', errors='ignore').read())))))",
        "description": "Performs a regex extraction across an entire document to find all email addresses, returning a clean deduplicated list of discovered mail contacts.",
        "variables": [
            {"name": "filepath", "default": "'pasted_text.txt'", "label": "Target Document", "type": "file"}
        ]
    },
    {
        "id": "search_multi_keyword_and",
        "title": "Multi-Keyword AND Search (Lines Containing All Terms)",
        "category": "search",
        "code": "terms = [t.strip().lower() for t in required_keywords]; print('\\n'.join([f'L{i+1}: {l.strip()}' for i, l in enumerate(open(filepath, 'r', encoding='utf-8', errors='ignore')) if all(t in l.lower() for t in terms)]))",
        "description": "Finds only those lines that contain every single required keyword simultaneously, ideal for filtering complex diagnostic logs or complex query filtering.",
        "variables": [
            {"name": "filepath", "default": "'server.log'", "label": "Target Document", "type": "file"},
            {"name": "required_keywords", "default": "['10.0.0.5', '401']", "label": "Required Keywords"}
        ]
    },
    {
        "id": "search_extract_urls",
        "title": "Web URL & HTTP Link Scraper",
        "category": "search",
        "code": "import re; print('\\n'.join(sorted(set(re.findall(r'https?://[^\\s)\\'\\\",]+', open(filepath, 'r', encoding='utf-8', errors='ignore').read())))))",
        "description": "Scans Markdown, HTML, log files, or custom pasted text buffers for HTTP and HTTPS web URLs, outputting an organized link directory.",
        "variables": [
            {"name": "filepath", "default": "'pasted_text.txt'", "label": "Target Document", "type": "file"}
        ]
    },
    {
        "id": "search_error_hunter",
        "title": "Error, Warning & Exception Hunter",
        "category": "search",
        "code": "import re; print('\\n'.join([f'[{line_num}] {line.strip()}' for line_num, line in enumerate(open(filepath, 'r', encoding='utf-8', errors='ignore'), 1) if re.search(r'error|exception|warn|fatal|failed|timeout', line, re.IGNORECASE)]))",
        "description": "Rapidly filters a log or code file for common failure indicators such as 'error', 'exception', 'warn', 'fatal', or 'failed', giving instant triage visibility.",
        "variables": [
            {"name": "filepath", "default": "'pasted_text.txt'", "label": "Target Document", "type": "file"}
        ]
    },
    {
        "id": "search_line_prefix",
        "title": "Line Prefix Filter (Find Headers, Timestamps, or Comments)",
        "category": "search",
        "code": "print('\\n'.join([l.strip() for l in open(filepath, 'r', encoding='utf-8', errors='ignore') if l.lstrip().startswith(prefix)]))",
        "description": "Filters a file to return only rows that begin with a specific character or timestamp string (such as # for Markdown headings, // for comments, or 192. for subnets).",
        "variables": [
            {"name": "filepath", "default": "'notes.md'", "label": "Target Document", "type": "file"},
            {"name": "prefix", "default": "#", "label": "Line Prefix String", "type": "string"}
        ]
    },
    {
        "id": "search_duplicates",
        "title": "Duplicate Line Detector & Repeating Entry Locator",
        "category": "search",
        "code": "import collections; print('\\n'.join([f'Repeated {cnt}x: {line}' for line, cnt in collections.Counter([l.strip() for l in open(filepath, 'r', encoding='utf-8', errors='ignore') if l.strip()]).items() if cnt > 1]) or 'No identical duplicate lines found!')",
        "description": "Analyzes a document or pasted text buffer to detect identical repeated lines, showing how many times each repeated row occurs in the dataset.",
        "variables": [
            {"name": "filepath", "default": "'server.log'", "label": "Target Document", "type": "file"}
        ]
    },
    {
        "id": "search_keyword_density",
        "title": "Keyword Frequency Ranker (Most Mentions Per Line)",
        "category": "search",
        "code": "term = target_word.lower(); matches = sorted([(l.lower().count(term), i+1, l.strip()) for i, l in enumerate(open(filepath, 'r', encoding='utf-8', errors='ignore')) if term in l.lower()], reverse=True); print('\\n'.join([f'({cnt} mentions on L{linenum}): {content}' for cnt, linenum, content in matches]))",
        "description": "Evaluates every line in a file to count how many times a target keyword appears on that line, ranking and printing lines with the highest occurrence frequency.",
        "variables": [
            {"name": "filepath", "default": "'notes.md'", "label": "Target Document", "type": "file"},
            {"name": "target_word", "default": "secure", "label": "Target Keyword", "type": "string"}
        ]
    },
    {
        "id": "search_inverted_exclude",
        "title": "Inverted Line Exclusion Search (Like grep -v)",
        "category": "search",
        "code": "excluded = exclude_term.lower(); print('\\n'.join([f'L{i+1}: {l.strip()}' for i, l in enumerate(open(filepath, 'r', encoding='utf-8', errors='ignore')) if excluded not in l.lower()]))",
        "description": "Returns all lines in a file that do NOT contain the specified unwanted string or noise-term, cleaning up verbose log outputs.",
        "variables": [
            {"name": "filepath", "default": "'server.log'", "label": "Target Document", "type": "file"},
            {"name": "exclude_term", "default": "192.168.1.10", "label": "Term to Exclude", "type": "string"}
        ]
    },
    {
        "id": "audit_file_permissions",
        "title": "System Auditing: File Write Access Checker",
        "category": "vulnscan",
        "code": "import os; print('\\n'.join([f'{f} is WRITABLE!' for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and os.access(os.path.join(directory, f), os.W_OK)]))",
        "description": "Audits a directory to identify any files with write permissions. Useful for verifying that sensitive files are not world-writable.",
        "variables": [
            {"name": "directory", "default": "'.'", "label": "Audit Directory"}
        ]
    },
    {
        "id": "audit_env_inspector",
        "title": "System Auditing: Environment & OS Inspector",
        "category": "vulnscan",
        "code": "import sys, os, platform; print(f'Platform: {platform.system()} {platform.release()}\\nPython: {sys.version}\\nEnv Variables Count: {len(os.environ)}')",
        "description": "Displays details about the local platform, OS, Python version, and basic environment diagnostics.",
        "variables": []
    }
]

# ----------------------------------------------------
# 2. STATE VARIABLES
# ----------------------------------------------------
current_category = "all"
current_search = ""
filtered_list = []
selected_one_liner = None

# ------------c----------------------------------------
# 3. INTERACTIVE EVENT HANDLERS
# ----------------------------------------------------
def filter_and_populate_dropdown():
    global filtered_list, selected_one_liner
    
    # Filter by category and search keyword
    filtered_list = []
    for item in ONE_LINERS:
        category_matches = (current_category == "all" or item["category"] == current_category)
        search_matches = (
            not current_search 
            or current_search in item["title"].lower() 
            or current_search in item["description"].lower() 
            or current_search in item["code"].lower()
        )
        if category_matches and search_matches:
            filtered_list.append(item)
            
    # Populate dropdown select
    select_element = document.getElementById("one-liner-select")
    select_element.innerHTML = ""
    
    if not filtered_list:
        opt = document.createElement("option")
        opt.value = ""
        opt.textContent = "No matching one-liners"
        select_element.appendChild(opt)
        
        # Display empty state
        document.getElementById("one-liner-title").textContent = "No Match Found"
        document.getElementById("one-liner-category").textContent = "-"
        document.getElementById("code-display").textContent = "# Try clearing filters"
        document.getElementById("one-liner-description").textContent = "Adjust your search terms or select another category."
        document.getElementById("input-variables-group").innerHTML = ""
        document.getElementById("console-output").textContent = "No runnable code available."
        selected_one_liner = None
    else:
        for item in filtered_list:
            opt = document.createElement("option")
            opt.value = item["id"]
            opt.textContent = item["title"]
            select_element.appendChild(opt)
            
        # Select the first element by default
        display_one_liner(filtered_list[0]["id"])

def get_current_assembled_code():
    if not selected_one_liner:
        return "# No one-liner selected"
        
    var_parts = []
    for var in selected_one_liner.get("variables", []):
        var_name = var["name"]
        input_el = document.getElementById(f"arg-{var_name}")
        val_str = input_el.value.strip() if input_el else var["default"]
        if not val_str:
            val_str = ""
            
        var_type = var.get("type", "")
        if var_type == "regex" or var_name in ("regex", "regex_pattern"):
            # Automatically strip quotes if the user typed them out of habit
            if (val_str.startswith("r'") and val_str.endswith("'")) or (val_str.startswith('r"') and val_str.endswith('"')):
                val_str = val_str[2:-1]
            elif (val_str.startswith("'") and val_str.endswith("'")) or (val_str.startswith('"') and val_str.endswith('"')):
                val_str = val_str[1:-1]
            if "'" in val_str and '"' not in val_str:
                val_str = f'r"{val_str}"'
            else:
                escaped_val = val_str.replace("'", "\\'")
                val_str = f"r'{escaped_val}'"
        elif var_type in ("string", "text", "glob") or var_name in ("search_term", "target_word", "exclude_term", "query_val", "col_name", "prefix", "glob_pattern", "pattern"):
            # Automatically strip quotes if the user typed them out of habit
            if (val_str.startswith("'") and val_str.endswith("'")) or (val_str.startswith('"') and val_str.endswith('"')):
                val_str = val_str[1:-1]
            val_str = repr(val_str)
        elif not val_str:
            val_str = "''"
            
        var_parts.append(f"{var_name} = {val_str}")
        
    base_code = selected_one_liner["code"]
    if var_parts:
        return "; ".join(var_parts) + "; " + base_code
    return base_code

def update_code_display(event=None):
    if not selected_one_liner:
        return
    code_el = document.getElementById("code-display")
    code_el.textContent = get_current_assembled_code()
    
    # Re-apply Prism.js formatting if available
    try:
        if hasattr(window, 'Prism'):
            window.Prism.highlightElement(code_el)
    except Exception as e:
        print("Prism highlighting error:", e)

def display_one_liner(one_liner_id):
    global selected_one_liner
    
    # Find matching one-liner
    item = next((x for x in ONE_LINERS if x["id"] == one_liner_id), None)
    if not item:
        return
        
    selected_one_liner = item
    
    # Update UI Elements
    document.getElementById("one-liner-title").textContent = item["title"]
    document.getElementById("one-liner-category").textContent = item["category"]
    document.getElementById("one-liner-description").textContent = item["description"]
    
    # Build inputs for variables
    inputs_container = document.getElementById("input-variables-group")
    inputs_container.innerHTML = ""
    
    if not item.get("variables"):
        no_params_el = document.createElement("div")
        no_params_el.className = "no-params-msg"
        no_params_el.textContent = "No customizable parameters required for this snippet. Ready to run or copy directly!"
        inputs_container.appendChild(no_params_el)
    else:
        for var in item["variables"]:
            row = document.createElement("div")
            row.className = "playground-input-row"
            
            lbl = document.createElement("span")
            lbl.textContent = var["label"]
            row.appendChild(lbl)
            
            if var.get("type") == "file" or var["name"] in ("filepath", "filename", "file_path", "source_file"):
                file_container = document.createElement("div")
                file_container.style.display = "flex"
                file_container.style.flexDirection = "column"
                file_container.style.flex = "1"
                file_container.style.gap = "0.5rem"
                file_container.style.minWidth = "0"
                
                sel = document.createElement("select")
                sel.className = "custom-select arg-file-selector"
                sel.style.width = "100%"
                sel.style.fontSize = "0.85rem"
                sel.style.padding = "0.4rem 0.8rem"
                
                if "pasted_text.txt" not in VIRTUAL_FILES:
                    default_paste = "[2026-08-04 08:15:01] ERROR: Database connection timeout on port 5432\n[2026-08-04 08:16:22] WARN: High memory utilization detected (88%)\n[2026-08-04 08:17:10] INFO: User admin logged in successfully from IP 192.168.10.45\n[2026-08-04 08:18:05] ERROR: Authentication failed for user root from IP 10.0.0.99\nContact support at alerts@sec-ops-internal.com or admin@domain.local for escalation.\nhttps://monitoring.internal.ops/dashboard?status=critical\n"
                    try:
                        with open("pasted_text.txt", "w", encoding="utf-8", errors="ignore") as pf:
                            pf.write(default_paste)
                        VIRTUAL_FILES["pasted_text.txt"] = len(default_paste.encode("utf-8"))
                    except Exception:
                        pass
                        
                for f_name in sorted(VIRTUAL_FILES.keys()):
                    opt = document.createElement("option")
                    opt.value = f"'{f_name}'"
                    if f_name == "pasted_text.txt":
                        opt.textContent = f"📋 [Custom Pasted Buffer] ({f_name})"
                    else:
                        opt.textContent = f"📁 {f_name} (in WASM Sandbox)"
                    if opt.value == var["default"]:
                        opt.selected = True
                    sel.appendChild(opt)
                    
                inp = document.createElement("input")
                inp.type = "text"
                inp.className = "arg-input"
                inp.id = f"arg-{var['name']}"
                inp.value = sel.value or var["default"]
                inp.style.display = "none"
                
                paste_area_div = document.createElement("div")
                paste_area_div.className = "paste-buffer-container"
                paste_area_div.style.display = "flex" if "'pasted_text.txt'" in inp.value else "none"
                paste_area_div.style.flexDirection = "column"
                paste_area_div.style.gap = "0.3rem"
                paste_area_div.style.marginTop = "0.3rem"
                
                paste_hint = document.createElement("div")
                paste_hint.style.fontSize = "0.75rem"
                paste_hint.style.color = "var(--accent-orange)"
                paste_hint.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> <b>Paste or type custom text below</b> (auto-saves to <code>pasted_text.txt</code> in real time):'
                
                txt_area = document.createElement("textarea")
                txt_area.className = "custom-paste-textarea"
                txt_area.rows = 5
                try:
                    with open("pasted_text.txt", "r", encoding="utf-8", errors="ignore") as f_read:
                        txt_area.value = f_read.read()
                except Exception:
                    txt_area.value = ""
                    
                def make_paste_handler(ta_element):
                    def on_paste_change(ev):
                        try:
                            content = ta_element.value
                            with open("pasted_text.txt", "w", encoding="utf-8", errors="ignore") as pf_write:
                                pf_write.write(content)
                            VIRTUAL_FILES["pasted_text.txt"] = len(content.encode("utf-8"))
                            refresh_file_list_ui()
                        except Exception as err:
                            print("Error updating paste buffer:", err)
                    return create_proxy(on_paste_change)
                txt_area.addEventListener("input", make_paste_handler(txt_area))
                
                paste_area_div.appendChild(paste_hint)
                paste_area_div.appendChild(txt_area)
                
                def make_select_handler(select_el, input_el, paste_div):
                    def on_file_select_change(ev):
                        selected_val = select_el.value
                        input_el.value = selected_val
                        if "'pasted_text.txt'" in selected_val:
                            paste_div.style.display = "flex"
                        else:
                            paste_div.style.display = "none"
                        update_code_display()
                    return create_proxy(on_file_select_change)
                sel.addEventListener("change", make_select_handler(sel, inp, paste_area_div))
                
                file_container.appendChild(sel)
                file_container.appendChild(inp)
                file_container.appendChild(paste_area_div)
                row.appendChild(file_container)
            elif var.get("type") == "glob" or var["name"] in ("glob_pattern", "file_pattern"):
                glob_container = document.createElement("div")
                glob_container.style.display = "flex"
                glob_container.style.flexDirection = "column"
                glob_container.style.flex = "1"
                glob_container.style.gap = "0.4rem"
                glob_container.style.minWidth = "0"
                
                inp = document.createElement("input")
                inp.type = "text"
                inp.className = "arg-input"
                inp.id = f"arg-{var['name']}"
                inp.value = var["default"]
                inp.placeholder = "Type glob pattern or filename (e.g. *.*, *.py, *.csv)..."
                inp.addEventListener("input", create_proxy(update_code_display))
                
                pills_box = document.createElement("div")
                pills_box.className = "regex-pills-box"
                pills_box.style.background = "rgba(0, 0, 0, 0.3)"
                pills_box.style.border = "1px solid rgba(16, 185, 129, 0.3)"
                pills_box.style.borderRadius = "6px"
                pills_box.style.padding = "0.5rem 0.6rem"
                
                pills_header = document.createElement("div")
                pills_header.style.fontSize = "0.72rem"
                pills_header.style.color = "var(--accent-green)"
                pills_header.style.marginBottom = "0.4rem"
                pills_header.style.fontWeight = "bold"
                pills_header.innerHTML = '<i class="fa-solid fa-user-secret"></i> CTF Recon &amp; Common File Patterns (Click to insert):'
                pills_box.appendChild(pills_header)
                
                pills_grid = document.createElement("div")
                pills_grid.style.display = "flex"
                pills_grid.style.flexWrap = "wrap"
                pills_grid.style.gap = "0.4rem"
                
                common_globs = [
                    # Cyber CTF & Vulnerability Hunting Targets
                    ("🚩 CTF Flags (*flag*)", "*flag*", "Matches Capture-The-Flag target files (flag.txt, root_flag, user.txt)"),
                    ("🔑 Passwords (*pass*)", "*pass*", "Locates credential files containing 'pass' in the name (password.txt, passwd)"),
                    ("🤫 Secrets (*secret*)", "*secret*", "Finds confidential files, API tokens, and client secrets (client_secret.json)"),
                    ("🛡️ Credentials (*cred*)", "*cred*", "Scans for stored authentication credentials (credentials.xml, aws_creds)"),
                    ("⚙️ Environment Vars (*.env*)", "*.env*", "Discovers exposed dotenv config files (.env, prod.env) often storing API keys"),
                    ("🔧 Config Files (*config*)", "*config*", "Finds application configuration files (config.json, wp-config.php)"),
                    ("🔐 Private Keys (*.key)", "*.key", "Locates cryptographic private keys and SSH/RSA authentication files"),
                    ("📜 SSL/TLS Certs (*.pem)", "*.pem", "Scans for X.509 server certificate and key PEM files"),
                    ("💾 SQL DB Dumps (*.sql)", "*.sql", "Discovers exported database backups containing schema and tabular records"),
                    ("🗄️ SQLite Databases (*.db)", "*.db", "Finds local SQLite database storage files (*.db, *.sqlite)"),
                    ("📦 Backup Dumps (*.bak)", "*.bak", "Locates left-behind developer or system backup files (index.php.bak)"),
                    ("🗑️ Old Code Versions (*.old)", "*.old", "Finds unpatched or deprecated codebase backups saved with .old extension"),
                    ("🐚 Shell History (*history*)", "*history*", "Scans for command history (.bash_history) that may leak typed plaintext passwords"),
                    ("🌐 index.html (Web Root)", "index.html", "Locates web application root entry points across directory structures"),
                    # General Workspace & Data Files
                    ("📁 All Files (*.*)", "*.*", "Matches every file with an extension across all folders in the workspace"),
                    ("🐍 Python (*.py)", "*.py", "Matches all Python script source files"),
                    ("📄 Markdown (*.md)", "*.md", "Matches documentation and report files (notes.md, README.md)"),
                    ("📊 CSV Datasets (*.csv)", "*.csv", "Matches tabular spreadsheets and structured datasets (sample.csv)"),
                    ("📋 Server Logs (*.log)", "*.log", "Matches web server access, authentication, and error logs (server.log)")
                ]
                
                def make_glob_click_handler(input_element, pat_str):
                    def on_pill_click(ev):
                        ev.preventDefault()
                        input_element.value = pat_str
                        update_code_display()
                    return create_proxy(on_pill_click)
                    
                for name, pat, tooltip in common_globs:
                    btn = document.createElement("button")
                    btn.className = "regex-example-pill"
                    btn.title = f"{tooltip}: {pat}"
                    btn.style.background = "rgba(16, 185, 129, 0.1)"
                    btn.style.border = "1px solid rgba(16, 185, 129, 0.4)"
                    btn.style.color = "var(--text-primary)"
                    btn.style.fontSize = "0.75rem"
                    btn.style.padding = "0.25rem 0.55rem"
                    btn.style.borderRadius = "14px"
                    btn.style.cursor = "pointer"
                    btn.style.transition = "var(--transition-smooth)"
                    btn.style.display = "inline-flex"
                    btn.style.alignItems = "center"
                    btn.style.gap = "0.3rem"
                    btn.textContent = name
                    btn.addEventListener("click", make_glob_click_handler(inp, pat))
                    pills_grid.appendChild(btn)
                    
                pills_box.appendChild(pills_grid)
                glob_container.appendChild(inp)
                glob_container.appendChild(pills_box)
                row.appendChild(glob_container)
            elif var.get("type") == "regex" or var["name"] in ("regex", "regex_pattern"):
                regex_container = document.createElement("div")
                regex_container.style.display = "flex"
                regex_container.style.flexDirection = "column"
                regex_container.style.flex = "1"
                regex_container.style.gap = "0.4rem"
                regex_container.style.minWidth = "0"
                
                inp = document.createElement("input")
                inp.type = "text"
                inp.className = "arg-input"
                inp.id = f"arg-{var['name']}"
                inp.value = var["default"]
                inp.placeholder = "Type raw regex without quotes (e.g. POST|401 or \\d{4})..."
                inp.addEventListener("input", create_proxy(update_code_display))
                
                pills_box = document.createElement("div")
                pills_box.className = "regex-pills-box"
                pills_box.style.background = "rgba(0, 0, 0, 0.3)"
                pills_box.style.border = "1px solid rgba(255, 107, 0, 0.25)"
                pills_box.style.borderRadius = "6px"
                pills_box.style.padding = "0.5rem 0.6rem"
                
                pills_header = document.createElement("div")
                pills_header.style.fontSize = "0.72rem"
                pills_header.style.color = "var(--accent-orange)"
                pills_header.style.marginBottom = "0.4rem"
                pills_header.style.fontWeight = "bold"
                pills_header.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Popular Example Regex Searches (Click to insert):'
                pills_box.appendChild(pills_header)
                
                pills_grid = document.createElement("div")
                pills_grid.style.display = "flex"
                pills_grid.style.flexWrap = "wrap"
                pills_grid.style.gap = "0.4rem"
                
                popular_regexes = [
                    ("🌐 IPv4 Address", "(?:[0-9]{1,3}\\.){3}[0-9]{1,3}", "Matches network IPv4 addresses like 192.168.1.10"),
                    ("📧 Email Address", "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", "Matches contact email addresses"),
                    ("⚠️ HTTP Error Codes", "(?:POST|GET).*(?:401|403|404|500|502|503)", "Matches failed web access requests and status errors"),
                    ("🚨 Security / Alerts", "(?i)(?:error|warn|critical|exception|failed|timeout|denied)", "Case-insensitive scan for system warnings or errors"),
                    ("📅 Dates (YYYY-MM-DD or DD/M/Y)", "\\d{4}-\\d{2}-\\d{2}|\\d{2}/[A-Z][a-z]{2}/\\d{4}", "Matches ISO dates or system log timestamp formats"),
                    ("🔗 Web URLs & Links", "https?://[^\\s)\\'\\\"\\,]+", "Extracts HTTP and HTTPS web links"),
                    ("🔒 Cryptographic Hashes", "\\b[a-fA-F0-9]{32,64}\\b", "Matches MD5, SHA256, or hex authentication tokens"),
                    ("💳 Credit Card Numbers", "\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\\b", "PCI compliance scan for credit card sequences"),
                    ("🏷️ MAC Address", "(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})", "Matches hardware network card Ethernet MAC addresses"),
                    ("💬 Quoted Strings", "\"[^\"]*\"|'[^']*'", "Matches values contained inside double or single quotation marks")
                ]
                
                def make_regex_click_handler(input_element, pat_str):
                    def on_pill_click(ev):
                        ev.preventDefault()
                        input_element.value = pat_str
                        update_code_display()
                    return create_proxy(on_pill_click)
                    
                for name, pat, tooltip in popular_regexes:
                    btn = document.createElement("button")
                    btn.className = "regex-example-pill"
                    btn.title = f"{tooltip}: {pat}"
                    btn.style.background = "rgba(0, 153, 255, 0.1)"
                    btn.style.border = "1px solid rgba(0, 153, 255, 0.4)"
                    btn.style.color = "var(--text-primary)"
                    btn.style.fontSize = "0.75rem"
                    btn.style.padding = "0.25rem 0.55rem"
                    btn.style.borderRadius = "14px"
                    btn.style.cursor = "pointer"
                    btn.style.transition = "var(--transition-smooth)"
                    btn.style.display = "inline-flex"
                    btn.style.alignItems = "center"
                    btn.style.gap = "0.3rem"
                    btn.textContent = name
                    btn.addEventListener("click", make_regex_click_handler(inp, pat))
                    pills_grid.appendChild(btn)
                    
                pills_box.appendChild(pills_grid)
                regex_container.appendChild(inp)
                regex_container.appendChild(pills_box)
                row.appendChild(regex_container)
            else:
                inp = document.createElement("input")
                inp.type = "text"
                inp.className = "arg-input"
                inp.id = f"arg-{var['name']}"
                inp.value = var["default"]
                inp.addEventListener("input", create_proxy(update_code_display))
                row.appendChild(inp)
                
            inputs_container.appendChild(row)
            
    # Assemble and highlight live self-contained code string
    update_code_display()
        
    # Reset Console
    console_out = document.getElementById("console-output")
    console_out.textContent = 'Press "Run Code" above to execute this script in the browser sandbox.'
    console_out.classList.remove("error")
    console_out.classList.remove("warning")

def copy_to_clipboard(event):
    if not selected_one_liner:
        return
        
    code_text = get_current_assembled_code()
    
    # Write to clipboard via modern JS API
    try:
        window.navigator.clipboard.writeText(code_text)
        
        # UI Feedback
        copy_btn = document.getElementById("copy-btn")
        copy_btn_text = document.getElementById("copy-btn-text")
        
        copy_btn.classList.add("copied")
        copy_btn_text.textContent = "Copied!"
        
        # Reset after 2s
        def reset_btn():
            copy_btn.classList.remove("copied")
            copy_btn_text.textContent = "Copy Code"
            
        window.setTimeout(create_proxy(reset_btn), 2000)
    except Exception as e:
        print("Clipboard copy failed:", e)

def run_code_sandbox(event):
    if not selected_one_liner:
        return
        
    console_out = document.getElementById("console-output")
    console_out.textContent = "Executing..."
    console_out.classList.remove("error")
    console_out.classList.remove("warning")
    
    # Gather execution context
    exec_context = {}
    assembled_code = get_current_assembled_code()
        
    # Redirect stdout to capture prints
    f = io.StringIO()
    error_occurred = False
    is_warning = False
    custom_message = ""
    
    with redirect_stdout(f):
        try:
            exec(assembled_code, exec_context)
        except Exception as e:
            error_occurred = True
            err_str = str(e)
            err_code = getattr(e, 'errno', None)
            err_type = type(e).__name__
            
            # Detect Browser WebAssembly OS Socket / Binding constraints (Errno 138 / Not Supported)
            if err_code in (138, 95, 98, 111, 48) or any(k in err_str.lower() for k in ("not supported", "socket", "bind", "listen")):
                is_warning = True
                custom_message = (
                    "⚠️ [WASM Sandbox Limit: Errno 138 - Network/Socket Operation Not Supported]\n\n"
                    "Why did this happen?\n"
                    "You are testing inside a web browser using WebAssembly (PyScript). For security, standard browsers do not permit WASM applications to bind listening ports or open OS-level TCP/UDP sockets.\n\n"
                    "💡 HOW TO EXECUTE THIS SERVER / SOCKET CODE:\n"
                    "1. Customize the variable inputs above (port, target host, etc.).\n"
                    "2. Click the 'Copy Code' button above.\n"
                    "3. Open your local command prompt or terminal (PowerShell, Terminal, Bash).\n"
                    "4. Run the snippet natively on your machine:\n"
                    "   python -c \"<pasted code>\""
                )
            # Detect uninstalled external libraries
            elif isinstance(e, (ModuleNotFoundError, ImportError)):
                is_warning = True
                mod_name = getattr(e, 'name', 'required package')
                custom_message = (
                    f"⚠️ [Missing External Library in Web Sandbox: '{mod_name}']\n\n"
                    f"This script requires the third-party library '{mod_name}', which is not bundled by default in this standalone in-browser WebAssembly environment.\n\n"
                    f"💡 HOW TO EXECUTE THIS ONE-LINER:\n"
                    f"1. Install the package locally: pip install {mod_name}\n"
                    f"2. Click 'Copy Code' above and run it in your terminal with:\n"
                    f"   python -c \"<pasted code>\""
                )
            # Detect restricted OS filesystem access
            elif isinstance(e, PermissionError) or "permission denied" in err_str.lower():
                is_warning = True
                custom_message = (
                    "⚠️ [WASM Sandbox Restriction: Filesystem Access Limited]\n\n"
                    "This command attempted to query system directories outside the protected browser sandbox.\n\n"
                    "💡 Click 'Copy Code' above and run in your desktop terminal to search or modify your local files!"
                )
            else:
                custom_message = f"Runtime Exception [{err_type}]: {err_str}"
            
    output = f.getvalue().strip()
    
    if error_occurred:
        if is_warning:
            console_out.classList.add("warning")
        else:
            console_out.classList.add("error")
            
        if output:
            console_out.textContent = f"{output}\n\n{custom_message}"
        else:
            console_out.textContent = custom_message
    else:
        console_out.textContent = output or "Code completed successfully (no console output)."

def run_full_sandbox_script(event):
    console_out = document.getElementById("sandbox-console-output")
    badge_el = document.getElementById("sandbox-runtime-badge")
    editor = document.getElementById("sandbox-code-editor")
    
    if not console_out or not editor:
        return
        
    console_out.classList.remove("error", "warning")
    if badge_el:
        badge_el.textContent = "RUNNING..."
        badge_el.style.color = "var(--accent-cyan)"
        
    custom_code = editor.value
    exec_context = {"__name__": "__main__"}
    
    start_time = time.time()
    f = io.StringIO()
    error_occurred = False
    err_msg = ""
    
    with redirect_stdout(f):
        try:
            exec(custom_code, exec_context)
        except Exception:
            error_occurred = True
            err_msg = traceback.format_exc()
            
    elapsed_ms = (time.time() - start_time) * 1000.0
    output_str = f.getvalue().rstrip()
    
    if badge_el:
        badge_el.textContent = f"FINISHED ({elapsed_ms:.1f} ms)"
        badge_el.style.color = "var(--accent-green)" if not error_occurred else "var(--accent-orange)"
        
    if error_occurred:
        console_out.classList.add("error")
        if output_str:
            console_out.textContent = f"{output_str}\n\n=== RUNTIME EXCEPTION ===\n{err_msg}"
        else:
            console_out.textContent = f"=== RUNTIME EXCEPTION ===\n{err_msg}"
    else:
        console_out.textContent = output_str or "(Script executed successfully with no console print output)."

def clear_sandbox_editor(event):
    editor = document.getElementById("sandbox-code-editor")
    if editor:
        editor.value = ""
        editor.focus()

def clear_sandbox_output(event):
    console_out = document.getElementById("sandbox-console-output")
    badge_el = document.getElementById("sandbox-runtime-badge")
    if console_out:
        console_out.classList.remove("error", "warning")
        console_out.textContent = "Console cleared. Ready for execution."
    if badge_el:
        badge_el.textContent = "READY"
        badge_el.style.color = "var(--text-muted)"

def load_ctf_recon_script(event):
    editor = document.getElementById("sandbox-code-editor")
    if not editor:
        return
    ctf_script = (
        "# Automated CTF Reconnaissance & Vulnerability Discovery Script\n"
        "# This script scans the WebAssembly virtual filesystem for common security artifacts.\n"
        "import os\n"
        "import glob\n\n"
        "def scan_ctf_targets():\n"
        "    print('+' + '-'*65 + '+')\n"
        "    print('| 🕵️  AUTOMATED CTF RECON & VULNERABILITY SCAN REPORT         |')\n"
        "    print('+' + '-'*65 + '+')\n\n"
        "    # 1. Flag Discovery\n"
        "    print('\\n[1] 🚩 SCANNING FOR CTF FLAGS (*flag*)...')\n"
        "    flags = sorted(glob.glob('./**/*flag*', recursive=True))\n"
        "    for path in flags:\n"
        "        if os.path.isfile(path):\n"
        "            try:\n"
        "                with open(path, 'r', encoding='utf-8', errors='ignore') as f:\n"
        "                    val = f.read().strip()\n"
        "                print(f'   👉 Found at [{path}]:\\n      {val}')\n"
        "            except Exception as e:\n"
        "                print(f'   ⚠️ Error reading {path}: {e}')\n\n"
        "    # 2. Exposed Credentials & Passwords\n"
        "    print('\\n[2] 🔑 HUNTING FOR EXPOSED CREDENTIALS & PASSWORDS...')\n"
        "    cred_patterns = ['*pass*', '*cred*', '*secret*', '*.env*']\n"
        "    found_creds = set()\n"
        "    for pat in cred_patterns:\n"
        "        for m in glob.glob(f'./**/{pat}', recursive=True):\n"
        "            if os.path.isfile(m):\n"
        "                found_creds.add(m)\n"
        "    for path in sorted(found_creds):\n"
        "        print(f'   📂 Target Config Found: {path}')\n"
        "        try:\n"
        "            with open(path, 'r', encoding='utf-8', errors='ignore') as f:\n"
        "                lines = [l.strip() for l in f.readlines() if l.strip()][:3] # Preview first 3 lines\n"
        "            for line in lines:\n"
        "                print(f'      > {line}')\n"
        "            if not lines:\n"
        "                print('      > (Empty file)')\n"
        "        except Exception:\n"
        "            pass\n\n"
        "    # 3. Shell History Analysis\n"
        "    print('\\n[3] 🐚 ANALYZING SHELL COMMAND HISTORY (.bash_history)...')\n"
        "    for path in glob.glob('./**/*history*', recursive=True):\n"
        "        if os.path.isfile(path):\n"
        "            with open(path, 'r', encoding='utf-8', errors='ignore') as f:\n"
        "                cmds = [c.strip() for c in f.readlines() if any(w in c.lower() for w in ('ssh', 'mysql', 'pass', 'key', 'aws', 'cat'))]\n"
        "            print(f'   ⚠️ Suspicious command leaks in [{path}]:')\n"
        "            for cmd in cmds:\n"
        "                print(f'      $ {cmd}')\n\n"
        "    print('\\n+' + '-'*65 + '+')\n"
        "    print('| ✅ SCAN COMPLETE - Sandbox analysis finished without errors   |')\n"
        "    print('+' + '-'*65 + '+')\n\n"
        "if __name__ == '__main__':\n"
        "    scan_ctf_targets()\n"
    )
    editor.value = ctf_script
    print("Loaded CTF reconnaissance demo script into sandbox editor.")

# ----------------------------------------------------
# 4. INITIALIZATION AND EVENT BINDING
# ----------------------------------------------------
def handle_category_click(event):
    global current_category
    
    # Remove active class from all pills
    pills = document.querySelectorAll(".category-pill")
    for pill in pills:
        pill.classList.remove("active")
        
    # Set current clicked pill as active
    target_pill = event.currentTarget
    target_pill.classList.add("active")
    
    current_category = target_pill.getAttribute("data-category")
    filter_and_populate_dropdown()

def handle_search_input(event):
    global current_search
    current_search = event.target.value.lower()
    filter_and_populate_dropdown()

def handle_dropdown_change(event):
    display_one_liner(event.target.value)

# ----------------------------------------------------
# 5. VIRTUAL FILESYSTEM & DRAG-AND-DROP WORKSPACE
# ----------------------------------------------------
VIRTUAL_FILES = {}

def refresh_file_list_ui():
    file_list_el = document.getElementById("virtual-file-list")
    if not file_list_el:
        return
    file_list_el.innerHTML = ""
    
    if not VIRTUAL_FILES:
        empty_li = document.createElement("li")
        empty_li.className = "file-item empty-state"
        empty_li.textContent = "No files in sandbox workspace yet."
        file_list_el.appendChild(empty_li)
        return
        
    for fname, fsize in sorted(VIRTUAL_FILES.items()):
        li = document.createElement("li")
        li.className = "file-item"
        
        icon = "fa-file-lines"
        if fname.endswith(".csv") or fname.endswith(".tsv"):
            icon = "fa-file-csv"
        elif fname.endswith(".md"):
            icon = "fa-file-code"
            
        if fsize < 1024:
            size_str = f"{fsize} B"
        elif fsize < 1024 * 1024:
            size_str = f"{fsize / 1024:.1f} KB"
        else:
            size_str = f"{fsize / (1024 * 1024):.1f} MB"
            
        name_div = document.createElement("div")
        name_div.className = "file-name"
        name_div.innerHTML = f'<i class="fa-solid {icon}"></i><span>{fname}</span>'
        
        meta_div = document.createElement("div")
        meta_div.className = "file-meta"
        meta_div.innerHTML = f'<span class="file-size">{size_str}</span>'
        
        del_btn = document.createElement("button")
        del_btn.className = "btn-delete-file"
        del_btn.title = f"Delete {fname} from virtual filesystem"
        del_btn.innerHTML = '<i class="fa-solid fa-trash-can"></i>'
        
        def make_deleter(target_name):
            def delete_file(event):
                event.stopPropagation()
                try:
                    if os.path.exists(target_name):
                        os.remove(target_name)
                    VIRTUAL_FILES.pop(target_name, None)
                    refresh_file_list_ui()
                    print(f"[WASM FS] Removed file: {target_name}")
                except Exception as e:
                    print("Error deleting file:", e)
            return create_proxy(delete_file)
            
        del_btn.addEventListener("click", make_deleter(fname))
        meta_div.appendChild(del_btn)
        
        li.appendChild(name_div)
        li.appendChild(meta_div)
        file_list_el.appendChild(li)

def save_uploaded_file(name, size, content):
    try:
        with open(name, "w", encoding="utf-8", errors="ignore") as f:
            f.write(content)
        VIRTUAL_FILES[name] = size
        refresh_file_list_ui()
        print(f"[WASM FS] Uploaded file into virtual filesystem: {name} ({size} bytes)")
    except Exception as e:
        print(f"Error saving uploaded file {name}: {e}")

def setup_drag_and_drop():
    drop_zone = document.getElementById("drop-zone")
    file_input = document.getElementById("file-input")
    
    if not drop_zone or not file_input:
        return
        
    def on_drag_over(e):
        e.preventDefault()
        e.stopPropagation()
        drop_zone.classList.add("dragover")
        
    def on_drag_leave(e):
        e.preventDefault()
        e.stopPropagation()
        drop_zone.classList.remove("dragover")
        
    def on_drop(e):
        e.preventDefault()
        e.stopPropagation()
        drop_zone.classList.remove("dragover")
        if e.dataTransfer and e.dataTransfer.files:
            window.readDroppedFiles(e.dataTransfer.files, create_proxy(save_uploaded_file))
            
    def on_zone_click(e):
        file_input.click()
        
    def on_file_input_change(e):
        if file_input.files:
            window.readDroppedFiles(file_input.files, create_proxy(save_uploaded_file))
            file_input.value = ""
            
    drop_zone.addEventListener("dragover", create_proxy(on_drag_over))
    drop_zone.addEventListener("dragleave", create_proxy(on_drag_leave))
    drop_zone.addEventListener("drop", create_proxy(on_drop))
    drop_zone.addEventListener("click", create_proxy(on_zone_click))
    file_input.addEventListener("change", create_proxy(on_file_input_change))

def init_default_workspace_files():
    defaults = {
        # Standard default dataset files
        "sample.csv": "Name,Role,Score\nAlice,Admin,98\nBob,User,85\nCharlie,Analyst,91\nDavid,Developer,94\nEve,Admin,89\n",
        "server.log": "192.168.1.10 - - [04/Aug/2026:08:01:02] \"GET /index.html HTTP/1.1\" 200\n10.0.0.5 - - [04/Aug/2026:08:02:15] \"POST /login HTTP/1.1\" 401\n192.168.1.10 - - [04/Aug/2026:08:05:00] \"GET /dashboard HTTP/1.1\" 200\n172.16.0.4 - - [04/Aug/2026:08:07:33] \"GET /api/v1/user HTTP/1.1\" 200\n10.0.0.5 - - [04/Aug/2026:08:09:12] \"POST /login HTTP/1.1\" 401\n",
        "notes.md": "# Incident Investigation Report\n\n## Overview\n- Detected anomalous authentication requests from host 10.0.0.5.\n- All critical system infrastructure remains secure.\n\n## Next Steps\n- Update firewall block rules for unrecognized external gateways.\n- Rotate session authorization keys across production web clusters.\n",
        "pasted_text.txt": "[2026-08-04 08:15:01] ERROR: Database connection timeout on port 5432\n[2026-08-04 08:16:22] WARN: High memory utilization detected (88%)\n[2026-08-04 08:17:10] INFO: User admin logged in successfully from IP 192.168.10.45\n[2026-08-04 08:18:05] ERROR: Authentication failed for user root from IP 10.0.0.99\nContact support at alerts@sec-ops-internal.com or admin@domain.local for escalation.\nhttps://monitoring.internal.ops/dashboard?status=critical\n",
        
        # Cyber CTF & Vulnerability Discovery Test Target Directory (ctf_target/)
        "ctf_target/home/user_flag.txt": "CTF{w31c0m3_t0_th3_r3c0n_z0n3_usr_9923}\n",
        "ctf_target/root_flag.md": "# ROOT FLAG\nCongratulations! You penetrated the core system.\nFlag: CTF{r00t_pr1v1l3g3_3sc4l4t10n_succ3ss_8841}\n",
        "ctf_target/config/db_passwords.txt": "Admin Database Credentials:\nUser: pg_superuser\nPassword: Sup3rS3cr3tP@ssw0rd!2026\nHost: db-prod.internal.domain:5432\n",
        "ctf_target/secrets/client_secrets.json": "{\n  \"client_id\": \"oauth_id_9823984234\",\n  \"client_secret\": \"sec_prod_live_829374982374928374\",\n  \"auth_token\": \"jwt_eyJhY2NvdW50IjoiYWRtaW4iLCJpc3N1ZWQiOjE3NDEyODg5Mjh9\"\n}\n",
        "ctf_target/config/aws_creds.ini": "[default]\naws_access_key_id = AKIAIOSFODNN7EXAMPLE\naws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\nregion = us-west-2\n",
        "ctf_target/web/.env.local": "APP_ENV=production\nDEBUG=True\nDATABASE_URL=postgres://root:T0pS3cr3tDBP@ss@db.internal:5432/prod_db\nAPI_KEY=live_sk_9a87sbfb67astdasfd67as5d6\nSECRET_HASH=8f434346648f6b96df89dda901c5176b\n",
        "ctf_target/web/wp-config.php": "<?php\ndefine( 'DB_NAME', 'wordpress_prod' );\ndefine( 'DB_USER', 'wp_master_admin' );\ndefine( 'DB_PASSWORD', 'W0rdPr3ssM@st3r99!' );\ndefine( 'DB_HOST', 'localhost' );\n?>\n",
        "ctf_target/keys/id_rsa.key": "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA1234567890abcdefGHIJKLMNOPQRSTUVWXYZ/sample/key\nForCTFReconDemoVal198237198273918273918237918237918273918273918B\n-----END RSA PRIVATE KEY-----\n",
        "ctf_target/keys/server_cert.pem": "-----BEGIN CERTIFICATE-----\nMIIDdzCCAl+gAwIBAgIeAFA/demo/cert/ctf/recon/test/val918239182739\n18273918237918237918273918273918B=\n-----END CERTIFICATE-----\n",
        "ctf_target/db/users_dump.sql": "-- PostgresSQL Database Backup Dump\nCREATE TABLE users (id INT, username VARCHAR(50), password_hash VARCHAR(100));\nINSERT INTO users VALUES (1, 'admin', '$2y$10$e84azH.demo.hash.val.908234');\nINSERT INTO users VALUES (2, 'sec_analyst', '$2y$10$pL98SjkfUaKkPqA.test.hash91');\n",
        "ctf_target/db/app_storage.db": "SQLite format 3 (Simulated binary SQLite header & storage table data for CTF discovery tests)\n[TABLE system_users][col_admin_token_val_991827]\n",
        "ctf_target/web/index.php.bak": "<?php\n// Old developer backup - unpatched index page with legacy bypass\nif (isset($_GET['debug_admin_override']) && $_GET['debug_admin_override'] === 'true') {\n    $_SESSION['role'] = 'administrator';\n}\n?>\n",
        "ctf_target/backups/settings.py.old": "# Legacy Django Settings (Deprecated)\nSECRET_KEY = 'insecure-test-key-left-behind-in-old-settings-backup'\nDEBUG = True\nALLOWED_HOSTS = ['*']\n",
        "ctf_target/home/.bash_history": "ls -l\ncat /etc/passwd\nssh -i ~/ctf_target/keys/id_rsa.key root@192.168.10.150\nmysql -u root -pMasterPass99! wordpress_prod\nexport AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG\nhistory -c\n",
        "ctf_target/web/index.html": "<!DOCTYPE html>\n<html lang=\"en\">\n<head><title>Internal Admin Console - Target Portal</title></head>\n<body>\n    <h1>System Operations Center</h1>\n    <!-- WARNING: Remember to remove debug credentials before deploying! admin:Sys@dm1n2026 -->\n    <form action=\"/login\" method=\"POST\">\n        <input type=\"text\" name=\"user\" placeholder=\"Username\" />\n        <input type=\"password\" name=\"pass\" placeholder=\"Password\" />\n        <button type=\"submit\">Authenticate</button>\n    </form>\n</body>\n</html>\n"
    }
    for filename, content in defaults.items():
        try:
            dirname = os.path.dirname(filename)
            if dirname and not os.path.exists(dirname):
                os.makedirs(dirname, exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            VIRTUAL_FILES[filename] = len(content.encode("utf-8"))
        except Exception as e:
            print("Failed to initialize default file:", filename, e)
    refresh_file_list_ui()

# Bind events to HTML controls on script load
try:
    # Categories
    pills = document.querySelectorAll(".category-pill")
    for pill in pills:
        pill.addEventListener("click", create_proxy(handle_category_click))
        
    # Search
    document.getElementById("search-box").addEventListener("input", create_proxy(handle_search_input))
    
    # Dropdown select
    document.getElementById("one-liner-select").addEventListener("change", create_proxy(handle_dropdown_change))
    
    # Action buttons
    document.getElementById("copy-btn").addEventListener("click", create_proxy(copy_to_clipboard))
    document.getElementById("run-btn").addEventListener("click", create_proxy(run_code_sandbox))
    
    # Full Sandbox Mode action buttons
    run_sb = document.getElementById("btn-run-sandbox")
    if run_sb: run_sb.addEventListener("click", create_proxy(run_full_sandbox_script))
    
    clr_ed = document.getElementById("btn-clear-editor")
    if clr_ed: clr_ed.addEventListener("click", create_proxy(clear_sandbox_editor))
    
    clr_out = document.getElementById("btn-clear-sandbox-output")
    if clr_out: clr_out.addEventListener("click", create_proxy(clear_sandbox_output))
    
    load_ctf = document.getElementById("btn-load-ctf-demo")
    if load_ctf: load_ctf.addEventListener("click", create_proxy(load_ctf_recon_script))
    
    # Perform initial population
    filter_and_populate_dropdown()
    
    # Initialize virtual filesystem & drag-and-drop
    init_default_workspace_files()
    setup_drag_and_drop()
    
except Exception as init_err:
    print("PyScript Event Binding Error:", init_err)
