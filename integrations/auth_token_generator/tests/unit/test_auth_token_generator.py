import json
import boto3
import requests_mock
from moto import mock_secretsmanager
from freezegun import freeze_time
from pom_common.test.test_utils import get_local_testconfig

REGION = "us-east-1"
TENANT = "testtenant"
STAGE = "x"
SECRET_NAME_NEWSTORE_API_USER = f"{TENANT}-newstore-api-user"

AUTH_URL = f"https://{TENANT}.{STAGE}.newstore.net/v0/token"

# 2021-03-17 12:47:42, exp=1615985262
FIRST_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlFqQTFSVEEwTVVSQ05qWXpNVGhFT0RZeE5UVTVSakl6TTBFd05qQkJNVGd4UVRnNE1VUkROQSJ9.eyJodHRwOi8vbmV3c3RvcmUvbmV3c3RvcmVfaWQiOiJhM2MxMjE1YTEwNmU0MzFhOTI5ODE1YWU3MWY2YjA3NyIsImh0dHA6Ly9uZXdzdG9yZS9yb2xlcyI6WyJuZXdzdG9yZV9hZG1pbiJdLCJodHRwOi8vbmV3c3RvcmUvdGVuYW50IjoibmV3c3RvcmUiLCJpc3MiOiJodHRwczovL2Rldi1uZXdzdG9yZS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWY1NzYyNzkwYTBiMjYwMDY3ZGMyMjI2IiwiYXVkIjoiaHR0cHM6Ly9kZXYtbmV3c3RvcmUuYXV0aDAuY29tL2FwaS92Mi8iLCJpYXQiOjE2MTU4OTg4NjIsImV4cCI6MTYxNTk4NTI2MiwiYXpwIjoiRThxdDF2ZXo3NWRDOVl2N0cyNlN3WThwcnlDV2o5SGkiLCJzY29wZSI6InJlYWQ6Y3VycmVudF91c2VyIHVwZGF0ZTpjdXJyZW50X3VzZXJfbWV0YWRhdGEgZGVsZXRlOmN1cnJlbnRfdXNlcl9tZXRhZGF0YSBjcmVhdGU6Y3VycmVudF91c2VyX21ldGFkYXRhIGNyZWF0ZTpjdXJyZW50X3VzZXJfZGV2aWNlX2NyZWRlbnRpYWxzIGRlbGV0ZTpjdXJyZW50X3VzZXJfZGV2aWNlX2NyZWRlbnRpYWxzIHVwZGF0ZTpjdXJyZW50X3VzZXJfaWRlbnRpdGllcyBvZmZsaW5lX2FjY2VzcyIsImd0eSI6InBhc3N3b3JkIn0.JE6bmHcK4uJZB7uBO_wbiY0AR-TEpJonrVD00Vjam59451aPB0phzntfMuU2W2BqRjR_jziTDQHOexyNRYtGwTfnCkxIiOsJdVho0KDjekdggIYM7tLjIMDCC6e8Jcn5yBS3nhZCAOYciURjfiSWpUQKqJaUZohHMqU4yTd5OrSLDgyG_snZc7kN3nZvg-UfZWElVJfHXwBbsQ0ZR4W0m8-Lt3aadKqC8oIYD2dYSjGprgF-nAr2uW5o7mHwgy8PehqAl5s1UR3ZpSIJ_jVo3BEDV6sQAVyKB1Q7yH_7jYRD35W7hT_l6ow1GyN8lt5OBvRA5ra9Zhx76-d3HiVbRA" # pylint: disable=line-too-long

# 2021-03-18 21:00:48, exp=1616101248
FORCE_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlFqQTFSVEEwTVVSQ05qWXpNVGhFT0RZeE5UVTVSakl6TTBFd05qQkJNVGd4UVRnNE1VUkROQSJ9.eyJodHRwOi8vbmV3c3RvcmUvbmV3c3RvcmVfaWQiOiJhM2MxMjE1YTEwNmU0MzFhOTI5ODE1YWU3MWY2YjA3NyIsImh0dHA6Ly9uZXdzdG9yZS9yb2xlcyI6WyJuZXdzdG9yZV9hZG1pbiJdLCJodHRwOi8vbmV3c3RvcmUvdGVuYW50IjoibmV3c3RvcmUiLCJpc3MiOiJodHRwczovL2Rldi1uZXdzdG9yZS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWY1NzYyNzkwYTBiMjYwMDY3ZGMyMjI2IiwiYXVkIjoiaHR0cHM6Ly9kZXYtbmV3c3RvcmUuYXV0aDAuY29tL2FwaS92Mi8iLCJpYXQiOjE2MTYwMTQ4NDgsImV4cCI6MTYxNjEwMTI0OCwiYXpwIjoiRThxdDF2ZXo3NWRDOVl2N0cyNlN3WThwcnlDV2o5SGkiLCJzY29wZSI6InJlYWQ6Y3VycmVudF91c2VyIHVwZGF0ZTpjdXJyZW50X3VzZXJfbWV0YWRhdGEgZGVsZXRlOmN1cnJlbnRfdXNlcl9tZXRhZGF0YSBjcmVhdGU6Y3VycmVudF91c2VyX21ldGFkYXRhIGNyZWF0ZTpjdXJyZW50X3VzZXJfZGV2aWNlX2NyZWRlbnRpYWxzIGRlbGV0ZTpjdXJyZW50X3VzZXJfZGV2aWNlX2NyZWRlbnRpYWxzIHVwZGF0ZTpjdXJyZW50X3VzZXJfaWRlbnRpdGllcyBvZmZsaW5lX2FjY2VzcyIsImd0eSI6InBhc3N3b3JkIn0.Aku9ghB4gVlftwYlOn082LrBi5sgjDmOiA-jKOBhV0kdc5591pz64K3ohtONOOZfGBEn-RXn3ezTSEG0H5F-LclXZnq7MvaxFIRSVZolu43A76YrkCkKh3d8iUujhrjAFEPytrTwTJ5ixL0SAhxUetOUNJcBphfRvZmYIOa6n6dL1dKVkh6w0GVjb8S0p2-4ilmTzBEb6xbKlEV9yikDuLhuaBZoIadelfuMuMFHN87fImg0knGnKDCfgtFTu87rNSkJE1DIJI-FmBzES49yPEgt5SeI08jB5bmCItLYeRMloYRnxGxLQEfRPt6kpH7ShIHVdGlt_5dd5794_5gQDQ" # pylint: disable=line-too-long

# 2021-03-19 09:56:19, exp=1616147779
EXP_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlFqQTFSVEEwTVVSQ05qWXpNVGhFT0RZeE5UVTVSakl6TTBFd05qQkJNVGd4UVRnNE1VUkROQSJ9.eyJodHRwOi8vbmV3c3RvcmUvbmV3c3RvcmVfaWQiOiJhM2MxMjE1YTEwNmU0MzFhOTI5ODE1YWU3MWY2YjA3NyIsImh0dHA6Ly9uZXdzdG9yZS9yb2xlcyI6WyJuZXdzdG9yZV9hZG1pbiJdLCJodHRwOi8vbmV3c3RvcmUvdGVuYW50IjoibmV3c3RvcmUiLCJpc3MiOiJodHRwczovL2Rldi1uZXdzdG9yZS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWY1NzYyNzkwYTBiMjYwMDY3ZGMyMjI2IiwiYXVkIjoiaHR0cHM6Ly9kZXYtbmV3c3RvcmUuYXV0aDAuY29tL2FwaS92Mi8iLCJpYXQiOjE2MTYwNjEzNzksImV4cCI6MTYxNjE0Nzc3OSwiYXpwIjoiRThxdDF2ZXo3NWRDOVl2N0cyNlN3WThwcnlDV2o5SGkiLCJzY29wZSI6InJlYWQ6Y3VycmVudF91c2VyIHVwZGF0ZTpjdXJyZW50X3VzZXJfbWV0YWRhdGEgZGVsZXRlOmN1cnJlbnRfdXNlcl9tZXRhZGF0YSBjcmVhdGU6Y3VycmVudF91c2VyX21ldGFkYXRhIGNyZWF0ZTpjdXJyZW50X3VzZXJfZGV2aWNlX2NyZWRlbnRpYWxzIGRlbGV0ZTpjdXJyZW50X3VzZXJfZGV2aWNlX2NyZWRlbnRpYWxzIHVwZGF0ZTpjdXJyZW50X3VzZXJfaWRlbnRpdGllcyBvZmZsaW5lX2FjY2VzcyIsImd0eSI6InBhc3N3b3JkIn0.CVo9XFTOFLX6Bjqp0uaIMOC30bTx8Ug3gp_3YHpJptMoBkKgWYDKK0sRWd7ohNfJ1QVnDqzX2NC_-z-yYajWIqlAdAlkdf94LTbesbO64vD81iz2796LXdfZNBeNF7U4xZphFyKZvaPabb4XJRr4KXcj-AzxqqWQaX94J3eaaH9KIG-aPY1lyh2WudS-1Jaw4bEMhvTb9q8MlHt2Ib8c9pC6gPMi8XnMqOb25LVDhNis_aL9CYFGiCr8V9_XOpRX36C_mP0mtTtOrQzwAdT76e1lZwBnOk361Xt_Nz_KbENZ8_ylHs10_VpcyW4xyO6oJb1n_dYvfBGdw9-ztAOuiQ" # pylint: disable=line-too-long

# 2021-03-19 10:38:36, exp=1616150316
OFFSET_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlFqQTFSVEEwTVVSQ05qWXpNVGhFT0RZeE5UVTVSakl6TTBFd05qQkJNVGd4UVRnNE1VUkROQSJ9.eyJodHRwOi8vbmV3c3RvcmUvbmV3c3RvcmVfaWQiOiJhM2MxMjE1YTEwNmU0MzFhOTI5ODE1YWU3MWY2YjA3NyIsImh0dHA6Ly9uZXdzdG9yZS9yb2xlcyI6WyJuZXdzdG9yZV9hZG1pbiJdLCJodHRwOi8vbmV3c3RvcmUvdGVuYW50IjoibmV3c3RvcmUiLCJpc3MiOiJodHRwczovL2Rldi1uZXdzdG9yZS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWY1NzYyNzkwYTBiMjYwMDY3ZGMyMjI2IiwiYXVkIjoiaHR0cHM6Ly9kZXYtbmV3c3RvcmUuYXV0aDAuY29tL2FwaS92Mi8iLCJpYXQiOjE2MTYwNjM5MTYsImV4cCI6MTYxNjE1MDMxNiwiYXpwIjoiRThxdDF2ZXo3NWRDOVl2N0cyNlN3WThwcnlDV2o5SGkiLCJzY29wZSI6InJlYWQ6Y3VycmVudF91c2VyIHVwZGF0ZTpjdXJyZW50X3VzZXJfbWV0YWRhdGEgZGVsZXRlOmN1cnJlbnRfdXNlcl9tZXRhZGF0YSBjcmVhdGU6Y3VycmVudF91c2VyX21ldGFkYXRhIGNyZWF0ZTpjdXJyZW50X3VzZXJfZGV2aWNlX2NyZWRlbnRpYWxzIGRlbGV0ZTpjdXJyZW50X3VzZXJfZGV2aWNlX2NyZWRlbnRpYWxzIHVwZGF0ZTpjdXJyZW50X3VzZXJfaWRlbnRpdGllcyBvZmZsaW5lX2FjY2VzcyIsImd0eSI6InBhc3N3b3JkIn0.pEAGYV5cJuWhw0jzwnbGnkIeMkyjZ2u4_H9DxJH69XEyF3oQldO4sNbzkaFrLBBawJbzHYt3iy8Q1oRDB2ilsDO3NzAkD3BKEZKpR3B5MsgLe0Np7tYtVF8ODFVABCX5kTKphLtHT2vGpDH50viMhrG1p7B3EEYyqgi0atJQcEdZ80LGILhixV1xH65bEzSGngwJjpuNRMe02EZbz0dmnsZ04gnehtIKrxU0p6ryQzdYWFrpR1l72Zhvuw_3vDwPEg4CZHqRKNJirFKqrR4Wzh4prR1CqZmhoOFIH0sTns6xpxng-2kdOZmp5IVlnx15V1ij5qxulqMnHHG7XF0Ptw" # pylint: disable=line-too-long

@mock_secretsmanager
def test_auth_token_generator(monkeypatch):
    # environment
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("REGION", REGION)
    monkeypatch.setenv("TENANT", TENANT)
    monkeypatch.setenv("STAGE", STAGE)
    monkeypatch.setenv("SECRET_NAME_NEWSTORE_API_USER", SECRET_NAME_NEWSTORE_API_USER)

    testconfig = get_local_testconfig({
        "username": "dummy",
        "password": "dummy",
    })

    class mock_utils_instance:
        def get_newstore_config(self):
            return {
                "NS_URL_API": f"{TENANT}.{STAGE}.newstore.net",
                "tenant": "frankandoak",
                "host": f"{TENANT}.{STAGE}.newstore.net"
            }

    class mock_utils():
        def get_instance():
            return mock_utils_instance()

    import auth_token_generator.utils as utils
    monkeypatch.setattr(utils, "Utils", mock_utils)

    secretsmanager = boto3.client("secretsmanager", REGION)
    secretsmanager.create_secret(Name=SECRET_NAME_NEWSTORE_API_USER, SecretString=json.dumps({
        "username": testconfig["username"],
        "password": testconfig["password"],
    }))

    from auth_token_generator.lambdas.auth_token_generator import handler # pylint: disable=import-outside-toplevel

    with freeze_time("2021-03-17 10:00:00"):
        # initial call - get a new token
        with requests_mock.Mocker() as mock:
            mock.post(AUTH_URL, text=json.dumps(token_test_data(FIRST_TOKEN)))
            token_result = handler(None, None)
            assert token_result["body"]["access_token"] == FIRST_TOKEN

        # second call - don't request a new token
        with requests_mock.Mocker() as mock:
            mock.post(AUTH_URL, text=json.dumps(token_test_data("some.other.token")))
            token_result = handler(None, None)
            assert token_result["body"]["access_token"] == FIRST_TOKEN

        # force new token
        with requests_mock.Mocker() as mock:
            mock.post(AUTH_URL, text=json.dumps(token_test_data(FORCE_TOKEN)))
            monkeypatch.setenv("FORCE", "1")
            token_result = handler(None, None)
            assert token_result["body"]["access_token"] == FORCE_TOKEN
            monkeypatch.delenv("FORCE")

        # no new request with FORCE deleted
        with requests_mock.Mocker() as mock:
            mock.post(AUTH_URL, text=json.dumps(token_test_data("an.other.token")))
            token_result = handler(None, None)
            assert token_result["body"]["access_token"] == FORCE_TOKEN

    with freeze_time("2021-03-18 23:30:00"):
        # current token is expired, request a new
        with requests_mock.Mocker() as mock:
            mock.post(AUTH_URL, text=json.dumps(token_test_data(EXP_TOKEN)))
            token_result = handler(None, None)
            assert token_result["body"]["access_token"] == EXP_TOKEN

        # second call for this token - don't request a new token
        with requests_mock.Mocker() as mock:
            mock.post(AUTH_URL, text=json.dumps(token_test_data("yet.another.token")))
            token_result = handler(None, None)
            assert token_result["body"]["access_token"] == EXP_TOKEN

    with freeze_time("2021-03-19 09:50:00"):
        with requests_mock.Mocker() as mock:
            monkeypatch.setenv("EXPIRY_OFFSET", "900") # 15 minutes
            mock.post(AUTH_URL, text=json.dumps(token_test_data(OFFSET_TOKEN)))
            token_result = handler(None, None)
            assert token_result["body"]["access_token"] == OFFSET_TOKEN
            monkeypatch.delenv("EXPIRY_OFFSET")


def token_test_data(token):
    return {
        "access_token": token,
        "refresh_token": "XNGc1MS2FamZjhTBjGPeiN2UFg20ykMhvY9WM9m_xSbY1",
        "expires_in": 86400,
        "scope": "read:current_user update:current_user_metadata delete:current_user_metadata create:current_user_metadata create:current_user_device_credentials delete:current_user_device_credentials update:current_user_identities offline_access", # pylint: disable=line-too-long
        "token_type": "Bearer"
    }
