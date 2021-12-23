from ward import fixture

from fi import Fi


@fixture(scope='global')
async def fi_client():
    client = Fi()
    yield client

    # cleanup
    await client.aclose()
