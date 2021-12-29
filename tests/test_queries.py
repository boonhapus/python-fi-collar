from ward import test, using
import httpx

from fi.queries import ACCOUNT_DETAILED

from tests.fixtures import fi_client
import tests.secrets as shh


for name, query in [
    ('account detailed', ACCOUNT_DETAILED)
]:

    @test('test getting {name}', tags=['unit'])
    @using(client=fi_client)
    async def _(client, q=query, *, name=name):
        # NOTE:
        #   the keyword-only argument 'name' is simply consumed, it's required for ward
        #   to dynamically generate the tests.
        await client.login(email=shh.email, password=shh.password)
        r = await client.query(q)
        assert r.status_code == httpx.codes.OK
