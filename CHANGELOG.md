# CHANGELOG



## v0.5.1 (2023-12-19)

### Fix

* fix: update packages with vulnerabilities (#34)

* fix: update packages with vulnerabilities

* ci: remove exact python version from lint and test on push job as referred version is unavailable

* ci: make trivy scan workflow use python 3.8

* ci: explicitly set the python-semantic-release version to 7.x as the 8 version has breaking changes

The version 8 seems to have missing option to print current version using command `print-version`

* fix: update vulnerable package in docker image ([`d2be986`](https://github.com/tvallas/mtr2mqtt/commit/d2be9863485535d1c9ce2e493b1a00cc62bfe877))


## v0.5.0 (2021-09-25)

### Ci

* ci: update python version used in ci tasks ([`3c10e25`](https://github.com/tvallas/mtr2mqtt/commit/3c10e25cc1d40d1137a3787fcbe4820e6fe2f6ca))

### Feature

* feat: add support to DPR990 and DPR991 receivers ([`acbbc51`](https://github.com/tvallas/mtr2mqtt/commit/acbbc516ce5b16321a3c2cd89eb253047a6bf30a))

### Fix

* fix: define encoding when opening metadata file ([`52f6812`](https://github.com/tvallas/mtr2mqtt/commit/52f6812d9af520db932bcdae9d5574a621eb7e19))

### Unknown

* Merge pull request #33 from tvallas/add_DPR991_support

feat: add support to DPR990 and DPR991 receivers ([`7c6a99b`](https://github.com/tvallas/mtr2mqtt/commit/7c6a99b74a007c9527c55496ca8a921451d3c797))


## v0.4.1 (2021-04-15)

### Chore

* chore: change docker-compose.yml file to use mosquitto-no-auth.conf

change mtr2mqtt to use quiet mode ([`f7e7668`](https://github.com/tvallas/mtr2mqtt/commit/f7e76688d3a59606bf00cdab3477e7ed8abc4c72))

### Ci

* ci: update python version in ci workflow ([`aefaf82`](https://github.com/tvallas/mtr2mqtt/commit/aefaf82ebe1c7ffaf53d4775099d2a8fa64a98b0))

* ci: wait until the package is available in pypi before docker build ([`bdd0033`](https://github.com/tvallas/mtr2mqtt/commit/bdd0033cbb530a32f4c164897cb79d66cc21cfc6))

* ci: add manual workflow dispatch event as trigger to semantic release workflow ([`ff9792a`](https://github.com/tvallas/mtr2mqtt/commit/ff9792a615f9a3b104c2652e9597897760448af7))

### Fix

* fix: implement better mqtt connection handling, logging and reconnection logic

fix #2 ([`747fe05`](https://github.com/tvallas/mtr2mqtt/commit/747fe058027ede1b016bb0c9717a2d040b05caa1))

### Unknown

* Merge pull request #32 from tvallas/fix/mqtt-reconnecet-when-disconnected

Fix/mqtt reconnecet when disconnected ([`0c6cbcf`](https://github.com/tvallas/mtr2mqtt/commit/0c6cbcf4acfb5e913ec7c8d04c2e5572e835cbb4))

* Merge pull request #31 from tvallas/ci/add-verify-task-to-pypi-release

ci: wait until the package is available in pypi before docker build ([`0b43b62`](https://github.com/tvallas/mtr2mqtt/commit/0b43b62c651eb6e9ac53456ed799718ac64a338f))

* Merge pull request #30 from tvallas/ci/add-manual-workflow-run-option

ci: add manual workflow dispatch event as trigger to semantic release… ([`321920b`](https://github.com/tvallas/mtr2mqtt/commit/321920b941ea303a722952f6003820f372790e5a))


## v0.4.0 (2021-04-09)

### Ci

* ci: fix workflow syntax ([`b7cd3c1`](https://github.com/tvallas/mtr2mqtt/commit/b7cd3c1fa272dbd0ecb48a0589b9dbfe5649733b))

* ci: define tags directly instead of using docker meta step ([`d72523a`](https://github.com/tvallas/mtr2mqtt/commit/d72523a9265699dec188c23b406b2d15fb6f460a))

### Feature

* feat(cli): add support for checking the software version ([`dc94b1c`](https://github.com/tvallas/mtr2mqtt/commit/dc94b1c6dfb8ddadd6f52cbfd1794eae725ede00))

### Unknown

* Merge pull request #29 from tvallas/feat/add-version-argument-support

feat(cli): add support for checking the software version ([`ef55b01`](https://github.com/tvallas/mtr2mqtt/commit/ef55b0130a4fed2e466de6d64583301dec6ae6e9))

* Ci/add trivy scanning (#28)

* ci: add trivy scanning to docker image ([`663770f`](https://github.com/tvallas/mtr2mqtt/commit/663770f938bcd97c0c60dc733dfd5dc42f9ec081))

* Merge pull request #27 from tvallas/ci/docker-buld-tag-fix

ci: fix workflow syntax ([`34ee435`](https://github.com/tvallas/mtr2mqtt/commit/34ee435e330e3c2b551d972c76f660f447955329))

* Merge pull request #26 from tvallas/ci/docker-buld-tag-fix

ci: define tags directly instead of using docker meta step ([`5add477`](https://github.com/tvallas/mtr2mqtt/commit/5add4774d527c6d746036021203bcf0815867a07))


## v0.3.2 (2021-04-02)

### Ci

* ci: test ci ([`4b50fa1`](https://github.com/tvallas/mtr2mqtt/commit/4b50fa146d50a71cd9487b1beeeecc957eabe9f2))

### Fix

* fix: change metadata file ([`2e976f9`](https://github.com/tvallas/mtr2mqtt/commit/2e976f9e5eb1f1da84bb9c9c3c96229b47eab5a7))

### Unknown

* Merge pull request #25 from tvallas/fix/metadata_file_structure

Fix/metadata file structure ([`814e46d`](https://github.com/tvallas/mtr2mqtt/commit/814e46d69c10c2fd68428a22ee57e4b4afd05910))


## v0.3.1 (2021-04-02)

### Ci

* ci: move docker build to sematic release workflow ([`cdf1357`](https://github.com/tvallas/mtr2mqtt/commit/cdf1357c46a88850b023963e062ac87ffd5d3824))

### Fix

* fix: fix syntax in docker-compose file ([`e6204f5`](https://github.com/tvallas/mtr2mqtt/commit/e6204f5835fa04f8d5f0baae871a5be6ff23670b))

### Unknown

* Merge pull request #24 from tvallas/fix/docker-compose-fixes

fix: fix syntax in docker-compose file ([`0656ad5`](https://github.com/tvallas/mtr2mqtt/commit/0656ad536a342295744cf900a91ce39d1554aa1a))

* Merge pull request #23 from tvallas/ci/combine-workflow-files

ci: move docker build to sematic release workflow ([`6514cba`](https://github.com/tvallas/mtr2mqtt/commit/6514cba328850416970b226cfd46ae20fdae28de))


## v0.3.0 (2021-04-02)

### Feature

* feat: add docker-compose file and a sample metadata file ([`39d6ba7`](https://github.com/tvallas/mtr2mqtt/commit/39d6ba7c373ccf9b57f9577b76a3142ec20d70cd))

### Unknown

* Merge pull request #22 from tvallas/feat/docker-compose-template

feat: add docker-compose file and a sample metadata file ([`4f2af38`](https://github.com/tvallas/mtr2mqtt/commit/4f2af38a28981965f81193190ae60f803c31d04f))


## v0.2.1 (2021-04-02)

### Ci

* ci: change docker build trigger event ([`5346b26`](https://github.com/tvallas/mtr2mqtt/commit/5346b262fb7efd331965d0c603088f3694f1b46d))

### Fix

* fix: update dependecies for CVE-2020-29651 ([`926c24f`](https://github.com/tvallas/mtr2mqtt/commit/926c24f97ac60e96588c92c764ebd90d6159328a))

### Unknown

* Merge pull request #21 from tvallas/fix/py-update-CVE-2020-29651

fix: update dependecies for CVE-2020-29651 ([`334b46b`](https://github.com/tvallas/mtr2mqtt/commit/334b46b552b5a6693ef06a543320a17aceae603c))

* Merge pull request #20 from tvallas/ci/change-docker-build-trigger

ci: change docker build trigger event ([`17daf7b`](https://github.com/tvallas/mtr2mqtt/commit/17daf7b6789169ce11a22f90d0108930133c8ca6))

* Chore/add docker support (#19)


* ci: add docker image build and push to dockerhub ([`1096b00`](https://github.com/tvallas/mtr2mqtt/commit/1096b00e6f82da656a009b21e22af0ca4a830f6b))


## v0.2.0 (2021-03-31)

### Feature

* feat(cli): add option to configure application using environment variables instead of cli arguments ([`5d6f94c`](https://github.com/tvallas/mtr2mqtt/commit/5d6f94cd9220415b2eb6903bbf89efaef0f21724))

### Unknown

* Merge pull request #18 from tvallas/feat/add-support-for-environment-variables

feat(cli): add option to configure application using environment vari… ([`b4403ed`](https://github.com/tvallas/mtr2mqtt/commit/b4403edc76b5b8c23ee82b888520195d0bdce39f))


## v0.1.2 (2021-03-28)

### Fix

* fix: add missing dependency to PyYAML ([`c6ea963`](https://github.com/tvallas/mtr2mqtt/commit/c6ea9634df7ccae78b8a44607ae7f7e4d70e89b1))

### Unknown

* Merge pull request #17 from tvallas/fix/add-missing-dependencies

fix: add missing dependency to PyYAML ([`f513666`](https://github.com/tvallas/mtr2mqtt/commit/f51366685c2d341778a67005e9ce156f56ce8c9a))


## v0.1.1 (2021-03-28)

### Ci

* ci: change version in setup.py file to use variable ([`2884704`](https://github.com/tvallas/mtr2mqtt/commit/28847046abeca32dd90a759e9e3e10bdfd51355b))

### Fix

* fix: test semantic versioning ([`ad0814b`](https://github.com/tvallas/mtr2mqtt/commit/ad0814b2d84cd5678ef7b7199af57d9ea7c1959e))

### Unknown

* Merge pull request #16 from tvallas/fix/semantic-release-test

fix: test semantic versioning ([`90b53c7`](https://github.com/tvallas/mtr2mqtt/commit/90b53c7f5f4ea9d1fffaa56bdfaeecdcda2a4951))

* Merge pull request #15 from tvallas/ci/semantic-release-settings

ci: change version in setup.py file to use variable ([`d8153fb`](https://github.com/tvallas/mtr2mqtt/commit/d8153fb72697fe41ce0ce4a465f707f75da14cb5))


## v0.1.0 (2021-03-28)

### Chore

* chore: update Pipfile.lock ([`986ff61`](https://github.com/tvallas/mtr2mqtt/commit/986ff6119b7b33d2496745dc57a40018ed78e339))

* chore: update pyYML version requirement for security  vulnerability reasons ([`a7271be`](https://github.com/tvallas/mtr2mqtt/commit/a7271be78ced193e29947c2174d8a751cc660cf4))

### Ci

* ci: change tests and lint to use pipenv ([`1e13dc2`](https://github.com/tvallas/mtr2mqtt/commit/1e13dc2aa28b878fed7cdc3d9930c7a46be7000b))

* ci: fix pylint test ([`39d7b9a`](https://github.com/tvallas/mtr2mqtt/commit/39d7b9a5757eeab2cf6084c404004f26788c1635))

* ci: fix pylint dependencies ([`4f34513`](https://github.com/tvallas/mtr2mqtt/commit/4f3451364a6c384d55a4df59b5d8c84f009a1ca2))

* ci(pylint): fix dependencies installation for pylint step ([`cfed3e7`](https://github.com/tvallas/mtr2mqtt/commit/cfed3e7ab5298e31f14c89e39a7cec345113f0d4))

* ci(ci): test ci by doing style fixes ([`7ac9d7e`](https://github.com/tvallas/mtr2mqtt/commit/7ac9d7ec0afa3685b391f7303482a9259c178498))

* ci: fix imports ([`62efeda`](https://github.com/tvallas/mtr2mqtt/commit/62efeda449832dd0dd82d647bb9dd5ac78e79333))

* ci(gitlab actions): test gitlab actions

Also some style changes and reorganising directory structure etc. ([`66a63ac`](https://github.com/tvallas/mtr2mqtt/commit/66a63ace68fe677c20903a2b81377359288dd940))

* ci(ci): test GitHub actions ([`85cfec4`](https://github.com/tvallas/mtr2mqtt/commit/85cfec41229e025de59a91ed9ae812967daf20a7))

* ci(ci): testing github actions ([`217d5fd`](https://github.com/tvallas/mtr2mqtt/commit/217d5fd1646a96412931f8a98251b50b6b3f7683))

### Documentation

* docs: fix syntax in readme ([`0415bd5`](https://github.com/tvallas/mtr2mqtt/commit/0415bd5adc0e593d62d1ef4c1cf199b326ad4a2a))

### Feature

* feat: add debug logging of unsupported packages ([`f7ae1e3`](https://github.com/tvallas/mtr2mqtt/commit/f7ae1e341a66cfff0689cd74fac474956c2f6e58))

* feat(mtr): add UTC timestamp field to reading output json ([`78fc3ff`](https://github.com/tvallas/mtr2mqtt/commit/78fc3ff4bebafe34e4a2f4ca2f11348c851944ff))

* feat(calibration support): add simple support for Utility packets having calibration date ([`950b731`](https://github.com/tvallas/mtr2mqtt/commit/950b73125ca46232766f36c9aa3304cacced16b6))

* feat(mtr2mqtt): initial commit ([`12dd367`](https://github.com/tvallas/mtr2mqtt/commit/12dd3673384d1bba466d437b72a6341be54fdcd2))

### Fix

* fix: ignore responses with checksum error ([`a6dd3c1`](https://github.com/tvallas/mtr2mqtt/commit/a6dd3c15ec1987fb84d7dc42cefea866e8a91a89))

* fix: fix utility packet return value to valid response instead of None if device wasn&#39;t calibrated ([`f5c7c09`](https://github.com/tvallas/mtr2mqtt/commit/f5c7c097ec78ac505841bbabd0040e189fed030c))

* fix(gitignore): fix typo in sample metadata file name ([`1b3125f`](https://github.com/tvallas/mtr2mqtt/commit/1b3125f45ce0a63cfd708c65797ecadba6c8fda4))

* fix(metadata): fix transmitter id comparison ([`4958340`](https://github.com/tvallas/mtr2mqtt/commit/49583404144c47f14e0ee2408a721752b78aafe0))

### Performance

* perf: cut the execution tree and at the first supported device ([`077b551`](https://github.com/tvallas/mtr2mqtt/commit/077b5511174b67788814cc22fed6613eee522c67))

### Refactor

* refactor(metadata): change loadfile function to return value as string ([`cc5a47d`](https://github.com/tvallas/mtr2mqtt/commit/cc5a47df0995eda0886bdaa98aad96439e5b989d))

* refactor: change args to named parameters ([`7fe014c`](https://github.com/tvallas/mtr2mqtt/commit/7fe014c3fbbade6f0766f32dd9c65fda6d8e8fa0))

* refactor: fix PEP8 style issues ([`989a491`](https://github.com/tvallas/mtr2mqtt/commit/989a491f8119e25cd9b7bcf54b181ddfd91c0e70))

* refactor: pEP8 style fixes ([`1fe1fbb`](https://github.com/tvallas/mtr2mqtt/commit/1fe1fbb771bde704182a3ae90f4b6d74ac0d579f))

* refactor(cli): fix simple pep8 style issues ([`b0c49c9`](https://github.com/tvallas/mtr2mqtt/commit/b0c49c9e5b5f5d95b19b062ee781bd570de18516))

* refactor(tests_mtr): fix pep8 style issues ([`9fb2c7d`](https://github.com/tvallas/mtr2mqtt/commit/9fb2c7d97cc274ecd9c110832307932bfbfe6006))

* refactor(scl): fix pep8 style issues ([`3d474d8`](https://github.com/tvallas/mtr2mqtt/commit/3d474d844b97c872bb02eeaacf5887d3208c4e00))

* refactor(mtr): fix pep8 style issues and add payload size check warning ([`93f15ca`](https://github.com/tvallas/mtr2mqtt/commit/93f15ca646519954d34339d8ae17048a1366969e))

* refactor(metadata): fix pep8 style issues ([`a33f0b3`](https://github.com/tvallas/mtr2mqtt/commit/a33f0b3be1995f1fb4c18b78e0af46238a7b00ae))

### Test

* test(metadata): add unit tests for metadata module ([`eac3675`](https://github.com/tvallas/mtr2mqtt/commit/eac3675aa4cd091c6cd48ebd7a4554b7f4c51382))

### Unknown

* Merge pull request #14 from tvallas/ci/fix-pipenv-for-unit-tests

ci: change tests and lint to use pipenv ([`a847c0e`](https://github.com/tvallas/mtr2mqtt/commit/a847c0e5cb908a0f9dd6393477490d455ce96acd))

* Feat/add semantic versioning (#13)

* feat: add python-semantic-release package and change setup.py to use variable for versioning

* ci: add test version of semantic release workflow ([`057554d`](https://github.com/tvallas/mtr2mqtt/commit/057554d1c18b2910976dbd3e410915c28d453de4))

* Merge pull request #12 from tvallas/chore/pipfile-lock-update

chore: update Pipfile.lock ([`35fd3dc`](https://github.com/tvallas/mtr2mqtt/commit/35fd3dcc9e3a9662669344e53aecfbada4804bc3))

* Merge pull request #11 from tvallas/fix/ignore-packets-with-wrong-checksum

Fix/ignore packets with wrong checksum ([`59f4b39`](https://github.com/tvallas/mtr2mqtt/commit/59f4b392d920e9e24bafb802b672b19cc22662fd))

* Merge pull request #10 from tvallas/fix/metadata-handling-for-utility-packets

fix: fix utility packet return value to valid response instead of Non… ([`0321243`](https://github.com/tvallas/mtr2mqtt/commit/03212439f5659e28dec6b5c410914fcd4a9055a9))

* Merge pull request #9 from tvallas/test/add-meta-data-tests

fix(gitignore): fix typo in sample metadata file name ([`911b47a`](https://github.com/tvallas/mtr2mqtt/commit/911b47a4fda3b068445600ec965bec3cff7a6a68))

* Merge pull request #8 from tvallas/test/add-meta-data-tests

Test/add meta data tests ([`53c70a9`](https://github.com/tvallas/mtr2mqtt/commit/53c70a9f5e576c2d871dbe2e77d1f829c757ed3e))

* Merge pull request #7 from tvallas/fix/mtr_parsing_improvements

Fix/mtr parsing improvements ([`ee776c7`](https://github.com/tvallas/mtr2mqtt/commit/ee776c7b721b339db2fc0753a82a1206dcafc545))

* Merge pull request #6 from tvallas/fix/readme-fixes

docs: fix syntax in readme ([`2117771`](https://github.com/tvallas/mtr2mqtt/commit/2117771f48d14d0b09abfc7f2b7461b067bb6198))

* Merge pull request #5 from tvallas/fix/pep8-style-issues

Fix/pep8 style issues ([`3777f06`](https://github.com/tvallas/mtr2mqtt/commit/3777f064e23c21c132fd01312f06ee0f42ea3b98))

* Merge pull request #4 from tvallas/feature/simple-ci-setup

Feature/simple ci setup ([`381e54e`](https://github.com/tvallas/mtr2mqtt/commit/381e54e075909289bea7477c8d1f8d3b6fc0fcfe))

* Merge pull request #3 from tvallas/feature/add-timestamp-to-mqtt-output

feat(mtr): add UTC timestamp field to reading output json ([`f61b1b2`](https://github.com/tvallas/mtr2mqtt/commit/f61b1b2fdc497efe7447b0b11f78ea41e28b9c40))

* Merge pull request #1 from tvallas/feature/utility-packet-support

feat(calibration support): add simple support for Utility packets hav… ([`67a86ad`](https://github.com/tvallas/mtr2mqtt/commit/67a86adddd0d1930cb7b491e19adb86343a64ee7))
