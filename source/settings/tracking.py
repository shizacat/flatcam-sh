"""Notify listeners when a settings or options field changes."""

from collections.abc import Callable

from pydantic import BaseModel, PrivateAttr

from exceptions import SettingsError


class BaseModelChangeTrack(BaseModel):
    """Notify bound callbacks when a field value changes."""

    _change_callbacks: list[Callable[[str], None]] = PrivateAttr(default_factory=list)

    def bind(self, callback: Callable[[str], None]) -> None:
        """
        Binds a callback invoked when a field value changes.

        The callback receives the name of the changed field. Assigning the current value does not call it.

        :param callback: function called with the changed field name
        """
        self._change_callbacks.append(callback)

    def unbind(self, callback: Callable[[str], None]) -> None:
        """
        Removes a callback previously bound with bind.

        :param callback:        function previously passed to bind

        :raises SettingsError:  the callback is not bound
        """
        try:
            self._change_callbacks.remove(callback)
        except ValueError as error:
            raise SettingsError("Callback is not bound.") from error

    def __setattr__(self, name: str, value: object) -> None:
        """
        Sets an attribute and notifies bound callbacks when a field changes.

        :param name:  attribute name
        :param value: attribute value
        """
        if name in type(self).model_fields and name in self.__dict__:
            previous = self.__dict__[name]
            super().__setattr__(name, value)
            if previous != self.__dict__[name]:
                for callback in tuple(self._change_callbacks):
                    callback(name)
            return

        super().__setattr__(name, value)
