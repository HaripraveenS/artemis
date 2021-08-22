# Artemis
## HTTP Proxy Server
An HTTP proxy server implemented via python socket programming with caching, blacklisting, and authentication.

## Description 
- `proxy.py` is the main proxy server file. 
- By default the proxy port is set to 8079, and a maximum of 10 active clients are allowed.
- GET and POST requests are handled.
- `client.py` contains code for a single client, with inputs for the HTTP request and username:password.
- `client_testing.py` contains code for multithreaded testing (multiple clients making multiple requests).

## Usage
- Run `proxy.py -server_port x -active_clients y -cache_size z`.
- By default the values are 8079 (server_port), 10 (active_clients), 5 (cache_size).
- Run `client.py`, enter the HTTP request and username:password.
- By default `GET www.google.com/ HTTP/1.1` is sent.
- Blacklisted URLs are added to `./blacklist.txt`.
- Admins are added to `./admins.txt`. Admins have access to blacklisted URLs.
- Files are saved to cache, upon exceeding cache size, last accessed URL is removed from cache.
- To test multithreading, simply run `client_testing.py`. Multiple client sockets will send requests.

## Avenues of Exploration:
- Handle HTTPS requests.
- Secure against MitM attacks.
- Handle one-time authentication, remove repeated authentication headers.
