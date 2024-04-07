'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''


class RecipeHop(object):
    def __init__(self,id,quantity, usage,utilisation,multiplicator,temperature,minutes,hours,days,loose,ibu, hop):
        self.id=id
        self.quantity=quantity
        self.usage=usage
        self.utilisation=utilisation
        self.multiplicator=multiplicator
        self.temperature = temperature
        self.minutes=minutes
        self.hours=hours
        self.days=days
        self.loose=loose
        self.ibu=ibu
        self.hop=hop    

    def __repr__(self):
        return self.hop.name+' quantity : '+str(self.quantity)+' Id : '+str(self.id) 