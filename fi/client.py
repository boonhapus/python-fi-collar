import httpx

from ._version import __version__
from ._http import RateLimitedHTTPClient


class Fi(RateLimitedHTTPClient):
    """
    Wrapper around the undocumented Fi GraphQL API.

    Parameters
    ----------


    """
    def __init__(self):
        self._session_id = None
        self._user_id = None

        super().__init__(
            tokens=2,
            seconds=1,
            base_url='https://api.tryfi.com',
            headers={
                'User-agent': f'Fi/{__version__} (+github: python-fi-collar)'
            }
        )

    async def login(self, email: str, password: str) -> httpx.Request:
        """
        """
        r = await self.post('auth/login', data={'email': email, 'password': password})
        r.raise_for_status()
        self._session_id = r.json()['sessionId']
        self._user_id = r.json()['userId']
        return r

    async def query(self, q: str, **variables) -> httpx.Request:
        """
        Perform a GraphQL query.

        Parameters
        ----------
        q : str
          graphql query to send to Fi.

        **variables
          graphql variables to substitute
        """
        # for name, value in variables.items():
        #     q = q.replace(f'${name}', f'{value}')
        r = await self.post('/graphql', json={'query': q, 'variables': variables})
        return r
