import os
import base64
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

def generate_rsa_keys(key_size=2048, output_dir="rsa_keys"):
    """
    生成指定数量的 RSA 密钥对，并将其保存到文件。
    
    :param num_keys: 需要生成的密钥对数量。
    :param key_size: RSA 密钥长度（默认为 2048 位）。
    :param output_dir: 输出目录，用于保存生成的密钥文件。
    """
    
    # 创建存储密钥的目录
    os.makedirs(output_dir, exist_ok=True)

    
    # 生成 RSA 密钥
    key = RSA.generate(key_size)

    # 获取私钥和公钥（PEM 格式）
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    print(private_key)
    print(public_key)

    # 将密钥保存到文件
    private_key_path = os.path.join(output_dir, f"private_key.pem")
    public_key_path = os.path.join(output_dir, f"public_key.pem")
    
    with open(private_key_path, 'wb') as priv_file:
        priv_file.write(private_key)
    
    with open(public_key_path, 'wb') as pub_file:
        pub_file.write(public_key)

    
    print(f"  私钥文件: {private_key_path}")
    print(f"  公钥文件: {public_key_path}")

    return public_key

# 生成AES密钥
def generate_aes_key(key_size=128):
    """
    生成AES密钥。
    :param key_size: 密钥长度（16, 24, 32字节分别对应AES-128, AES-192, AES-256）
    :return: AES密钥
    """
    return get_random_bytes(key_size)

# 使用RSA公钥加密AES密钥
def encrypt_aes_key_with_rsa(aes_key, rsa_public_key_pem):
    """
    使用RSA公钥加密AES密钥。
    :param aes_key: AES密钥
    :param rsa_public_key_pem: RSA公钥（PEM格式）
    :return: 加密后的AES密钥（字节形式）
    """
    # 加载RSA公钥
    public_key = RSA.import_key(rsa_public_key_pem)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_aes_key = cipher_rsa.encrypt(aes_key)
    return encrypted_aes_key

# Base64 解码
def base64_decode(encoded_text):
    """
    将 Base64 字符串解码为原始字符串。
    :param encoded_text: Base64 编码的字符串
    :return: 解码后的原始字符串
    """
    # 将 Base64 字符串解码为字节数据
    decoded_bytes = base64.b64decode(encoded_text.encode('utf-8'))
    # 转换为字符串返回
    return decoded_bytes.decode('utf-8')

# 转换为Base64字符串
def convert_to_base64(data):
    """
    将字节数据转换为Base64字符串。
    :param data: 字节数据
    :return: Base64字符串
    """
    return base64.b64encode(data).decode('utf-8')


def chat():
        headers = {"content-type": "application/json", "Authorization": self.token}
        data = {
            "task_history":[],
            "query": self.query,
            "query_type":"1",
            "model_id": self.model_id,
            "patient_id": self.patientid,
            "model": self.model
            }
# 主函数示例
if __name__ == "__main__":
    #生成RSA公钥和私钥
    public_key_test = generate_rsa_keys(key_size=2048, output_dir="rsa_keys")

    # 生成AES密钥
    aes_key = generate_aes_key()
    print(f"AES密钥 (Base64): {convert_to_base64(aes_key)}")
    
    # 示例RSA公钥（PEM格式）
    rsa_public_key_pem = """
    -----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDxDLDYby2D63Dh1kIN5/Yl6FMR
    FkGu3zJYghMZJGrnI6g5MmBQ5Ynm4+4pY9X7a6/SJKgN3AQJPA3ZZRmE5hkAK8QV
    xxPUOrOfmymZ4mTyNo2EsX2P/oIVm04CvQZKkOX69FOMxoZUtThR0WjbYSSt6o3v
    4jLchC6EY7KoVwIDAQAB
    -----END PUBLIC KEY-----
    """
    
    # 使用RSA公钥加密AES密钥
    encrypted_aes_key = encrypt_aes_key_with_rsa(aes_key, public_key_test)
    print(encrypted_aes_key)
    print(f"加密后的AES密钥 (Base64): {convert_to_base64(encrypted_aes_key)}")