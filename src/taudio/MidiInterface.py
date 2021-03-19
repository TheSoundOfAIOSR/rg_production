# -*- coding: utf-8 -*-
"""
Created on Wed Mar 17 23:23:37 2021
@author: Fernando Garcia (fergarciadlc)
"""
import json
import rtmidi


class MidiInterface:
    def __init__(self):
        self.api_supported_idxs = rtmidi.get_compiled_api()
        self.api_supported_names = [
            rtmidi.get_api_name(idx) for idx in self.api_supported_idxs
        ]

        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()

        self.devices = self.get_midi_devices()

    def get_midi_devices(self):
        api = []
        for idx, name in zip(self.api_supported_idxs, self.api_supported_names):
            dev = {
                "idx": idx,
                "name": name + " (" + rtmidi.get_api_display_name(idx) + ")",
            }
            api.append(dev.copy())

        midi_devices = {
            "api": api,
            "input": [
                self.midi_in.get_port_name(n)
                for n in range(self.midi_in.get_port_count())
            ],
            "output": [
                self.midi_out.get_port_name(n)
                for n in range(self.midi_out.get_port_count())
            ],
        }

        return midi_devices


def select_midi_device(self, event):
    selected_device = event
    """
    selected_device in the form:
    [idx]"Midi device nane"
    """
    # TODO: improve implementation, maybe with regex
    selected_idx = int(selected_device.split("[")[1].split("]")[0])
    self.midi_input_idx = selected_idx
    print("MIDI device selected: ", self.midi_devices["input"][self.midi_input_idx])
    print(f"Using API: {self.midi_devices['api']}")


if __name__ == "__main__":
    midi = MidiInterface()
    print(json.dumps(midi.devices, indent=2))
