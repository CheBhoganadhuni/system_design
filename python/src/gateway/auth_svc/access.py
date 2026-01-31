import os, requests

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)
    
    basicAuth = (auth.username, auth.password)
    resp = requests.post(
        url=f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth=basicAuth
    )
    
    if resp.status_code != 200:
        return None, ("invalid credentials", 401)
    
    return resp.text, None