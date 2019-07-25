async def test_index(cli):
    resp = await cli.get('/')
    assert resp.status == 200
