"""Support for covers connected with WMS WebControl pro."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from wmspro.destination import Destination
from wmspro.const import (
    WMS_WebControl_pro_API_actionDescription,
    WMS_WebControl_pro_API_actionType,
)

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityDescription,
    CoverEntityFeature,
)
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
    """Set up the WMS based covers from a config entry."""
    hub = config_entry.runtime_data

    entities: list[WebControlProGenericEntity] = []
    for dest in hub.dests.values():
        if dest.action(
            WMS_WebControl_pro_API_actionDescription.RollerShutterBlindDrive
        ):
            entities.append(
                WebControlProRollerShutterBlind(config_entry.entry_id, dest)
            )  # noqa: PERF401
        elif dest.action(WMS_WebControl_pro_API_actionDescription.AwningDrive):
            entities.append(WebControlProAwning(config_entry.entry_id, dest))  # noqa: PERF401
        elif dest.action(WMS_WebControl_pro_API_actionDescription.SlatDrive):
            entities.append(WebControlProSlat(config_entry.entry_id, dest))  # noqa: PERF401
        elif dest.action(WMS_WebControl_pro_API_actionDescription.WindowDrive):
            entities.append(WebControlProWindow(config_entry.entry_id, dest))  # noqa: PERF401

    async_add_entities(entities)


class WebControlProCover(WebControlProGenericEntity, CoverEntity):
    """Representation of a WMS based cover."""

    def __init__(
        self,
        config_entry_id: str,
        dest: Destination,
        drive_type: WMS_WebControl_pro_API_actionDescription,
    ) -> None:
        self._drive_type = drive_type
        super().__init__(config_entry_id, dest)()

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover."""
        action = self._dest.action(self._drive_type)
        if action["percentage"]:
            return 100 - action["percentage"]
        return None

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        action = self._dest.action(self._drive_type)
        await action(percentage=100 - kwargs[ATTR_POSITION])

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        return self.current_cover_position == 0

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        await self.async_set_cover_position(ATTR_POSITION=100)

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        await self.async_set_cover_position(ATTR_POSITION=0)

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the device if in motion."""
        action = self._dest.action(
            WMS_WebControl_pro_API_actionDescription.ManualCommand,
            WMS_WebControl_pro_API_actionType.Stop,
        )
        await action()


class WebControlProRollerShutterBlind(WebControlProCover):
    """Representation of a WMS based normal blind."""

    _attr_device_class = CoverDeviceClass.BLIND

    def __init__(self, config_entry_id: str, dest: Destination) -> None:
        super().__init__(
            config_entry_id,
            dest,
            WMS_WebControl_pro_API_actionDescription.RollerShutterBlindDrive,
        )()


class WebControlProAwning(WebControlProCover):
    """Representation of a WMS based awning."""

    _attr_device_class = CoverDeviceClass.AWNING

    def __init__(self, config_entry_id: str, dest: Destination) -> None:
        super().__init__(
            config_entry_id, dest, WMS_WebControl_pro_API_actionDescription.AwningDrive
        )()

    # @property
    # def current_cover_position(self) -> int | None:
    #     """Return current position of cover."""
    #     action = self._dest.action(WMS_WebControl_pro_API_actionDescription.AwningDrive)
    #     if action["percentage"]:
    #         return 100 - action["percentage"]
    #     return None

    # async def async_set_cover_position(self, **kwargs: Any) -> None:
    #     """Move the cover to a specific position."""
    #     action = self._dest.action(WMS_WebControl_pro_API_actionDescription.AwningDrive)
    #     await action(percentage=100 - kwargs[ATTR_POSITION])


class WebControlProSlat(WebControlProCover):
    """Representation of a WMS based slat."""

    _attr_device_class = CoverDeviceClass.SHUTTER
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.SET_POSITION
        | CoverEntityFeature.STOP
        | CoverEntityFeature.OPEN_TILT
        | CoverEntityFeature.CLOSE_TILT
        | CoverEntityFeature.SET_TILT_POSITION
        | CoverEntityFeature.STOP_TILT
    )

    def __init__(self, config_entry_id: str, dest: Destination) -> None:
        super().__init__(
            config_entry_id, dest, WMS_WebControl_pro_API_actionDescription.SlatDrive
        )()

    @property
    def current_cover_tilt_position(self) -> int | None:
        """Return current position of cover."""
        action = self._dest.action(WMS_WebControl_pro_API_actionDescription.SlatRotate)
        if action["percentage"]:
            return action["percentage"]
        return None

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        action = self._dest.action(WMS_WebControl_pro_API_actionDescription.SlatRotate)
        await action(percentage=kwargs[ATTR_POSITION])

    async def async_open_cover_tilt(self, **kwargs: Any) -> None:
        """Open the cover."""
        await self.async_set_cover_tilt_position(ATTR_POSITION=100)

    async def async_close_cover_tilt(self, **kwargs: Any) -> None:
        """Close the cover."""
        await self.async_set_cover_tilt_position(ATTR_POSITION=0)

    async def async_stop_cover_tilt(self, **kwargs: Any) -> None:
        """Stop the device if in motion."""
        action = self._dest.action(
            WMS_WebControl_pro_API_actionDescription.ManualCommand,
            WMS_WebControl_pro_API_actionType.Stop,
        )
        await action()


class WebControlProWindow(WebControlProCover):
    """Representation of a WMS based window."""

    _attr_device_class = CoverDeviceClass.WINDOW

    def __init__(self, config_entry_id: str, dest: Destination) -> None:
        super().__init__(
            config_entry_id, dest, WMS_WebControl_pro_API_actionDescription.WindowDrive
        )()

    # @property
    # def current_cover_position(self) -> int | None:
    #     """Return current position of cover."""
    #     action = self._dest.action(WMS_WebControl_pro_API_actionDescription.WindowDrive)
    #     if action["percentage"]:
    #         return 100 - action["percentage"]
    #     return None

    # async def async_set_cover_position(self, **kwargs: Any) -> None:
    #     """Move the cover to a specific position."""
    #     action = self._dest.action(WMS_WebControl_pro_API_actionDescription.WindowDrive)
    #     await action(percentage=100 - kwargs[ATTR_POSITION])
