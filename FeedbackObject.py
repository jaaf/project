'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''


from PyQt6.QtCore import QObject

class FeedbackObject(object):
    def __init__(self,after_sparge_wort_volume,after_sparge_gravity,additional_water,additional_boil_time,after_boil_wort_volume,after_boil_gravity,notes):
        self.after_sparge_wort_volume =after_sparge_wort_volume
        self.after_sparge_gravity =after_sparge_gravity
        self.additional_water =additional_water
        self.additional_boil_time =additional_boil_time
        self.after_boil_wort_volume =after_boil_wort_volume
        self.after_boil_gravity = after_boil_gravity
        self.notes=notes

    def __repr__(self):
        return f"[{self.after_sparge_wort_volume}, {self.after_sparge_gravity}, {self.additional_water}, {self.additional_boil_time} , {self.after_boil_wort_volume}, {self.after_boil_gravity}]"