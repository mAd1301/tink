tink_module(aead)

add_subdirectory(internal)

tink_cc_library(
  NAME aead_wrapper
  SRCS
    aead_wrapper.cc
    aead_wrapper.h
  DEPS
    absl::memory
    absl::status
    absl::strings
    tink::core::aead
    tink::core::crypto_format
    tink::core::primitive_set
    tink::core::primitive_wrapper
    tink::internal::monitoring_util
    tink::internal::registry_impl
    tink::internal::util
    tink::monitoring::monitoring
    tink::util::status
    tink::util::statusor
)

tink_cc_library(
  NAME cord_aead
  SRCS
    cord_aead.h
  DEPS
    absl::cord
    tink::util::statusor
)

tink_cc_library(
  NAME cord_aead_wrapper
  SRCS
    cord_aead_wrapper.cc
    cord_aead_wrapper.h
  DEPS
    tink::aead::cord_aead
    absl::status
    absl::cord
    tink::core::crypto_format
    tink::core::primitive_set
    tink::core::primitive_wrapper
    tink::util::status
    tink::util::statusor
)

tink_cc_library(
  NAME aead_config
  SRCS
    aead_config.cc
    aead_config.h
  DEPS
    tink::aead::aead_wrapper
    tink::aead::aes_ctr_hmac_aead_key_manager
    tink::aead::aes_eax_key_manager
    tink::aead::aes_gcm_key_manager
    tink::aead::aes_gcm_siv_key_manager
    tink::aead::kms_aead_key_manager
    tink::aead::kms_envelope_aead_key_manager
    tink::aead::xchacha20_poly1305_key_manager
    absl::core_headers
    absl::memory
    absl::status
    tink::core::registry
    tink::config::tink_fips
    tink::mac::mac_config
    tink::util::status
    tink::proto::config_cc_proto
)

tink_cc_library(
  NAME aead_factory
  SRCS
    aead_factory.cc
    aead_factory.h
  DEPS
    tink::aead::aead_wrapper
    absl::core_headers
    absl::memory
    tink::core::aead
    tink::core::key_manager
    tink::core::keyset_handle
    tink::core::registry
    tink::util::status
    tink::util::statusor
)

tink_cc_library(
  NAME aead_key_templates
  SRCS
    aead_key_templates.cc
    aead_key_templates.h
  DEPS
    absl::strings
    tink::proto::aes_ctr_cc_proto
    tink::proto::aes_ctr_hmac_aead_cc_proto
    tink::proto::aes_eax_cc_proto
    tink::proto::aes_gcm_cc_proto
    tink::proto::aes_gcm_siv_cc_proto
    tink::proto::common_cc_proto
    tink::proto::hmac_cc_proto
    tink::proto::kms_envelope_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_library(
  NAME aes_eax_key_manager
  SRCS
    aes_eax_key_manager.h
  DEPS
    absl::memory
    absl::status
    absl::strings
    tink::core::aead
    tink::core::key_type_manager
    tink::core::template_util
    tink::subtle::aes_eax_boringssl
    tink::subtle::random
    tink::util::constants
    tink::util::secret_data
    tink::util::status
    tink::util::statusor
    tink::util::validation
    tink::proto::aes_eax_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_library(
  NAME aes_gcm_key_manager
  SRCS
    aes_gcm_key_manager.h
  DEPS
    tink::aead::cord_aead
    absl::memory
    absl::status
    absl::strings
    tink::core::aead
    tink::core::key_type_manager
    tink::core::template_util
    tink::core::input_stream
    tink::aead::internal::cord_aes_gcm_boringssl
    tink::internal::fips_utils
    tink::subtle::aes_gcm_boringssl
    tink::subtle::random
    tink::util::constants
    tink::util::input_stream_util
    tink::util::secret_data
    tink::util::status
    tink::util::statusor
    tink::util::validation
    tink::proto::aes_gcm_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_library(
  NAME aes_gcm_siv_key_manager
  SRCS
    aes_gcm_siv_key_manager.h
  DEPS
    absl::memory
    absl::strings
    tink::core::aead
    tink::core::key_type_manager
    tink::core::template_util
    tink::subtle::aes_gcm_siv_boringssl
    tink::subtle::random
    tink::util::constants
    tink::util::secret_data
    tink::util::status
    tink::util::statusor
    tink::util::validation
    tink::proto::aes_gcm_siv_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_library(
  NAME aes_ctr_hmac_aead_key_manager
  SRCS
    aes_ctr_hmac_aead_key_manager.cc
    aes_ctr_hmac_aead_key_manager.h
  DEPS
    absl::memory
    absl::status
    absl::statusor
    absl::strings
    tink::core::aead
    tink::core::key_type_manager
    tink::core::template_util
    tink::core::mac
    tink::internal::fips_utils
    tink::mac::hmac_key_manager
    tink::subtle::aes_ctr_boringssl
    tink::subtle::encrypt_then_authenticate
    tink::subtle::ind_cpa_cipher
    tink::subtle::random
    tink::util::constants
    tink::util::enums
    tink::util::input_stream_util
    tink::util::secret_data
    tink::util::status
    tink::util::statusor
    tink::util::validation
    tink::proto::aes_ctr_cc_proto
    tink::proto::aes_ctr_hmac_aead_cc_proto
    tink::proto::common_cc_proto
    tink::proto::hmac_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_library(
  NAME xchacha20_poly1305_key_manager
  SRCS
    xchacha20_poly1305_key_manager.h
  DEPS
    absl::memory
    absl::status
    absl::strings
    tink::core::aead
    tink::core::key_type_manager
    tink::core::template_util
    tink::core::input_stream
    tink::subtle::subtle
    tink::subtle::xchacha20_poly1305_boringssl
    tink::util::constants
    tink::util::input_stream_util
    tink::util::secret_data
    tink::util::status
    tink::util::statusor
    tink::util::validation
    tink::proto::tink_cc_proto
    tink::proto::xchacha20_poly1305_cc_proto
)

tink_cc_library(
  NAME kms_aead_key_manager
  SRCS
    kms_aead_key_manager.h
  DEPS
    absl::memory
    absl::status
    absl::strings
    tink::core::aead
    tink::core::key_type_manager
    tink::core::template_util
    tink::core::kms_client
    tink::core::kms_clients
    tink::util::constants
    tink::util::status
    tink::util::statusor
    tink::util::validation
    tink::proto::kms_aead_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_library(
  NAME kms_envelope_aead
  SRCS
    kms_envelope_aead.cc
    kms_envelope_aead.h
  DEPS
    absl::endian
    absl::status
    absl::strings
    tink::core::aead
    tink::core::registry
    tink::util::status
    tink::util::statusor
    tink::proto::tink_cc_proto
)

tink_cc_library(
  NAME kms_envelope_aead_key_manager
  SRCS
    kms_envelope_aead_key_manager.cc
    kms_envelope_aead_key_manager.h
  DEPS
    tink::aead::kms_envelope_aead
    absl::memory
    absl::status
    absl::strings
    tink::core::aead
    tink::core::key_type_manager
    tink::core::template_util
    tink::core::kms_client
    tink::core::kms_clients
    tink::internal::fips_utils
    tink::util::constants
    tink::util::status
    tink::util::statusor
    tink::util::validation
    tink::proto::kms_envelope_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_library(
  NAME mock_aead
  SRCS
    mock_aead.h
  DEPS
    gmock
    absl::strings
    tink::core::aead
    tink::util::statusor
  TESTONLY
)

tink_cc_library(
  NAME failing_aead
  SRCS
    failing_aead.cc
    failing_aead.h
  DEPS
    absl::strings
    tink::core::aead
  TESTONLY
)

tink_cc_library(
  NAME aead_parameters
  SRCS
    aead_parameters.h
  DEPS
    tink::core::parameters
)

tink_cc_library(
  NAME aead_key
  SRCS
    aead_key.h
  DEPS
    tink::aead::aead_parameters
    absl::strings
    tink::core::key
)

tink_cc_library(
  NAME aes_gcm_parameters
  SRCS
    aes_gcm_parameters.cc
    aes_gcm_parameters.h
  DEPS
    tink::aead::aead_parameters
    absl::strings
    tink::util::status
    tink::util::statusor
)

tink_cc_library(
  NAME aes_gcm_key
  SRCS
    aes_gcm_key.cc
    aes_gcm_key.h
  DEPS
    tink::aead::aead_key
    tink::aead::aes_gcm_parameters
    absl::strings
    absl::optional
    tink::core::partial_key_access_token
    tink::core::restricted_data
    tink::subtle::subtle_util
    tink::util::status
    tink::util::statusor
)

tink_cc_library(
  NAME aes_gcm_proto_serialization
  SRCS
    aes_gcm_proto_serialization.cc
    aes_gcm_proto_serialization.h
  DEPS
    tink::aead::aes_gcm_key
    tink::aead::aes_gcm_parameters
    absl::status
    absl::optional
    tink::core::partial_key_access
    tink::core::restricted_data
    tink::core::secret_key_access_token
    tink::internal::key_parser
    tink::internal::key_serializer
    tink::internal::mutable_serialization_registry
    tink::internal::parameters_parser
    tink::internal::parameters_serializer
    tink::internal::proto_key_serialization
    tink::internal::proto_parameters_serialization
    tink::util::status
    tink::util::statusor
    tink::proto::aes_gcm_cc_proto
    tink::proto::tink_cc_proto
)

# tests

tink_cc_test(
  NAME aead_wrapper_test
  SRCS
    aead_wrapper_test.cc
  DEPS
    tink::aead::aead_wrapper
    tink::aead::mock_aead
    gmock
    absl::flat_hash_map
    absl::memory
    absl::status
    absl::statusor
    absl::strings
    tink::core::aead
    tink::core::crypto_format
    tink::core::primitive_set
    tink::core::registry
    tink::internal::registry_impl
    tink::monitoring::monitoring
    tink::monitoring::monitoring_client_mocks
    tink::util::status
    tink::util::statusor
    tink::util::test_matchers
    tink::util::test_util
    tink::proto::tink_cc_proto
)

tink_cc_test(
  NAME aead_config_test
  SRCS
    aead_config_test.cc
  DEPS
    tink::aead::aead_config
    tink::aead::aead_key_templates
    tink::aead::aes_gcm_key_manager
    gmock
    absl::memory
    absl::status
    tink::core::aead
    tink::core::keyset_handle
    tink::core::primitive_set
    tink::core::registry
    tink::config::tink_fips
    tink::internal::fips_utils
    tink::util::status
    tink::util::statusor
    tink::util::test_matchers
    tink::proto::tink_cc_proto
)

tink_cc_test(
  NAME aead_factory_test
  SRCS
    aead_factory_test.cc
  DEPS
    tink::aead::aead_config
    tink::aead::aead_factory
    tink::aead::aes_gcm_key_manager
    gmock
    absl::status
    absl::strings
    tink::core::aead
    tink::core::crypto_format
    tink::core::keyset_handle
    tink::internal::key_info
    tink::util::status
    tink::util::statusor
    tink::util::test_keyset_handle
    tink::util::test_util
    tink::proto::aes_gcm_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_test(
  NAME aead_key_templates_test
  SRCS
    aead_key_templates_test.cc
  DEPS
    tink::aead::aead_config
    tink::aead::aead_key_templates
    tink::aead::aes_ctr_hmac_aead_key_manager
    tink::aead::aes_eax_key_manager
    tink::aead::aes_gcm_key_manager
    tink::aead::aes_gcm_siv_key_manager
    tink::aead::kms_envelope_aead_key_manager
    tink::aead::xchacha20_poly1305_key_manager
    gmock
    absl::status
    absl::statusor
    tink::core::aead
    tink::core::key_manager_impl
    tink::core::key_manager
    tink::core::keyset_handle
    tink::subtle::aead_test_util
    tink::util::fake_kms_client
    tink::util::status
    tink::util::test_matchers
    tink::proto::aes_ctr_cc_proto
    tink::proto::aes_ctr_hmac_aead_cc_proto
    tink::proto::aes_eax_cc_proto
    tink::proto::aes_gcm_cc_proto
    tink::proto::aes_gcm_siv_cc_proto
    tink::proto::common_cc_proto
    tink::proto::hmac_cc_proto
    tink::proto::kms_envelope_cc_proto
    tink::proto::tink_cc_proto
    tink::proto::xchacha20_poly1305_cc_proto
)

tink_cc_test(
  NAME aes_eax_key_manager_test
  SRCS
    aes_eax_key_manager_test.cc
  DEPS
    tink::aead::aes_eax_key_manager
    gmock
    tink::core::aead
    tink::subtle::aead_test_util
    tink::subtle::aes_eax_boringssl
    tink::util::secret_data
    tink::util::status
    tink::util::statusor
    tink::util::test_matchers
    tink::proto::aes_eax_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_test(
  NAME aes_gcm_key_manager_test
  SRCS
    aes_gcm_key_manager_test.cc
  DEPS
    tink::aead::aes_gcm_key_manager
    tink::aead::cord_aead
    gmock
    absl::memory
    absl::status
    tink::core::aead
    tink::aead::internal::cord_aes_gcm_boringssl
    tink::subtle::aead_test_util
    tink::subtle::aes_gcm_boringssl
    tink::util::istream_input_stream
    tink::util::secret_data
    tink::util::status
    tink::util::statusor
    tink::util::test_matchers
    tink::proto::aes_gcm_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_test(
  NAME aes_gcm_siv_key_manager_test
  SRCS
    aes_gcm_siv_key_manager_test.cc
  DEPS
    tink::aead::aes_gcm_siv_key_manager
    gmock
    absl::status
    tink::core::aead
    tink::internal::ssl_util
    tink::subtle::aead_test_util
    tink::subtle::aes_gcm_siv_boringssl
    tink::util::secret_data
    tink::util::status
    tink::util::statusor
    tink::util::test_matchers
    tink::proto::aes_gcm_siv_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_test(
  NAME aes_ctr_hmac_aead_key_manager_test
  SRCS
    aes_ctr_hmac_aead_key_manager_test.cc
  DEPS
    tink::aead::aes_ctr_hmac_aead_key_manager
    gmock
    absl::status
    tink::core::aead
    tink::subtle::subtle
    tink::subtle::aead_test_util
    tink::subtle::aes_ctr_boringssl
    tink::util::enums
    tink::util::istream_input_stream
    tink::util::secret_data
    tink::util::status
    tink::util::statusor
    tink::util::test_matchers
    tink::proto::aes_ctr_cc_proto
    tink::proto::aes_ctr_hmac_aead_cc_proto
    tink::proto::common_cc_proto
    tink::proto::hmac_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_test(
  NAME xchacha20_poly1305_key_manager_test
  SRCS
    xchacha20_poly1305_key_manager_test.cc
  DEPS
    tink::aead::xchacha20_poly1305_key_manager
    gmock
    absl::memory
    absl::status
    tink::core::aead
    tink::internal::ssl_util
    tink::subtle::aead_test_util
    tink::subtle::xchacha20_poly1305_boringssl
    tink::util::istream_input_stream
    tink::util::secret_data
    tink::util::status
    tink::util::statusor
    tink::util::test_matchers
    tink::proto::tink_cc_proto
    tink::proto::xchacha20_poly1305_cc_proto
)

tink_cc_test(
  NAME kms_aead_key_manager_test
  SRCS
    kms_aead_key_manager_test.cc
  DEPS
    tink::aead::kms_aead_key_manager
    gmock
    absl::memory
    absl::status
    tink::core::aead
    tink::core::kms_client
    tink::core::kms_clients
    tink::subtle::aead_test_util
    tink::util::status
    tink::util::statusor
    tink::util::test_matchers
    tink::util::test_util
    tink::proto::kms_aead_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_test(
  NAME kms_envelope_aead_test
  SRCS
    kms_envelope_aead_test.cc
  DEPS
    tink::aead::aead_config
    tink::aead::aead_key_templates
    tink::aead::kms_envelope_aead
    gmock
    absl::endian
    absl::memory
    absl::status
    absl::strings
    tink::core::aead
    tink::core::keyset_handle
    tink::core::registry
    tink::internal::ssl_util
    tink::mac::mac_key_templates
    tink::util::status
    tink::util::statusor
    tink::util::test_matchers
    tink::util::test_util
    tink::proto::aes_gcm_cc_proto
)

tink_cc_test(
  NAME kms_envelope_aead_key_manager_test
  SRCS
    kms_envelope_aead_key_manager_test.cc
  DEPS
    tink::aead::aead_config
    tink::aead::aead_key_templates
    tink::aead::aes_eax_key_manager
    tink::aead::kms_envelope_aead
    tink::aead::kms_envelope_aead_key_manager
    gmock
    absl::memory
    absl::status
    tink::core::aead
    tink::core::kms_client
    tink::core::kms_clients
    tink::core::registry
    tink::subtle::aead_test_util
    tink::util::fake_kms_client
    tink::util::status
    tink::util::statusor
    tink::util::test_matchers
    tink::util::test_util
    tink::proto::kms_envelope_cc_proto
    tink::proto::tink_cc_proto
)

tink_cc_test(
  NAME cord_aead_wrapper_test
  SRCS
    cord_aead_wrapper_test.cc
  DEPS
    tink::aead::cord_aead
    tink::aead::cord_aead_wrapper
    gmock
    absl::memory
    absl::status
    absl::strings
    absl::cord
    tink::core::primitive_set
    tink::util::status
    tink::util::test_matchers
    tink::util::test_util
    tink::proto::tink_cc_proto
)

tink_cc_test(
  NAME failing_aead_test
  SRCS
    failing_aead_test.cc
  DEPS
    tink::aead::failing_aead
    gmock
    absl::status
    tink::util::test_matchers
)

tink_cc_test(
  NAME aes_gcm_parameters_test
  SRCS
    aes_gcm_parameters_test.cc
  DEPS
    tink::aead::aes_gcm_parameters
    gmock
    tink::util::statusor
    tink::util::test_matchers
)

tink_cc_test(
  NAME aes_gcm_key_test
  SRCS
    aes_gcm_key_test.cc
  DEPS
    tink::aead::aes_gcm_key
    tink::aead::aes_gcm_parameters
    gmock
    absl::optional
    tink::core::partial_key_access
    tink::core::restricted_data
    tink::util::statusor
    tink::util::test_matchers
)

tink_cc_test(
  NAME aes_gcm_proto_serialization_test
  SRCS
    aes_gcm_proto_serialization_test.cc
  DEPS
    tink::aead::aes_gcm_key
    tink::aead::aes_gcm_parameters
    tink::aead::aes_gcm_proto_serialization
    gmock
    tink::core::insecure_secret_key_access
    tink::core::partial_key_access
    tink::core::restricted_data
    tink::internal::mutable_serialization_registry
    tink::internal::proto_key_serialization
    tink::internal::proto_parameters_serialization
    tink::subtle::random
    tink::util::test_matchers
    tink::proto::aes_gcm_cc_proto
    tink::proto::tink_cc_proto
)
