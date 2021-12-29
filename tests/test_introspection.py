from ward import test, using
import httpx

from tests.fixtures import fi_client
import tests.secrets as shh


query = """
query TestIntrospection {
    currentUser {
        __typename
        id
        firstName

        userHouseholds {
            __typename

            household {
                __typename

                pets {
                    __typename
                    id
                }
            }
        }
    }
}
"""

query = """
query PetDataRefresh ($petId: ID!) {
    pet (id: $petId) {
        __typename
        id

        live_steps: ongoingActivity(walksVersion: 1) {
            ... on OngoingWalk {
                ...timestampsStartEnd
                totalSteps
                distance
                positions {
                    date
                    position {
                        latitude
                        longitude
                    }
                }
            }
        }

        live_sleep: ongoingActivity(walksVersion: 1) {
            ... on OngoingRest {
                ...timestampsStartEnd
                position {
                    latitude
                    longitude
                }
            }
        }

        # past_day: currentActivitySummary(period: DAILY) {
        #     start
        #     end
        #     totalSteps
        #     totalDistance
        # }

        currentDailySummary {
            __typename
            start
            end
            totalSteps
            # asleep
        }

        # ...activityThisDay
        # ...currentLocation
        # ...statusLED
        # ...statusBattery
    }
}

fragment timestampsStartEnd on OngoingActivity {
    __typename
    start
    lastReportTimestamp
    # at_location: areaName
    # with_user: presentUser {
    #     id
    # }
}
"""
variables = {
    'petId': '6cEIDbH1zqjjCBwcT8xVPa'
}


@test('test introspection', tags=['introspection'])
@using(client=fi_client)
async def _(client, q=query, v=variables):
    from rich import print

    await client.login(email=shh.email, password=shh.password)
    r = await client.query(q, **v)
    # assert r.status_code == httpx.codes.OK

    print(r)
    print(r.headers)
    print(r.json())
    assert 1 == 2
