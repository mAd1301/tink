// Copyright 2017 Google Inc.
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

package com.google.crypto.tink.hybrid;

import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;

import com.google.crypto.tink.HybridDecrypt;
import com.google.crypto.tink.HybridEncrypt;
import com.google.crypto.tink.Parameters;
import com.google.crypto.tink.TinkProtoParametersFormat;
import com.google.crypto.tink.aead.PredefinedAeadParameters;
import com.google.crypto.tink.daead.PredefinedDeterministicAeadParameters;
import com.google.crypto.tink.proto.HashType;
import com.google.crypto.tink.proto.KeyTemplate;
import com.google.crypto.tink.subtle.EciesAeadHkdfHybridDecrypt;
import com.google.crypto.tink.subtle.EciesAeadHkdfHybridEncrypt;
import com.google.crypto.tink.subtle.EllipticCurves;
import com.google.crypto.tink.subtle.EllipticCurves.CurveType;
import com.google.crypto.tink.subtle.Random;
import com.google.crypto.tink.testing.TestUtil;
import com.google.protobuf.ExtensionRegistryLite;
import java.security.GeneralSecurityException;
import java.security.KeyPair;
import java.security.interfaces.ECPrivateKey;
import java.security.interfaces.ECPublicKey;
import java.util.Set;
import java.util.TreeSet;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

/**
 * Unit tests for EciesAeadHkdfHybridEncrypt.
 *
 * <p>TODO(b/74250701): Add more tests.
 */
@RunWith(JUnit4.class)
public class EciesAeadHkdfHybridEncryptTest {
  @Before
  public void setUp() throws GeneralSecurityException {
    HybridConfig.register();
  }

  private void testBasicMultipleEncrypts(CurveType curveType, Parameters parameters)
      throws Exception {
    KeyTemplate keyTemplate =
        KeyTemplate.parseFrom(
            TinkProtoParametersFormat.serialize(parameters),
            ExtensionRegistryLite.getEmptyRegistry());
    KeyPair recipientKey = EllipticCurves.generateKeyPair(curveType);
    ECPublicKey recipientPublicKey = (ECPublicKey) recipientKey.getPublic();
    ECPrivateKey recipientPrivateKey = (ECPrivateKey) recipientKey.getPrivate();
    byte[] salt = "some salt".getBytes("UTF-8");
    byte[] plaintext = Random.randBytes(20);
    byte[] context = "context info".getBytes("UTF-8");
    String hmacAlgo = HybridUtil.toHmacAlgo(HashType.SHA256);
    HybridEncrypt hybridEncrypt =
        new EciesAeadHkdfHybridEncrypt(
            recipientPublicKey,
            salt,
            hmacAlgo,
            EllipticCurves.PointFormatType.UNCOMPRESSED,
            new RegistryEciesAeadHkdfDemHelper(keyTemplate));
    HybridDecrypt hybridDecrypt =
        new EciesAeadHkdfHybridDecrypt(
            recipientPrivateKey,
            salt,
            hmacAlgo,
            EllipticCurves.PointFormatType.UNCOMPRESSED,
            new RegistryEciesAeadHkdfDemHelper(keyTemplate));

    // Makes sure that the encryption is randomized.
    Set<String> ciphertexts = new TreeSet<String>();
    for (int j = 0; j < 8; j++) {
      byte[] ciphertext = hybridEncrypt.encrypt(plaintext, context);
      if (ciphertexts.contains(new String(ciphertext, "UTF-8"))) {
        throw new GeneralSecurityException("Encryption is not randomized");
      }
      ciphertexts.add(new String(ciphertext, "UTF-8"));
      byte[] decrypted = hybridDecrypt.decrypt(ciphertext, context);
      assertArrayEquals(plaintext, decrypted);
    }
    assertEquals(8, ciphertexts.size());
  }

  @Test
  public void testBasicMultipleEncrypts() throws Exception {
    testBasicMultipleEncrypts(CurveType.NIST_P256, PredefinedAeadParameters.AES128_CTR_HMAC_SHA256);
    testBasicMultipleEncrypts(CurveType.NIST_P384, PredefinedAeadParameters.AES128_CTR_HMAC_SHA256);
    testBasicMultipleEncrypts(CurveType.NIST_P521, PredefinedAeadParameters.AES128_CTR_HMAC_SHA256);

    testBasicMultipleEncrypts(
        CurveType.NIST_P521, PredefinedDeterministicAeadParameters.AES256_SIV);

    if (!TestUtil.isAndroid()) {
      testBasicMultipleEncrypts(CurveType.NIST_P256, PredefinedAeadParameters.AES128_GCM);
      testBasicMultipleEncrypts(CurveType.NIST_P384, PredefinedAeadParameters.AES128_GCM);
      testBasicMultipleEncrypts(CurveType.NIST_P521, PredefinedAeadParameters.AES128_GCM);
    }
  }
}
