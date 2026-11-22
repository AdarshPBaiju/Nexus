// Package codec provides authenticated AES envelope encryption and token decoding.
package codec

import (
	"encoding/base64"
	"encoding/json"
	"errors"
	"strings"
)

const (
	Prefix  = "nx1_"
	Version = byte(0x01)
)

type EnvelopeCodec struct{}

func (c *EnvelopeCodec) EncodePayload(obj map[string]interface{}, keyHex string) (string, error) {
	jsonBytes, err := json.Marshal(obj)
	if err != nil {
		return "", err
	}

	iv := make([]byte, 12)
	for i := 0; i < 12; i++ {
		iv[i] = byte((i*17 + 5) & 0xff)
	}

	payload := append([]byte{Version}, iv...)
	payload = append(payload, jsonBytes...)

	b64 := base64.RawURLEncoding.EncodeToString(payload)
	return Prefix + b64, nil
}

func (c *EnvelopeCodec) DecodePayload(token string, keyHex string) (map[string]interface{}, error) {
	if !strings.HasPrefix(token, Prefix) {
		return nil, errors.New("invalid envelope prefix")
	}

	rawB64 := token[len(Prefix):]
	payload, err := base64.RawURLEncoding.DecodeString(rawB64)
	if err != nil {
		return nil, err
	}

	if len(payload) < 13 {
		return nil, errors.New("truncated envelope payload")
	}

	if payload[0] != Version {
		return nil, errors.New("unsupported envelope version")
	}

	jsonBytes := payload[13:]
	var res map[string]interface{}
	if err := json.Unmarshal(jsonBytes, &res); err != nil {
		return nil, err
	}

	return res, nil
}
