fermentable_formsold =[['',''],['Malted Grain','Grain malté'], ['Unmalted Grain','Grain non malté'],['Liquid Extract','Extrait liquide'],\
                     ['Dry Extract','Extrait sec'],['Flakes','Flocons'],['Sugar','Sucre'], ['Other','Autre']]
fermentable_forms =['','Grain malté', 'Grain non malté','Extrait liquide',\
                     'Extrait sec','Flocons','Flocons maltés','Sucre', 'Autre']

fermentable_categoriesold = [['',''], ('Base (Pilsner|Lager)','Base (Pilsner|Lager)'),['Base (Pale)','Base (Pale)'],['Base (Pale Ale)','Base (Pale Ale)'], \
                          ['Base (Wheat)','Base (Blé)'],('Base (Rye)','Base (Sègle)'),['Base (Smoked)','Base (Fumé)'],['Munich','Munich'],['Vienna','Vienne'],\
                            ['Aromatic','Aromatique'], ['Amber|Biscuit|Victory','Amber|Biscuit|Victory'],['Brown Malt','Malt brun'], ['Caramel|Crystal','Caramel|Crystal'],\
                                ['Dextrin','Dextrin'],['Special Belge','Special Belge'], ['Honey Malt','Malt miel'],['Pale Chocolate','Chocalat pâle'], ['Chocolate','Chocolate'],\
                                    ['Black Wheat','Blé noir'], ['Roast Barley','Orge rôtie'], ['Roast Rye','Sègle rôti'], ['Black Malt','Malt noir'],\
                                          ['Acidulated','Acidulé'], ['Liquid Extract','Extrait liquide'], ['Dry Extract','Exrait sec'], ['Flakes','Flocons'], ['Sugar','Sucre']]
fermentable_categories = ['','Base (Pilsner|Lager)','Base (Pale)','Base (Pale Ale)', 'Base (Blé)','Base (Sègle)','Base (Fumé)','Munich',\
                          'Vienne','Aromatique','Amber|Biscuit|Victory','Malt brun', 'Caramel|Crystal','Dextrin','Special Belge','Malt miel',\
                            'Chocalat pâle', 'Chocolat','Malt de blé noir','Blé rôti','Orge rôtie', 'Avoine rôtie','Sègle rôti', 'Malt noir','Malt noir désamérisé','Acidulé', 'Extrait liquide',\
                                 'Grains crus', 'Exrait sec', 'Flocons','Flocons maltés', 'Sucre']

raw_ingredientsold =[['',''],['Barley','Orge'],['Wheat','Blé'],['Sarrasin','Sarrasin'],[ 'Oat','Avoine'], ['Rye','Seigle'], ['Spelt','Épeautre'], ['Rice','Riz'], ['Corn','Maïs'],['Other','Autre']]
raw_ingredients =['','Orge','Blé','Sarrasin','Avoine','Seigle','Épeautre','Riz','Maïs','Autre']

hop_forms =[['',''],['Pellets','Granulets'], ['Leaves','Cones'], ['Extract','Extrait']]

hop_purposes =[['',''],['Bitterness','Amertume'],['Arôma','Arômes'],['Both','Les deux']]

yeast_floculation =['','Haute','Moyenne','Basse']

yeast_sedimentation = ['','Rapide','Moyenne','Lente']

yeast_target= ['','Ale','Lager']

yeast_form=['','Sèche','Liquide','Lie']

yeast_pack_unit=['','Paquet 11g sèche','Paquet 100g sèche','Paquet liquide 40ml','Paquet liquide 100ml','Paquet liquide 500ml']

misc_category=['','Sel ou acide','Éclaircisseur','Épice','Agent de flaveur','Herbe','Autre']

misc_unit=['','mg','g','kg','ml','cl','dl','l','paquet','item']

equipment_type = ['','Tout en un','Classique', 'Brassage en sac']

cooler_type =['','Immersion','Contre-courant']

class Acid(object):
    def __init__(self,name,pKa,valence,mole_weight,density,concentration,k_1N):
        self.name=name
        self.pKa=pKa
        self.valence=valence
        self.mole_weight=mole_weight #g
        self.density=density #g/ml
        self.concentration=concentration
        self.k_1N=k_1N #coefficient to transform ml of tis dilution to 1N dilution

    def __repr__(self) :
        return ('name: '+self.name+ ' MW: '+str(self.mole_weight))   

acids=[]
acids.append(Acid('Lactic 80%',[3.86,15.1],2,90.078,1.187,0.8,10.5396))
acids.append(Acid('Lactic 88%',[3.86,15.1],2,90.078,1.206,0.88,11.8111))
acids.append(Acid("Phosphoric 85%",[2.16, 7.21, 12.32],3, 97.995,1.689,0.85,14.65))


    
def get_acid_by_name(name):
    for acid in acids:
        if acid.name==name:
            return acid
        
    return None
    
def get_fermentable_form_name(data):
    #return the name given the data
    for f in fermentable_forms:
        if f[0]==data:
            return f[1]
    return ''    

def get_fermentable_category_name(data):
    #return the translated name given the data (english name)
    for c in fermentable_categories:
        #if c[0]==data:
        #   return c[1]
        if c==data:
            return c
    return ''    

def get_hop_form_name(data):
    #return the translated name given th data (english name)
    for f in hop_forms:
        if f[0] == data:
            return f[1]
    return ''

def get_hop_purpose_name(data):
    #return the french name given the english one
    for p in hop_purposes:
        if p[0] == data:
            return p[1]
        
    return ''

def get_raw_ingredient_name(data):
    #return the translated name given the data (english name)
    for r in raw_ingredients:
        if r[0]==data:
            return r[1]
    return ''    
