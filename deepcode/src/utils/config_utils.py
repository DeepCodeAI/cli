def handle_backend_host_last_slash(backend_host):
    last_symbol_index = len(backend_host)-1
    print(backend_host)
    return backend_host[:last_symbol_index] if backend_host[last_symbol_index] == '/' else backend_host
