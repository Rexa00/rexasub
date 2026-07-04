import base64
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_ips import decode_payload, extract_ips_from_text


class FetchIpsTests(unittest.TestCase):
    def test_extract_ips_from_vless_payload(self) -> None:
        payload = """
        vless://abc@104.18.0.0:443?security=tls&type=ws
        vless://abc@104.18.1.1:443?security=tls&type=ws
        """
        self.assertEqual(extract_ips_from_text(payload), ["104.18.0.0", "104.18.1.1"])

    def test_decode_payload_from_base64(self) -> None:
        plain = "vless://abc@104.18.0.0:443"
        encoded = base64.b64encode(plain.encode("utf-8")).decode("ascii")
        self.assertEqual(decode_payload(encoded), plain)

    def test_extract_ips_from_domain_host(self) -> None:
        payload = "vless://abc@example.com:443"
        self.assertEqual(
            extract_ips_from_text(payload, resolver=lambda host: ["93.184.216.34"]),
            ["93.184.216.34"],
        )

    def test_extract_ips_from_vmess_payload(self) -> None:
        payload = "vmess://" + base64.b64encode(b'{"add":"127.0.0.1","port":"443","id":"abc"}').decode("ascii")
        self.assertEqual(extract_ips_from_text(payload), ["127.0.0.1"])


if __name__ == "__main__":
    unittest.main()
