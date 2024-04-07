'''
Copyright José FOURNIER 2023

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

from database.fermentables.fermentable import Fermentable,are_equal
class RecipeFermentable(object):
    def __init__(self, id,quantity,usage,steep_potential,diph, buffering_capacity,fermentable):
        self.id=id
        self.quantity=quantity
        self.usage=usage
        self.steep_potential=steep_potential
        self.diph=diph
        self.buffering_capacity=buffering_capacity
        self.fermentable=fermentable

    def __repr__(self):
        return self.fermentable.name+' quantity : '+str(self.quantity) +' Id : '+str(self.id) +' DI pH : '+str(self.diph)
    
    @staticmethod
    def are_equal(r1,r2) :
        if r1.quantity!=r2.quantity:
            return False
        if r1.usage!=r2.usage:
            return False  
        if r1.steep_potential!=r2.steep_potential:
            return False
        if r1.diph!=r2.diph:
            return False
        if r1.buffering_capacity!=r2.buffering_capacity:
            return False
        if not Fermentable.are_equal(r1.fermentable,r2.fermentable):
            return False
        return True    
              