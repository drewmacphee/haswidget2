"""Common code for Swidget."""
from __future__ import annotations

from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, TypeVar

from .swidgetclient.device import SwidgetDevice
from typing_extensions import Concatenate, ParamSpec

from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SwidgetDataUpdateCoordinator

_T = TypeVar("_T", bound="CoordinatedSwidgetEntity")
_P = ParamSpec("_P")


def async_refresh_after(
    func: Callable[Concatenate[_T, _P], Awaitable[None]]  # type: ignore[misc]
) -> Callable[Concatenate[_T, _P], Coroutine[Any, Any, None]]:  # type: ignore[misc]
    """Define a wrapper to refresh after."""

    async def _async_wrap(self: _T, *args: _P.args, **kwargs: _P.kwargs) -> None:
        await func(self, *args, **kwargs)
        await self.coordinator.async_request_refresh_without_children()

    return _async_wrap


def format_mac(mac: str) -> str:
    """Format MAC address to be consistent (lowercase, no separators)."""
    return mac.replace(":", "").replace("-", "").lower()


def short_mac(mac: str) -> str:
    """Get a short unique identifier from MAC address.
    
    Takes the last 6 characters (3 bytes) of the MAC which are unique per device,
    since the first 6 characters (OUI) are the same for all Swidget devices.
    """
    clean_mac = format_mac(mac)
    return clean_mac[-6:]  # Last 6 hex chars (e.g., "a1b2c3")


class CoordinatedSwidgetEntity(CoordinatorEntity[SwidgetDataUpdateCoordinator]):
    """Common base class for all coordinated Swidget entities."""

    _attr_has_entity_name = True

    def __init__(
        self, device: SwidgetDevice, coordinator: SwidgetDataUpdateCoordinator
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.device: SwidgetDevice = device
        self._device_mac = short_mac(self.device.mac_address)
        self._attr_unique_id = self._device_mac

    @property
    def device_info(self) -> DeviceInfo:
        """Return information about the device."""
        return DeviceInfo(
            connections={(dr.CONNECTION_NETWORK_MAC, self.device.mac_address)},
            identifiers={(DOMAIN, self._device_mac)},
            manufacturer="Swidget",
            model=self.device.model,
            name=self.device.friendly_name,
            sw_version=self.device.version,
        )

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return bool(self.device.is_on)
