from ward import test, using
import httpx

from tests.fixtures import fi_client
import tests.secrets as shh


@test('test login', tags=['unit'])
@using(client=fi_client)
async def _(client):
    r = await client.login(email=shh.email, password=shh.password)
    assert r.status_code == httpx.codes.OK
