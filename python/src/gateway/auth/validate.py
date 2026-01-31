import os, requests

def token(request):
    if not request.headers.get("Authorization"):
        return None, ("missing token", 401)
    
    token = request.headers.get("Authorization")

    if not token:
        return None, ("missing token", 401)
    
    resp = requests.post(
        url=f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token}
    )
    
    if resp.status_code != 200:
        return None, ("invalid token", 401)
    
    return resp.text, None