// Copyright 2020 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
////////////////////////////////////////////////////////////////////////////////

package subtle

import (
	"errors"
	"fmt"

	"golang.org/x/crypto/chacha20poly1305"
	"github.com/google/tink/go/subtle/random"
	"github.com/google/tink/go/tink"
)

const (
	poly1305TagSize = 16
)

// ChaCha20Poly1305 is an implementation of AEAD interface.
type ChaCha20Poly1305 struct {
	Key []byte
}

// Assert that ChaCha20Poly1305 implements the AEAD interface.
var _ tink.AEAD = (*ChaCha20Poly1305)(nil)

// NewChaCha20Poly1305 returns an ChaCha20Poly1305 instance.
// The key argument should be a 32-bytes key.
func NewChaCha20Poly1305(key []byte) (*ChaCha20Poly1305, error) {
	if len(key) != chacha20poly1305.KeySize {
		return nil, errors.New("chacha20poly1305: bad key length")
	}

	return &ChaCha20Poly1305{Key: key}, nil
}

// Encrypt encrypts plaintext with associatedData.
//
// The resulting ciphertext consists of two parts:
//  1. the nonce used for encryption
//  2. the actual ciphertext
func (ca *ChaCha20Poly1305) Encrypt(plaintext []byte, associatedData []byte) ([]byte, error) {
	if len(plaintext) > maxInt-chacha20poly1305.NonceSize-poly1305TagSize {
		return nil, fmt.Errorf("chacha20poly1305: plaintext too long")
	}
	c, err := chacha20poly1305.New(ca.Key)
	if err != nil {
		return nil, err
	}

	nonce := random.GetRandomBytes(chacha20poly1305.NonceSize)
	// Set dst's capacity to fit the nonce and ciphertext.
	dst := make([]byte, 0, chacha20poly1305.NonceSize+len(plaintext)+c.Overhead())
	dst = append(dst, nonce...)
	// Seal appends the ciphertext to dst. So the final output is: nonce || ciphertext.
	return c.Seal(dst, nonce, plaintext, associatedData), nil
}

// Decrypt decrypts ciphertext with associatedData.
// 
// ciphertext consists of two parts:
//  1. the nonce used for encryption
//  2. the actual ciphertext
func (ca *ChaCha20Poly1305) Decrypt(ciphertext []byte, associatedData []byte) ([]byte, error) {
	if len(ciphertext) < chacha20poly1305.NonceSize+poly1305TagSize {
		return nil, fmt.Errorf("chacha20poly1305: ciphertext too short")
	}

	c, err := chacha20poly1305.New(ca.Key)
	if err != nil {
		return nil, err
	}

	nonce := ciphertext[:chacha20poly1305.NonceSize]
	pt, err := c.Open(nil, nonce, ciphertext[chacha20poly1305.NonceSize:] /*=ciphertext*/, associatedData)
	if err != nil {
		return nil, fmt.Errorf("ChaCha20Poly1305.Decrypt: %v", err)
	}
	return pt, nil
}
