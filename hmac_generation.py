import hmac
import hashlib

# Tes identifiants fournis dans l'espace marchand
client_id = "djomy-client-1756569269779-996a" 
secret = "s3cr3t-UX7dltPbKjR6JWVuWak84jGzfhe6bOSD"

signature_hex = hmac.new(
    key=secret.encode(),
    msg=client_id.encode(),
    digestmod=hashlib.sha256
).hexdigest()

x_api_key = f"{client_id}:{signature_hex}"

print(f"X-API-KEY: {x_api_key}")