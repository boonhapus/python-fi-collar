from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional
import datetime as dt
import re

from pydantic import BaseModel


Latitude = float
Longitude = float


def _camel_to_snake(name: str) -> str:
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def _alter_dictionary(dictionary, transform):
    empty = {}

    for k, v in dictionary.items():
        k = transform(k)

        if isinstance(v, dict):
            v = _alter_dictionary(v, transform)

        empty[k] = v

    return empty


class Base(BaseModel):
    """
    """
    # class Config:
    #     orm_mode = True

    @classmethod
    def from_graph_response(cls, data):
        new = _alter_dictionary(data, _camel_to_snake)
        return cls(**new)


class StepsActivity(Base):
    date_key: str  # YYYY-MM-DDTHH
    steps: int
    distance: float

    @property
    def datetime(self) -> dt.datetime:
        return dt.datetime.strptime(self.date_key, '%Y-%m-%dT%H')


class SleepActivity(Base):
    date_key: str  # YYYY-MM-DDTHH
    napping_minutes: int
    sleeping_minutes: int

    @property
    def datetime(self) -> dt.datetime:
        return dt.datetime.strptime(self.date_key, '%Y-%m-%dT%H')


class Collar(Base):
    id: str
    owner_id: str
    with_user_id: str
    battery_percent: float
    is_led_on: bool
    led_color: str
    gps_coordinates: Tuple[Latitude, Longitude]
    zone: str
    wifi_network: str
    is_online: bool
    is_lost: bool
    last_seen: dt.datetime


class Pet(Base):
    id: str
    name: str
    breed: str
    gender: str
    weight: float
    daily_steps_goal: str
    profile_photo: str
    collar: Collar
    steps_history: List[StepsActivity]
    sleep_history: List[SleepActivity]

    @property
    def at_location(self) -> Optional[str]:
        """

        """
        return self.collar.zone

    @property
    def with_user(self) -> Optional[str]:
        """

        """
        return self.collar.with_user_id

    @property
    def today_steps(self) -> int:
        """
        Time spent sleeping in minutes.
        """
        today = dt.datetime.now().date
        activity = (h for h in self.steps_history[-24:] if h.datetime.date == today)
        return sum(h.steps for h in activity)

    @property
    def today_sleep(self) -> int:
        """
        Time spent sleeping in minutes.
        """
        today = dt.datetime.now().date
        activity = (h for h in self.sleep_history[-24:] if h.datetime.date == today)
        return sum(h.sleeping_minutes for h in activity)

    @property
    def today_naps(self) -> int:
        """
        Time spent napping in minutes.
        """
        today = dt.datetime.now().date
        activity = (h for h in self.sleep_history[-24:] if h.datetime.date == today)
        return sum(h.napping_minutes for h in activity)


class BaseStation(Base):
    id: str
    name: str
    gps_coordinates: Tuple[Latitude, Longitude]
    wifi_network: str
    signal_quality: str
    is_online: bool


class Account(Base):
    id: str
    email: str
    first_name: str
    last_name: str
    phone_number: str
    pets: List[Pet]
    bases: List[BaseStation]

    @property
    def name(self) -> str:
        return ' '.join(self.first_name, self.last_name)

    @classmethod
    def from_graph_response(cls, data):
        tx = data.json()['data']['currentUser']
        return super().from_graph_response(tx)


# TODO: use aliases and dynamically build this query for each pet
Q_PET_ACTIVITY_REFRESH = """
query PetActivityRefresh(petId: $pet_id) {
    pet (id: $petId) {
        ...activityThisHour
        ...activityThisDay
        ...currentLocation
        # ...statusLED
        # ...statusBattery
    }
}
"""


F_ACTIVITY_THIS_HOUR = """
"""

F_ACTIVITY_THIS_DAY = """
"""

F_CURRENT_LOCATION = """
"""


ACCOUNT_DETAILED = """
query {

    pet (id: $pet_id) {
        ongoingActivity(walksVersion: 1) {
            __typename
            start
            presentUser {
              __typename
              id
            }
            areaName
            lastReportTimestamp
            obfuscatedReason
            totalSteps
            uncertaintyInfo {
                __typename
                areaName
                updatedAt
                circle {
                    __typename
                    radius
                    latitude
                    longitude
                }
            }
            ... on OngoingWalk {
                distance
                positions {
                    __typename
                    date
                    errorRadius
                    position {
                        __typename
                        latitude
                        longitude
                    }
                }
                path {
                    __typename
                    position {
                        __typename
                        latitude
                        longitude
                    }
                }
            }
            ... on OngoingRest {
                position {
                    __typename
                    latitude
                    longitude
                }
                place {
                    __typename
                    id
                    name
                    address
                    radius
                    position {
                        __typename
                        latitude
                        longitude
                    }
                }
            }
        }
    }

    currentUser {
        __typename
        id
        email
        firstName
        lastName
        # phoneNumber
        # fiNewsNotificationsEnabled
        # chipReseller {
        #     id
        # }

        userHouseholds {
            __typename

            household {
                __typename

                pets {
                    __typename
                    id
                    name
                    # profilePhoto {
                    #     id
                    #     caption
                    #     date
                    #     likeCount
                    #     liked
                    #     image {
                    #         __typename
                    #         fullSize
                    #     }
                    # }
                    # homeCityState
                    # yearOfBirth
                    # monthOfBirth
                    # dayOfBirth
                    # gender
                    # weight
                    # isPurebred
                    # instagramHandle
                    breed {
                        __typename
                        id
                        name
                        # popularityScore
                    }
                    photos {
                        __typename
                        first {
                            __typename
                            id
                            caption
                            date
                            likeCount
                            liked
                            image {
                                __typename
                                fullSize
                            }
                        }
                    }
                    # items {
                    #     __typename
                    #     id
                    #     caption
                    #     date
                    #     likeCount
                    #     liked
                    #     image {
                    #         __typename
                    #         fullSize
                    #     }
                    # }
                }

                bases {
                    __typename
                    baseId
                    name
                    position {
                        __typename
                        latitude
                        longitude
                    }
                    infoLastUpdated
                    networkName
                    online
                    onlineQuality
                }
            }
        }
    }
}
"""
