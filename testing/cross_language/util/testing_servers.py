# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""testing_server starts up testing gRPC servers in different languages."""

import os
import subprocess
import time

from typing import List, Optional, Type, TypeVar
from absl import logging
import grpc
import portpicker
import tink

from tink.proto import tink_pb2
from util import _primitives
from protos import testing_api_pb2
from protos import testing_api_pb2_grpc

P = TypeVar('P')

# Server paths are relative to a root folder where all the server are located.
# It can be set manually as follows:
#   bazel test util:testing_servers_test \
#     --test_env TINK_CROSS_LANG_ROOT_PATH=<path to the root folder>
_SERVER_PATHS = {
    'cc': ['cc/bazel-bin/testing_server', 'cc/testing_server'],
    'go': ['go/bazel-bin/testing_server_/testing_server', 'go/testing_server'],
    'java': [
        'java_src/bazel-bin/testing_server_deploy.jar',
        'java_src/testing_server'
    ],
    'python': ['python/bazel-bin/testing_server', 'python/testing_server']
}

# All languages that have a testing server
LANGUAGES = list(_SERVER_PATHS.keys())

KEYSET_READER_WRITER_TYPES = [('KEYSET_READER_BINARY', 'KEYSET_WRITER_BINARY'),
                              ('KEYSET_READER_JSON', 'KEYSET_WRITER_JSON')]

# location of the testing_server java binary, relative to the root folder where
# all the server are located.
_JAVA_PATH = ('java_src/bazel-bin/testing_server.runfiles/local_jdk/bin/java')

_PRIMITIVE_STUBS = {
    'aead': testing_api_pb2_grpc.AeadStub,
    'daead': testing_api_pb2_grpc.DeterministicAeadStub,
    'streaming_aead': testing_api_pb2_grpc.StreamingAeadStub,
    'hybrid': testing_api_pb2_grpc.HybridStub,
    'mac': testing_api_pb2_grpc.MacStub,
    'signature': testing_api_pb2_grpc.SignatureStub,
    'prf': testing_api_pb2_grpc.PrfSetStub,
    'jwt': testing_api_pb2_grpc.JwtStub,
}

# All primitives.
_PRIMITIVES = list(_PRIMITIVE_STUBS.keys())

SUPPORTED_LANGUAGES_BY_PRIMITIVE = {
    'aead': ['cc', 'go', 'java', 'python'],
    'daead': ['cc', 'go', 'java', 'python'],
    'streaming_aead': ['cc', 'go', 'java', 'python'],
    'hybrid': ['cc', 'go', 'java', 'python'],
    'mac': ['cc', 'go', 'java', 'python'],
    'signature': ['cc', 'go', 'java', 'python'],
    'prf': ['cc', 'java', 'go', 'python'],
    'jwt': ['cc', 'java', 'go', 'python'],
}

# Needed in golang, because there key URIs are not optional.
GCP_KEY_URI_PREFIX = (
    'gcp-kms://projects/tink-test-infrastructure/locations/global/'
    'keyRings/unit-and-integration-testing/cryptoKeys/')
AWS_KEY_URI_PREFIX = 'aws-kms://arn:aws:kms:us-east-2:235739564943:'

GCP_CREDENTIALS_PATH = os.path.join(
    os.environ['TEST_SRCDIR'] if 'TEST_SRCDIR' in os.environ else '',
    'cross_language_test/testdata/gcp/credential.json')
AWS_CREDENTIALS_INI_PATH = os.path.join(
    os.environ['TEST_SRCDIR'] if 'TEST_SRCDIR' in os.environ else '',
    'cross_language_test/testdata/aws/credentials.ini')
AWS_CREDENTIALS_CRED_PATH = os.path.join(
    os.environ['TEST_SRCDIR'] if 'TEST_SRCDIR' in os.environ else '',
    'cross_language_test/testdata/aws/credentials.cred')

_RELATIVE_ROOT_PATH = 'tink_base/testing'


def _root_path() -> str:
  """Return the root path where server binaries are located.

  This root path can be set in the TINK_CROSS_LANG_ROOT_PATH enviroment
  variable. If TINK_CROSS_LANG_ROOT_PATH is not set, the root path is calculated
  from the TEST_SRCDIR enviroment variable.

  Returns:
    The root path of the cross language tests servers.
  Raises:
    ValueError if no variables are set.
    FileNotFoundError if a variable is set but the path is invalid.
  """

  def _check_path_exists_or_fail(path, env_variable):
    """Returns the path if it eixts, otherwise raises a FileNotFoundError."""
    if os.path.exists(path):
      return path
    raise FileNotFoundError(f'Variable {env_variable} is set but has an ' +
                            f'invalid path {path}')

  if 'TINK_CROSS_LANG_ROOT_PATH' in os.environ:
    return _check_path_exists_or_fail(os.environ['TINK_CROSS_LANG_ROOT_PATH'],
                                      'TINK_CROSS_LANG_ROOT_PATH')
  if 'TEST_SRCDIR' in os.environ:
    return _check_path_exists_or_fail(
        os.path.join(os.environ['TEST_SRCDIR'], _RELATIVE_ROOT_PATH),
        'TEST_SRCDIR')

  raise ValueError('No root path environment variable set')


def _server_path(lang: str) -> str:
  """Returns the path where the server binary is located."""
  root_dir = _root_path()
  for relative_server_path in _SERVER_PATHS[lang]:
    server_path = os.path.join(root_dir, relative_server_path)
    logging.info('try path: %s', server_path)
    if os.path.exists(server_path):
      return server_path
  raise RuntimeError('Executable for lang %s not found' % lang)


def _server_cmd(lang: str, port: int) -> List[str]:
  """Returns the server command."""
  if lang == 'java':
    # Java expects a .cred file. Others a .ini file.
    aws_credentials_path = AWS_CREDENTIALS_CRED_PATH
  else:
    aws_credentials_path = AWS_CREDENTIALS_INI_PATH

  server_path = _server_path(lang)
  # TODO(b/249015767): Refactor KMS integration to pass credentials via gRPC.
  server_args = [
      '--port',
      '%d' % port, '--gcp_credentials_path', GCP_CREDENTIALS_PATH,
      '--aws_credentials_path', aws_credentials_path
  ]
  if lang == 'go':
    # in all languages except go, the key URI parameters are optional.
    # in go, they are required, but can be a prefix.
    server_args.extend([
        '--gcp_key_uri', GCP_KEY_URI_PREFIX,
        '--aws_key_uri', AWS_KEY_URI_PREFIX])

  if lang == 'java' and server_path.endswith('.jar'):
    java_path = os.path.join(_root_path(), _JAVA_PATH)
    return [java_path, '-jar', server_path] + server_args
  else:
    return [server_path] + server_args


def _get_file_content(filename: str) -> str:
  with open(filename, 'r') as f:
    return f.read()


class _TestingServers():
  """TestingServers starts up testing gRPC servers and returns service stubs."""

  def __init__(self, test_name: str):
    self._server = {}
    self._output_file = {}
    self._channel = {}
    self._metadata_stub = {}
    self._keyset_stub = {}
    self._aead_stub = {}
    self._daead_stub = {}
    self._streaming_aead_stub = {}
    self._hybrid_stub = {}
    self._mac_stub = {}
    self._signature_stub = {}
    self._prf_stub = {}
    self._jwt_stub = {}
    self._test_name = test_name

    for lang in LANGUAGES:
      port = portpicker.pick_unused_port()
      cmd = _server_cmd(lang, port)
      logging.info('cmd = %s', cmd)
      output_path = self._get_output_path(lang)
      logging.info('writing server output to %s', output_path)
      try:
        self._output_file[lang] = open(output_path, 'w+')
      except IOError as e:
        logging.info('unable to open server output file %s', output_path)
        raise RuntimeError('Could not start %s server' % lang) from e
      self._server[lang] = subprocess.Popen(
          cmd, stdout=self._output_file[lang], stderr=subprocess.STDOUT)
      logging.info('%s server started on port %d with pid: %d. Log output: %s',
                   lang, port, self._server[lang].pid,
                   self._output_file[lang].name)
      self._channel[lang] = grpc.secure_channel(
          '[::]:%d' % port, grpc.local_channel_credentials())
    for lang in LANGUAGES:
      try:
        grpc.channel_ready_future(self._channel[lang]).result(timeout=30)
      except Exception as e:
        logging.info('Timeout while connecting to server %s', lang)
        self._server[lang].kill()
        _, _ = self._server[lang].communicate()
        raise RuntimeError(
            'Could not start %s server, output=%s' %
            (lang, _get_file_content(self._output_file[lang].name))) from e
      self._metadata_stub[lang] = testing_api_pb2_grpc.MetadataStub(
          self._channel[lang])
      self._keyset_stub[lang] = testing_api_pb2_grpc.KeysetStub(
          self._channel[lang])
    for primitive in _PRIMITIVES:
      for lang in SUPPORTED_LANGUAGES_BY_PRIMITIVE[primitive]:
        stub_name = '_%s_stub' % primitive
        getattr(self, stub_name)[lang] = _PRIMITIVE_STUBS[primitive](
            self._channel[lang])

  def _get_output_path(self, lang) -> str:
    try:
      output_dir = os.environ['TEST_UNDECLARED_OUTPUTS_DIR']
    except KeyError as e:
      raise RuntimeError(
          'Could not start %s server, TEST_UNDECLARED_OUTPUTS_DIR environment'
          'variable must be set') from e
    output_file = '%s-%s-%s' % (self._test_name, lang, 'server.log')
    return os.path.join(output_dir, output_file)

  def keyset_stub(self, lang) -> testing_api_pb2_grpc.KeysetStub:
    return self._keyset_stub[lang]

  def aead_stub(self, lang) -> testing_api_pb2_grpc.AeadStub:
    return self._aead_stub[lang]

  def daead_stub(self, lang) -> testing_api_pb2_grpc.DeterministicAeadStub:
    return self._daead_stub[lang]

  def streaming_aead_stub(self, lang) -> testing_api_pb2_grpc.StreamingAeadStub:
    return self._streaming_aead_stub[lang]

  def hybrid_stub(self, lang) -> testing_api_pb2_grpc.HybridStub:
    return self._hybrid_stub[lang]

  def mac_stub(self, lang) -> testing_api_pb2_grpc.MacStub:
    return self._mac_stub[lang]

  def signature_stub(self, lang) -> testing_api_pb2_grpc.SignatureStub:
    return self._signature_stub[lang]

  def prf_stub(self, lang) -> testing_api_pb2_grpc.PrfSetStub:
    return self._prf_stub[lang]

  def jwt_stub(self, lang) -> testing_api_pb2_grpc.JwtStub:
    return self._jwt_stub[lang]

  def metadata_stub(self, lang) -> testing_api_pb2_grpc.MetadataStub:
    return self._metadata_stub[lang]

  def stop(self):
    """Stops all servers."""
    logging.info('Stopping servers...')
    for lang in LANGUAGES:
      self._channel[lang].close()
    for lang in LANGUAGES:
      self._server[lang].terminate()
    time.sleep(2)
    for lang in LANGUAGES:
      if self._server[lang].poll() is None:
        logging.info('Killing server %s.', lang)
        self._server[lang].kill()
    for lang in LANGUAGES:
      self._output_file[lang].close()
    logging.info('All servers stopped.')

    print()
    print()
    for lang in LANGUAGES:
      total_reps = 1 + 100 // len(lang + ' ')
      length = total_reps * len(lang + ' ') - 1
      print('=' * length)
      print((lang + ' ') * total_reps)
      print('v' * length)
      with open(self._get_output_path(lang)) as f:
        print(f.read())
      print('^' * length)
      print((lang + ' ') * total_reps)
      print('=' * length)
      print()

_ts = None


def start(output_files_prefix: str) -> None:
  """Starts all servers."""
  global _ts
  _ts = _TestingServers(output_files_prefix)

  versions = {}
  for lang in LANGUAGES:
    response = _ts.metadata_stub(lang).GetServerInfo(
        testing_api_pb2.ServerInfoRequest())
    if lang != response.language:
      raise ValueError(
          'lang = %s != response.language = %s' % (lang, response.language))
    if response.tink_version:
      versions[lang] = response.tink_version
    else:
      logging.warning('server in lang %s has no tink version.', lang)
  unique_versions = list(set(versions.values()))
  logging.info('Tink version: %s', unique_versions[0])


def stop() -> None:
  """Stops all servers."""
  _ts.stop()


def key_template(lang: str, template_name: str) -> tink_pb2.KeyTemplate:
  """Returns the key template of template_name, implemented in lang."""
  return _primitives.key_template(_ts.keyset_stub(lang), template_name)


def new_keyset(lang: str, template: tink_pb2.KeyTemplate) -> bytes:
  """Returns a new KeysetHandle, implemented in lang."""
  return _primitives.new_keyset(_ts.keyset_stub(lang), template)


def public_keyset(lang: str, private_keyset: bytes) -> bytes:
  """Returns a public keyset handle, implemented in lang."""
  return _primitives.public_keyset(_ts.keyset_stub(lang), private_keyset)


def keyset_to_json(lang: str, keyset: bytes) -> str:
  return _primitives.keyset_to_json(_ts.keyset_stub(lang), keyset)


def keyset_from_json(lang: str, json_keyset: str) -> bytes:
  return _primitives.keyset_from_json(_ts.keyset_stub(lang), json_keyset)


def keyset_read_encrypted(lang: str, encrypted_keyset: bytes,
                          master_keyset: bytes,
                          associated_data: Optional[bytes],
                          keyset_reader_type: str) -> bytes:
  return _primitives.keyset_read_encrypted(
      _ts.keyset_stub(lang), encrypted_keyset, master_keyset, associated_data,
      keyset_reader_type)


def keyset_write_encrypted(lang: str, keyset: bytes, master_keyset: bytes,
                           associated_data: Optional[bytes],
                           keyset_writer_type: str) -> bytes:
  return _primitives.keyset_write_encrypted(
      _ts.keyset_stub(lang), keyset, master_keyset, associated_data,
      keyset_writer_type)


def jwk_set_to_keyset(lang: str, jwk_set: str) -> bytes:
  return _primitives.jwk_set_to_keyset(_ts.jwt_stub(lang), jwk_set)


def jwk_set_from_keyset(lang: str, keyset: bytes) -> str:
  return _primitives.jwk_set_from_keyset(_ts.jwt_stub(lang), keyset)


def remote_primitive(lang: str, keyset: bytes, primitive_class: Type[P]) -> P:
  """Creates a primitive from a keyset backed by the given language.

  Internally, this does an RPC to the server specified by 'lang' in order to
  try to 'Create' the primitive. If the RPC returns with an error, a TinkError
  is returned. Otherwise, an instance of the primitive is returned which
  forwards calls to the service implemented in the language.

  Args:
    lang: specification of the language to use
    keyset: the serialized keyset
    primitive_class: the type of the primitive

  Returns:
    A primitive to be used.

  Raises:
    TinkError if creation fails.
  """

  if primitive_class == tink.aead.Aead:
    return _primitives.Aead(lang, _ts.aead_stub(lang), keyset, None)
  if primitive_class == tink.daead.DeterministicAead:
    return _primitives.DeterministicAead(lang, _ts.daead_stub(lang), keyset,
                                         None)
  if primitive_class == tink.streaming_aead.StreamingAead:
    return _primitives.StreamingAead(lang, _ts.streaming_aead_stub(lang),
                                     keyset)
  if primitive_class == tink.hybrid.HybridDecrypt:
    return _primitives.HybridDecrypt(lang, _ts.hybrid_stub(lang), keyset, None)
  if primitive_class == tink.hybrid.HybridEncrypt:
    return _primitives.HybridEncrypt(lang, _ts.hybrid_stub(lang), keyset, None)
  if primitive_class == tink.mac.Mac:
    return _primitives.Mac(lang, _ts.mac_stub(lang), keyset, None)
  if primitive_class == tink.signature.PublicKeySign:
    return _primitives.PublicKeySign(lang, _ts.signature_stub(lang), keyset,
                                     None)
  if primitive_class == tink.signature.PublicKeyVerify:
    return _primitives.PublicKeyVerify(lang, _ts.signature_stub(lang), keyset,
                                       None)
  if primitive_class == tink.prf.PrfSet:
    return _primitives.PrfSet(lang, _ts.prf_stub(lang), keyset, None)
  if primitive_class == tink.jwt.JwtMac:
    return _primitives.JwtMac(lang, _ts.jwt_stub(lang), keyset)
  if primitive_class == tink.jwt.JwtPublicKeySign:
    return _primitives.JwtPublicKeySign(lang, _ts.jwt_stub(lang), keyset)
  if primitive_class == tink.jwt.JwtPublicKeyVerify:
    return _primitives.JwtPublicKeyVerify(lang, _ts.jwt_stub(lang), keyset)
  raise ValueError('Unsupported P in remote_primitive: ' + str(primitive_class))
