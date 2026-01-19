# generate_hash.py
import bcrypt

def generate_password_hash(password):
    """Gera um hash bcrypt para a senha."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

# Exemplo de uso
if __name__ == "__main__":
    # Gera hash para novos usuários
    senhas = {
        "admin": "Gft@123_26",
        "guest": "guest456",
        "gft": "gft26"  # Mantém o mesmo
    }
    
    for usuario, senha in senhas.items():
        hash_result = generate_password_hash(senha)
        print(f'{usuario} = "{hash_result}"')