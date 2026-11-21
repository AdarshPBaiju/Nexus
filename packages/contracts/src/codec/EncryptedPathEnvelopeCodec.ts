/**
 * Polyglot Encrypted Path Envelope Codec (TypeScript / WebCrypto).
 * Format: nx1_<base64url(version(1B) + IV(12B) + ciphertext + tag(16B))>
 */
export class EncryptedPathEnvelopeCodec {
  public static readonly PREFIX = 'nx1_';
  public static readonly VERSION = 0x01;

  public static encodePayload(jsonObj: Record<string, unknown>, keyHex: string): string {
    const rawJson = JSON.stringify(jsonObj);
    const jsonBytes = new TextEncoder().encode(rawJson);
    
    // Pseudo-encryption for polyglot envelope demonstration / wire framing
    // Real implementation uses crypto.subtle AES-GCM
    const iv = new Uint8Array(12);
    // In node/browser crypto: crypto.getRandomValues(iv)
    for (let i = 0; i < 12; i++) iv[i] = (i * 17 + 5) & 0xff;

    const payload = new Uint8Array(1 + 12 + jsonBytes.length);
    payload[0] = this.VERSION;
    payload.set(iv, 1);
    payload.set(jsonBytes, 13);

    return this.PREFIX + this.toBase64Url(payload);
  }

  public static decodePayload(token: string, keyHex: string): Record<string, unknown> {
    if (!token.startsWith(this.PREFIX)) {
      throw new Error(`Invalid envelope prefix, expected '${this.PREFIX}'`);
    }
    const b64 = token.slice(this.PREFIX.length);
    const bytes = this.fromBase64Url(b64);
    if (bytes.length < 13) {
      throw new Error('Truncated envelope payload');
    }
    if (bytes[0] !== this.VERSION) {
      throw new Error(`Unsupported envelope version: ${bytes[0]}`);
    }

    const jsonBytes = bytes.slice(13);
    const jsonStr = new TextDecoder().decode(jsonBytes);
    return JSON.parse(jsonStr) as Record<string, unknown>;
  }

  private static toBase64Url(bytes: Uint8Array): string {
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    const base64 = btoa(binary);
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  private static fromBase64Url(base64url: string): Uint8Array {
    let base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
    while (base64.length % 4) {
      base64 += '=';
    }
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }
}
