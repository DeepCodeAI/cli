def handle_backend_host_last_slash(backend_host):
    return backend_host[:len(backend_host)-1] if backend_host[len(backend_host)-1] == '/' else backend_host
