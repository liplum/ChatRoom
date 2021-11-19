from events import event


class notified:
    def __init__(self):
        self._on_content_changed = event()

    @property
    def on_content_changed(self) -> event:
        """
        Para 1:current object

        :return: event(noticed)
        """
        return self._on_content_changed
