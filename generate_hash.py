import bcrypt

senha = "gft123"   # a senha simples que você quer
hash_ = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
print(hash_.decode())
