// Copyright 2023 Google LLC
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

#ifndef TINK_MAC_AES_GCM_PROTO_SERIALIZATION_H_
#define TINK_MAC_AES_GCM_PROTO_SERIALIZATION_H_

#include "tink/util/status.h"

namespace crypto {
namespace tink {

// Registers proto parsers and serializers for AES-GCM parameters and keys.
crypto::tink::util::Status RegisterAesGcmProtoSerialization();

}  // namespace tink
}  // namespace crypto

#endif  // TINK_MAC_AES_GCM_PROTO_SERIALIZATION_H_
