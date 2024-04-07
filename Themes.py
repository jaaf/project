from PyQt6.QtGui import QPalette,QColor



class Themes():

    @staticmethod
    def get_palette(theme_name):
        match theme_name:
            case 'brown':
                pal=QPalette()
                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(98,95,95))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor('68,65,65'))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(78,75,75))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(45,45,45)) 
                
                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor('peachpuff'))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor('peachpuff'))
                
                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor('honeydew'))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor('honeydew'))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor('red'))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor(45,45,45))
            

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(255,0,0)) 
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(255,0,0))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(68,65,65))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(68,65,65))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText,QColor('peachpuff'))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor('lightgray'))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, QColor('honeydew')) 
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, QColor('honeydew'))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor('peachpuff'))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor('peachpuff'))

            case 'winter':
                pal=QPalette()
                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, QColor(67,85,96))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, QColor(67,85,96))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, QColor(67,85,96))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, QColor(67,85,96)) 
                
                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, QColor(228,233,218))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, QColor(228,233,218))
                
                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, QColor(146,150,125))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, QColor('honeydew'))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, QColor('honeydew'))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.HighlightedText, QColor('honedew'))
            

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, QColor(67,85,96)) 
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, QColor(267,85,96))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, QColor(67,85,96))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, QColor(67,85,96))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText,QColor(228,233,218))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, QColor(228,233,218))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, QColor('honeydew')) 
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, QColor('honeydew'))

                pal.setColor(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, QColor(228,233,218))
                pal.setColor(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, QColor(228,233,218))
        return pal    
    
    @staticmethod
    def get_additional_colors(theme_name):
        addColors = {}
        match theme_name:
            
            case "brown":
                addColors['intro']='honeydew'
                return  addColors
            case 'winter':
                addColors['intro']='honeydew'    
