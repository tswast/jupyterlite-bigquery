
def hello():
    return "Hello from bigquery-lite!"

async def auth():
    """
    Opens a pop-up browser window to read an authentication string.
    """
    import js
    import asyncio
    try:
        from pyodide.ffi import create_proxy
    except ImportError:
        # Fallback for non-pyodide environments if necessary,
        # though this package is intended for JupyterLite.
        raise ImportError("auth() requires a Pyodide environment (JupyterLite).")

    loop = asyncio.get_event_loop()
    future = loop.create_future()

    def on_token(token):
        if not future.done():
            future.set_result(token)

    proxy = create_proxy(on_token)
    js.window.onBigQueryToken = proxy

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BigQuery Auth</title>
        <style>
            body { font-family: sans-serif; padding: 20px; }
            input { width: 100%; padding: 8px; margin: 10px 0; box-sizing: border-box; }
            button { padding: 10px 20px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h3>BigQuery Authentication</h3>
        <p>Please enter your authentication token:</p>
        <input type="text" id="token_input" placeholder="Paste token here...">
        <br>
        <button id="submit_btn">Submit</button>
        <script>
            document.getElementById('submit_btn').onclick = function() {
                var token = document.getElementById('token_input').value;
                if (window.opener && window.opener.onBigQueryToken) {
                    window.opener.onBigQueryToken(token);
                }
                window.close();
            };
        </script>
    </body>
    </html>
    """

    w = js.window.open("", "bigquery_auth", "width=400,height=250")
    if not w:
        proxy.destroy()
        raise RuntimeError("Pop-up window blocked or failed to open. Please allow pop-ups for this site.")

    w.document.write(html)
    w.document.close()

    try:
        result = await future
    finally:
        proxy.destroy()
        js.eval("delete window.onBigQueryToken")

    return result
