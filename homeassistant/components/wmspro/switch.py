"""Support for switches connected with WMS WebControl pro."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from wmspro.const import WMS_WebControl_pro_API_actionDescription

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import WebControlProConfigEntry
from .entity import WebControlProGenericEntity

SCAN_INTERVAL = timedelta(seconds=5)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: WebControlProConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the WMS based lights from a config entry."""
    hub = config_entry.runtime_data

    entities: list[WebControlProGenericEntity] = []
    for dest in hub.dests.values():
        if dest.action(WMS_WebControl_pro_API_actionDescription.LoadSwitch):
            entities.append(WebControlProSwitch(config_entry.entry_id, dest))

    async_add_entities(entities)


class WebControlProSwitch(WebControlProGenericEntity, SwitchEntity):
    """Representation of a WMS based switch."""

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        action = self._dest.action(WMS_WebControl_pro_API_actionDescription.LoadSwitch)
        return action["onOffState"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        action = self._dest.action(WMS_WebControl_pro_API_actionDescription.LoadSwitch)
        await action(onOffState=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        action = self._dest.action(WMS_WebControl_pro_API_actionDescription.LoadSwitch)
        await action(onOffState=False)
