# CHANGELOG

<!-- version list -->

## v0.10.0 (2026-04-26)

### Features

- **summary**: Add retained receiver summary topic
  ([`126d924`](https://github.com/tvallas/mtr2mqtt/commit/126d924edb5787f117a9904d888bccafc5746b5c))


## v0.9.0 (2026-04-26)

### Bug Fixes

- **table**: Show only textual availability status
  ([`0493a7f`](https://github.com/tvallas/mtr2mqtt/commit/0493a7f683568f1d8b40a7d98c2685f50e6bac92))

### Features

- **status**: Publish retained availability state
  ([`8226c62`](https://github.com/tvallas/mtr2mqtt/commit/8226c62f8588f94811e1f29d0d5615039137d1dc))


## v0.8.2 (2026-04-26)

### Bug Fixes

- **deps**: Update GitPython for security advisories
  ([`3e0ba4f`](https://github.com/tvallas/mtr2mqtt/commit/3e0ba4fa505c60a0161f9b22b4b3fd34434c6b81))

### Chores

- **deps**: Bump docker/build-push-action from 6 to 7
  ([`517a8c2`](https://github.com/tvallas/mtr2mqtt/commit/517a8c2eecb2c65695cfce0e1aefc4d591b0f0ff))

- **deps**: Bump docker/login-action from 3 to 4
  ([`0c4f296`](https://github.com/tvallas/mtr2mqtt/commit/0c4f296436b27040eff064db3ff9f7f4d92a1d9b))


## v0.8.1 (2026-04-18)

### Bug Fixes

- **docker**: Reduce runtime image size
  ([`9636c76`](https://github.com/tvallas/mtr2mqtt/commit/9636c76e4029c3478e1e6747ae5781b81252ba08))


## v0.8.0 (2026-04-18)

### Features

- **output**: Add live sensor table view
  ([`406367c`](https://github.com/tvallas/mtr2mqtt/commit/406367c92821bce8892110d0f76e0570737ca777))

- **output**: Add structured JSON logging
  ([`26320de`](https://github.com/tvallas/mtr2mqtt/commit/26320decf7cdd5e470d94d6811fc7a8f3af24b4e))


## v0.7.4 (2026-04-18)

### Bug Fixes

- **ci**: Repair lint target and narrow exception handling
  ([`20e56e6`](https://github.com/tvallas/mtr2mqtt/commit/20e56e69b92f7c1ebd76aeab1888900d450a25ab))

- **cli**: Validate startup configuration inputs
  ([`ad54e70`](https://github.com/tvallas/mtr2mqtt/commit/ad54e70c6dfaa274503760751ff1bf09128289a5))

- **runtime**: Harden receiver and mqtt failure handling
  ([`d9f57f2`](https://github.com/tvallas/mtr2mqtt/commit/d9f57f2346b99b7727250a0d6415d88b2993d6c4))


## v0.7.3 (2026-04-18)

### Bug Fixes

- **cli**: Handle runtime startup errors
  ([`18bca65`](https://github.com/tvallas/mtr2mqtt/commit/18bca657ca2ca617f6a834248e7dc410080ea870))

- **runtime**: Isolate bridge lifecycle
  ([`c9b07f1`](https://github.com/tvallas/mtr2mqtt/commit/c9b07f16702830c50c30b7142c870b3d315406db))


## v0.7.2 (2026-04-18)

### Bug Fixes

- **metadata**: Handle unexpected YAML shapes
  ([`a68313d`](https://github.com/tvallas/mtr2mqtt/commit/a68313deb5c7629d890688a734ab5fa4f3f865aa))

### Documentation

- **agents**: Add repository workflow guidance
  ([`03b2806`](https://github.com/tvallas/mtr2mqtt/commit/03b2806e2f6e26da973ddb358cbd6d7e645d8d90))


## v0.7.1 (2026-04-18)

### Bug Fixes

- **cli**: Recover from serial device disconnects
  ([`dcf1527`](https://github.com/tvallas/mtr2mqtt/commit/dcf15275fddd9b757bfae3db0f655def18496246))


## v0.7.0 (2026-04-18)

### Documentation

- Document Home Assistant MQTT discovery configuration
  ([`68d503d`](https://github.com/tvallas/mtr2mqtt/commit/68d503d530ea9b6b9babfd233085ba9a972778f9))

### Features

- Add Home Assistant MQTT discovery support
  ([`0dfad71`](https://github.com/tvallas/mtr2mqtt/commit/0dfad71b87053dc45db5aaf550e70ed320c11a97))

### Testing

- Cover Home Assistant MQTT discovery behavior
  ([`21d9841`](https://github.com/tvallas/mtr2mqtt/commit/21d9841deecdedbba6e1f26dcfddd686690ff28a))


## v0.6.10 (2026-04-18)

### Bug Fixes

- **mqtt**: Use callback API v2
  ([`9a6c040`](https://github.com/tvallas/mtr2mqtt/commit/9a6c040c74543f2133cc749c362a6782c2af483a))


## v0.6.9 (2026-04-17)

### Bug Fixes

- **deps**: Bump python in the docker-minor-patch group
  ([`2304af4`](https://github.com/tvallas/mtr2mqtt/commit/2304af48cebd6dbb99938052e6f46086e4e1da7b))

### Chores

- **ci**: Expand Python version coverage in CI
  ([`6c070f6`](https://github.com/tvallas/mtr2mqtt/commit/6c070f6e9d5c2ea0b3c01a18fbe57a3f3e47ff67))

- **deps**: Add Dependabot configuration
  ([`0b635be`](https://github.com/tvallas/mtr2mqtt/commit/0b635beec7dcc06fd86af3db2ac5c999835ba470))

- **deps**: Bump actions/checkout from 4 to 6
  ([`e95503e`](https://github.com/tvallas/mtr2mqtt/commit/e95503ea9e3f54a3d4f4e2d32e5f48c73aa3833e))

- **deps**: Bump actions/setup-python from 5 to 6
  ([`e1bfd28`](https://github.com/tvallas/mtr2mqtt/commit/e1bfd288afe9e7ccc727503bef617c95dcec1356))

- **deps**: Bump docker/setup-buildx-action from 3 to 4
  ([`9deda2b`](https://github.com/tvallas/mtr2mqtt/commit/9deda2b72953dda56273764ab75847efd594f22a))


## v0.6.8 (2026-04-17)

### Bug Fixes

- Add OCI metadata and attestations to docker publish workflow
  ([`02d681d`](https://github.com/tvallas/mtr2mqtt/commit/02d681db8046b184f17ee745a1951d865e8070ac))

- Allow docker publish attestations from semantic release
  ([`9529bc9`](https://github.com/tvallas/mtr2mqtt/commit/9529bc9980a9cf117a7dc6d5134fa4c2560dc3b9))

- Fix accidental typo in the runner tag
  ([`1ac0fb6`](https://github.com/tvallas/mtr2mqtt/commit/1ac0fb6ae88a37d0140cf90a3309f95e20434e64))

- Fix semanteic release job permissions
  ([`0e9a47f`](https://github.com/tvallas/mtr2mqtt/commit/0e9a47f9421087b13754981b67d8101a50f98673))

### Continuous Integration

- Add OCI metadata and attestations to Docker publish workflow
  ([`184fd75`](https://github.com/tvallas/mtr2mqtt/commit/184fd7517711fd981015c4e2ec59c3cb86a21378))

- Modernize Trivy security scanning workflow
  ([`ac8e0e0`](https://github.com/tvallas/mtr2mqtt/commit/ac8e0e0ffcdfe85c7e573ed6a595b68a6f5c68ee))


## v0.6.7 (2026-04-16)

### Bug Fixes

- **changelog**: Move semantic-release marker above legacy entries
  ([`e4f40d8`](https://github.com/tvallas/mtr2mqtt/commit/e4f40d8783206e57602a96e9e97ed2412a584d5d))


## Legacy changelog

## v0.6.4 (2026-04-16)

### Bug Fixes

* ci: remove duplicate GitHub release creation ([`be3eb63`](https://github.com/tvallas/mtr2mqtt/commit/be3eb63))

## v0.6.3 (2026-04-16)

### Bug Fixes

* ci: switch PyPI publish to trusted publishing ([`cc09c43`](https://github.com/tvallas/mtr2mqtt/commit/cc09c43))

### Build System

* build: migrate packaging to pyproject.toml and uv ([`a1c3e3d`](https://github.com/tvallas/mtr2mqtt/commit/a1c3e3d))

### Continuous Integration

* ci: migrate CI workflow from pipenv to uv ([`47be79e`](https://github.com/tvallas/mtr2mqtt/commit/47be79e))

## v0.6.2 (2026-04-16)

### Fix

* fix(ci): tag docker image from semantic-release output by @tvallas in #64

## v0.6.1 (2026-04-16)

### Chore

* chore(ci): move pylint into CI and remove legacy lint workflow by @tvallas in #60
* chore(ci): simplify Docker workflow to PR smoke build by @tvallas in #61

### Test

* test: expand unit coverage for parser and helpers by @tvallas in #62

### Fix

* fix: update pipenv dependencies and replace deprecated security check by @tvallas in #63

## v0.6.0 (2026-04-16)

### Chore

* chore(ci): add concurrency guard to release workflow by @tvallas in #58

### Feature

* feat(ci): add Docker publish workflow triggered by release by @tvallas in #59

## v0.5.1 (2023-12-19)

### Fix

* fix: update packages with vulnerabilities (#34)
* fix: update packages with vulnerabilities
* ci: remove exact python version from lint and test on push job as referred version is unavailable
* ci: make trivy scan workflow use python 3.8
* ci: explicitly set the python-semantic-release version to 7.x as the 8 version has breaking changes. The version 8 seems to have missing option to print current version using command `print-version`
* fix: update vulnerable package in docker image ([`d2be986`](https://github.com/tvallas/mtr2mqtt/commit/d2be9863485535d1c9ce2e493b1a00cc62bfe877))

## v0.5.0 (2021-09-25)

### Ci

* ci: update python version used in ci tasks ([`3c10e25`](https://github.com/tvallas/mtr2mqtt/commit/3c10e25cc1d40d1137a3787fcbe4820e6fe2f6ca))

### Feature

* feat: add support to DPR990 and DPR991 receivers ([`acbbc51`](https://github.com/tvallas/mtr2mqtt/commit/acbbc516ce5b16321a3c2cd89eb253047a6bf30a))

### Fix

* fix: define encoding when opening metadata file ([`52f6812`](https://github.com/tvallas/mtr2mqtt/commit/52f6812))

### Unknown

* Merge pull request #33 from tvallas/add_DPR991_support
* feat: add support to DPR990 and DPR991 receivers ([`7c6a99b`](https://github.com/tvallas/mtr2mqtt/commit/7c6a99b))

## v0.4.1 (2021-04-15)

### Chore

* chore: change docker-compose.yml file to use mosquitto-no-auth.conf
* change mtr2mqtt to use quiet mode ([`f7e7668`](https://github.com/tvallas/mtr2mqtt/commit/f7e7668))

### Ci

* ci: update python version in ci workflow ([`aefaf82`](https://github.com/tvallas/mtr2mqtt/commit/aefaf82))
* ci: wait until the package is available in pypi before docker build ([`bdd0033`](https://github.com/tvallas/mtr2mqtt/commit/bdd0033))
* ci: add manual workflow dispatch event as trigger to semantic release workflow ([`ff9792a`](https://github.com/tvallas/mtr2mqtt/commit/ff9792a))

### Fix

* fix: implement better mqtt connection handling, logging and reconnection logic
* fix #2 ([`747fe05`](https://github.com/tvallas/mtr2mqtt/commit/747fe05))

### Unknown

* Merge pull request #32 from tvallas/fix/mqtt-reconnecet-when-disconnected
* Fix/mqtt reconnecet when disconnected ([`0c6cbcf`](https://github.com/tvallas/mtr2mqtt/commit/0c6cbcf))
* Merge pull request #31 from tvallas/ci/add-verify-task-to-pypi-release
* ci: wait until the package is available in pypi before docker build ([`0b43b62`](https://github.com/tvallas/mtr2mqtt/commit/0b43b62))
* Merge pull request #30 from tvallas/ci/add-manual-workflow-run-option
* ci: add manual workflow dispatch event as trigger to semantic release workflow ([`321920b`](https://github.com/tvallas/mtr2mqtt/commit/321920b))

## v0.4.0 (2021-04-09)

### Ci

* ci: fix workflow syntax ([`b7cd3c1`](https://github.com/tvallas/mtr2mqtt/commit/b7cd3c1))
* ci: define tags directly instead of using docker meta step ([`d72523a`](https://github.com/tvallas/mtr2mqtt/commit/d72523a))

### Feature

* feat(cli): add support for checking the software version ([`dc94b1c`](https://github.com/tvallas/mtr2mqtt/commit/dc94b1c))

### Unknown

* Merge pull request #29 from tvallas/feat/add-version-argument-support
* feat(cli): add support for checking the software version ([`ef55b01`](https://github.com/tvallas/mtr2mqtt/commit/ef55b01))
* Ci/add trivy scanning (#28)
* ci: add trivy scanning to docker image ([`663770f`](https://github.com/tvallas/mtr2mqtt/commit/663770f))
* Merge pull request #27 from tvallas/ci/docker-buld-tag-fix
* ci: fix workflow syntax ([`34ee435`](https://github.com/tvallas/mtr2mqtt/commit/34ee435))
* Merge pull request #26 from tvallas/ci/docker-buld-tag-fix
* ci: define tags directly instead of using docker meta step ([`5add477`](https://github.com/tvallas/mtr2mqtt/commit/5add477))

## v0.3.2 (2021-04-02)

### Ci

* ci: test ci ([`4b50fa1`](https://github.com/tvallas/mtr2mqtt/commit/4b50fa1))

### Fix

* fix: change metadata file ([`2e976f9`](https://github.com/tvallas/mtr2mqtt/commit/2e976f9))

### Unknown

* Merge pull request #25 from tvallas/fix/metadata_file_structure
* Fix/metadata file structure ([`814e46d`](https://github.com/tvallas/mtr2mqtt/commit/814e46d))

## v0.3.1 (2021-04-02)

### Ci

* ci: move docker build to sematic release workflow ([`cdf1357`](https://github.com/tvallas/mtr2mqtt/commit/cdf1357))

### Fix

* fix: fix syntax in docker-compose file ([`e6204f5`](https://github.com/tvallas/mtr2mqtt/commit/e6204f5))

### Unknown

* Merge pull request #24 from tvallas/fix/docker-compose-fixes
* fix: fix syntax in docker-compose file ([`0656ad5`](https://github.com/tvallas/mtr2mqtt/commit/0656ad5))
* Merge pull request #23 from tvallas/ci/combine-workflow-files
* ci: move docker build to sematic release workflow ([`6514cba`](https://github.com/tvallas/mtr2mqtt/commit/6514cba))

## v0.3.0 (2021-04-02)

### Feature

* feat: add docker-compose file and a sample metadata file ([`39d6ba7`](https://github.com/tvallas/mtr2mqtt/commit/39d6ba7))

### Unknown

* Merge pull request #22 from tvallas/feat/docker-compose-template
* feat: add docker-compose file and a sample metadata file ([`4f2af38`](https://github.com/tvallas/mtr2mqtt/commit/4f2af38))

## v0.2.1 (2021-04-02)

### Ci

* ci: change docker build trigger event ([`5346b26`](https://github.com/tvallas/mtr2mqtt/commit/5346b26))

### Fix

* fix: update dependecies for CVE-2020-29651 ([`926c24f`](https://github.com/tvallas/mtr2mqtt/commit/926c24f))

### Unknown

* Merge pull request #21 from tvallas/fix/py-update-CVE-2020-29651
* fix: update dependecies for CVE-2020-29651 ([`334b46b`](https://github.com/tvallas/mtr2mqtt/commit/334b46b))
* Merge pull request #20 from tvallas/ci/change-docker-build-trigger
* ci: change docker build trigger event ([`17daf7b`](https://github.com/tvallas/mtr2mqtt/commit/17daf7b))
* Chore/add docker support (#19)
* ci: add docker image build and push to dockerhub ([`1096b00`](https://github.com/tvallas/mtr2mqtt/commit/1096b00))

## v0.2.0 (2021-03-31)

### Feature

* feat(cli): add option to configure application using environment variables instead of cli arguments ([`5d6f94c`](https://github.com/tvallas/mtr2mqtt/commit/5d6f94c))

### Unknown

* Merge pull request #18 from tvallas/feat/add-support-for-environment-variables
* feat(cli): add option to configure application using environment variables instead of cli arguments ([`b4403ed`](https://github.com/tvallas/mtr2mqtt/commit/b4403ed))

## v0.1.2 (2021-03-28)

### Fix

* fix: add missing dependency to PyYAML ([`c6ea963`](https://github.com/tvallas/mtr2mqtt/commit/c6ea963))

### Unknown

* Merge pull request #17 from tvallas/fix/add-missing-dependencies
* fix: add missing dependency to PyYAML ([`f513666`](https://github.com/tvallas/mtr2mqtt/commit/f513666))

## v0.1.1 (2021-03-28)

### Ci

* ci: change version in setup.py file to use variable ([`2884704`](https://github.com/tvallas/mtr2mqtt/commit/2884704))

### Fix

* fix: test semantic versioning ([`ad0814b`](https://github.com/tvallas/mtr2mqtt/commit/ad0814b))

### Unknown

* Merge pull request #16 from tvallas/fix/semantic-release-test
* fix: test semantic versioning ([`90b53c7`](https://github.com/tvallas/mtr2mqtt/commit/90b53c7))
* Merge pull request #15 from tvallas/ci/semantic-release-settings
* ci: change version in setup.py file to use variable ([`d8153fb`](https://github.com/tvallas/mtr2mqtt/commit/d8153fb))

## v0.1.0 (2021-03-28)

### Chore

* chore: update Pipfile.lock ([`986ff61`](https://github.com/tvallas/mtr2mqtt/commit/986ff61))
* chore: update pyYML version requirement for security vulnerability reasons ([`a7271be`](https://github.com/tvallas/mtr2mqtt/commit/a7271be))

### Ci

* ci: change tests and lint to use pipenv ([`1e13dc2`](https://github.com/tvallas/mtr2mqtt/commit/1e13dc2))
* ci: fix pylint test ([`39d7b9a`](https://github.com/tvallas/mtr2mqtt/commit/39d7b9a))
* ci: fix pylint dependencies ([`4f34513`](https://github.com/tvallas/mtr2mqtt/commit/4f34513))
* ci(pylint): fix dependencies installation for pylint step ([`cfed3e7`](https://github.com/tvallas/mtr2mqtt/commit/cfed3e7))
* ci(ci): test ci by doing style fixes ([`7ac9d7e`](https://github.com/tvallas/mtr2mqtt/commit/7ac9d7e))
* ci: fix imports ([`62efeda`](https://github.com/tvallas/mtr2mqtt/commit/62efeda))
* ci(gitlab actions): test gitlab actions. Also some style changes and reorganising directory structure etc. ([`66a63ac`](https://github.com/tvallas/mtr2mqtt/commit/66a63ac))
* ci(ci): test GitHub actions ([`85cfec4`](https://github.com/tvallas/mtr2mqtt/commit/85cfec4))
* ci(ci): testing github actions ([`217d5fd`](https://github.com/tvallas/mtr2mqtt/commit/217d5fd))

### Documentation

* docs: fix syntax in readme ([`0415bd5`](https://github.com/tvallas/mtr2mqtt/commit/0415bd5))

### Feature

* feat: add debug logging of unsupported packages ([`f7ae1e3`](https://github.com/tvallas/mtr2mqtt/commit/f7ae1e3))
* feat(mtr): add UTC timestamp field to reading output json ([`78fc3ff`](https://github.com/tvallas/mtr2mqtt/commit/78fc3ff))
* feat(calibration support): add simple support for Utility packets having calibration date ([`950b731`](https://github.com/tvallas/mtr2mqtt/commit/950b731))
* feat(mtr2mqtt): initial commit ([`12dd367`](https://github.com/tvallas/mtr2mqtt/commit/12dd367))

### Fix

* fix: ignore responses with checksum error ([`a6dd3c1`](https://github.com/tvallas/mtr2mqtt/commit/a6dd3c1))
* fix: fix utility packet return value to valid response instead of None if device wasn't calibrated ([`f5c7c09`](https://github.com/tvallas/mtr2mqtt/commit/f5c7c09))
* fix(gitignore): fix typo in sample metadata file name ([`1b3125f`](https://github.com/tvallas/mtr2mqtt/commit/1b3125f))
* fix(metadata): fix transmitter id comparison ([`4958340`](https://github.com/tvallas/mtr2mqtt/commit/4958340))

### Performance

* perf: cut the execution tree and at the first supported device ([`077b551`](https://github.com/tvallas/mtr2mqtt/commit/077b551))

### Refactor

* refactor(metadata): change loadfile function to return value as string ([`cc5a47d`](https://github.com/tvallas/mtr2mqtt/commit/cc5a47d))
* refactor: change args to named parameters ([`7fe014c`](https://github.com/tvallas/mtr2mqtt/commit/7fe014c))
* refactor: fix PEP8 style issues ([`989a491`](https://github.com/tvallas/mtr2mqtt/commit/989a491))
* refactor: pEP8 style fixes ([`1fe1fbb`](https://github.com/tvallas/mtr2mqtt/commit/1fe1fbb))
* refactor(cli): fix simple pep8 style issues ([`b0c49c9`](https://github.com/tvallas/mtr2mqtt/commit/b0c49c9))
* refactor(tests_mtr): fix pep8 style issues ([`9fb2c7d`](https://github.com/tvallas/mtr2mqtt/commit/9fb2c7d))
* refactor(scl): fix pep8 style issues ([`3d474d8`](https://github.com/tvallas/mtr2mqtt/commit/3d474d8))
* refactor(mtr): fix pep8 style issues and add payload size check warning ([`93f15ca`](https://github.com/tvallas/mtr2mqtt/commit/93f15ca))
* refactor(metadata): fix pep8 style issues ([`a33f0b3`](https://github.com/tvallas/mtr2mqtt/commit/a33f0b3))

### Test

* test(metadata): add unit tests for metadata module ([`eac3675`](https://github.com/tvallas/mtr2mqtt/commit/eac3675))

### Unknown

* Merge pull request #14 from tvallas/ci/fix-pipenv-for-unit-tests
* ci: change tests and lint to use pipenv ([`a847c0e`](https://github.com/tvallas/mtr2mqtt/commit/a847c0e))
* Feat/add semantic versioning (#13)
* feat: add python-semantic-release package and change setup.py to use variable for versioning
* ci: add test version of semantic release workflow ([`057554d`](https://github.com/tvallas/mtr2mqtt/commit/057554d))
* Merge pull request #12 from tvallas/chore/pipfile-lock-update
* chore: update Pipfile.lock ([`35fd3dc`](https://github.com/tvallas/mtr2mqtt/commit/35fd3dc))
* Merge pull request #11 from tvallas/fix/ignore-packets-with-wrong-checksum
* Fix/ignore packets with wrong checksum ([`59f4b39`](https://github.com/tvallas/mtr2mqtt/commit/59f4b39))
* Merge pull request #10 from tvallas/fix/metadata-handling-for-utility-packets
* fix: fix utility packet return value to valid response instead of None if device wasn't calibrated ([`0321243`](https://github.com/tvallas/mtr2mqtt/commit/0321243))
* Merge pull request #9 from tvallas/test/add-meta-data-tests
* fix(gitignore): fix typo in sample metadata file name ([`911b47a`](https://github.com/tvallas/mtr2mqtt/commit/911b47a))
* Merge pull request #8 from tvallas/test/add-meta-data-tests
* Test/add meta data tests ([`53c70a9`](https://github.com/tvallas/mtr2mqtt/commit/53c70a9))
* Merge pull request #7 from tvallas/fix/mtr_parsing_improvements
* Fix/mtr parsing improvements ([`ee776c7`](https://github.com/tvallas/mtr2mqtt/commit/ee776c7))
* Merge pull request #6 from tvallas/fix/readme-fixes
* docs: fix syntax in readme ([`2117771`](https://github.com/tvallas/mtr2mqtt/commit/2117771))
* Merge pull request #5 from tvallas/fix/pep8-style-issues
* Fix/pep8 style issues ([`3777f06`](https://github.com/tvallas/mtr2mqtt/commit/3777f06))
* Merge pull request #4 from tvallas/feature/simple-ci-setup
* Feature/simple ci setup ([`381e54e`](https://github.com/tvallas/mtr2mqtt/commit/381e54e))
* Merge pull request #3 from tvallas/feature/add-timestamp-to-mqtt-output
* feat(mtr): add UTC timestamp field to reading output json ([`f61b1b2`](https://github.com/tvallas/mtr2mqtt/commit/f61b1b2))
* Merge pull request #1 from tvallas/feature/utility-packet-support
* feat(calibration support): add simple support for Utility packets having calibration date ([`67a86ad`](https://github.com/tvallas/mtr2mqtt/commit/67a86ad))
