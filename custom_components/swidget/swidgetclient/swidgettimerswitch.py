from .device import (
    DeviceType,
)
from .swidgetswitch import SwidgetSwitch

class SwidgetTimerSwitch(SwidgetSwitch):

    def __init__(self, host,  secret_key: str, ssl: bool) -> None:
        super().__init__(host=host, secret_key=secret_key, ssl=ssl)
        self._device_type = DeviceType.TimerSwitch

    @property
    def is_on(self) -> bool:
        """Return whether device is on, checking both toggle state and timer duration."""
        toggle_state = self.assemblies['host'].components["0"].functions['toggle']["state"]
        try:
            timer_duration = self.assemblies['host'].components["0"].functions['timer'].get("duration", 0)
            # Device is on if toggle is on AND timer has a duration > 0
            return toggle_state == "on" and timer_duration > 0
        except (KeyError, AttributeError):
            # Fallback to toggle state if timer info not available
            return toggle_state == "on"

    async def set_countdown_timer(self, minutes):
        """Set the countdown timer."""
        await self.send_command(
            assembly="host", component="0", function="timer", command={"duration": minutes}
        )