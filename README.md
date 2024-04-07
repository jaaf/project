# Bière
## WARNING
This software is  intended for a French speaking audience. If it is successful it might be translated in English.

Ce logiciel est pour une audience francophone. S’il connaissait un certain succès, il pourrait être traduit en Anglais
## Qu’est-ce que Bière ?
Bière est un logiciel de brassage destiné aux brasseurs à la maison. Il permet d’effectuer la plupart des calculs nécessaires au brassage de la bière.

Il est placé sous licence GPL et, en plus d’être libre, est entièrement gratuit.

Pour le moment, il est compatible avec les plateformes Windows et Linux.

**Une chaîne youtube met à votre disposition tous les **
[tutoriels d’installation et de prise en main de Bière](https://www.youtube.com/channel/UChFFMG1XequnuPoV36UBkZg) sur laquelle des playlists sont créées pour les différentes plateformes.

## Installation
L’installation de Bière peut se faire de deux manières:
- pour être utilisé avec une base de données mysql
- pour être utilisé avec une base de données sqlite3

La deuxième façon est recommandée, surtout si l’utilisateur n’est pas à l’aise avec l’installation de programme.

### Installation avec sqlite
#### Sur Windows
1- téléchargez l’exécutable correspondant (installateur) dans la liste des fichiers du dossier racine. Pour windows Bière-1.0-installer.exe, pour Linux Bière-1.0-installer.rpm ou Bière-1.0-installer.deb.

2- exécutez l’installateur. Une icône du programme sera placée sur le bureau.
3- lancez le programme en cliquant sur l’icône. Le programme démarre dans un terminal. Lorsqu’on vous pose une première question sur le type de base de données a utiliser, répondez **sqlite**.
Le programme démarre dans sa fenêtre. 
#### Sur Linux
1- téléchargez le fichier biere-1.0.rpm
2- retirez toute installation précédente avec la commande

    sudo dnf remove biere

3- Installez avec la commande

    sudo dnf localinstall biere-1.0.rpm
    


### Installation avec mysql
1- Installez le serveur de base de données mariadb en version 11.0.3. D’autres versions pourrait fonctionner mais le programme a été testé avec cette version seulement.

  1-a Dans un terminal utilisez la commande 
  
      user -u root -p
  
  puis saisissez le mot de passe d’administration du serveur mariadb.

  L’invite de commande de mariadb  devient 
    
> MariaDB [(none)]>

Pour toutes le commandes qui vont suivre, une réponse Query OK est attendue.

1-b Créez une base de données
Derrière cette invite, créez une base de données avec la commande suivante:

    create database biere1;

Vous pouvez changer le nom de la base de données si vous le souhaitez mais mémorisez-le.

1-c Utilisez cette base de données

    use biere1;

L’invite de commande devient

> 
MariaDB [(biere1)]>

1-d Créez un utilisateur et attribuez-lui un mot de passe

    create user biere@localhost identified by "bierepass"

Dans cette commande l’utilisateur biere@localhost est impératif. Par contre vous pouvez remplacer le mot de passe par celui de votre choix mais mémorisez-le

1-e Donnez les privilèges à cet utilisateur sur la base créée

    grant all privileges on biere1.* to biere@localhost;

biere1 doit bien sûr être remplacé par le nom de base que vous avez choisi précédemment.

Vous pouvez quitter le client du serveur avec 

    exit
#### Sur Windows
2- téléchargez l’exécutable correspondant (installateur) dans la liste des fichiers de dossier racine. Pour windows Bière-1.0-installer.exe, pour Linux Bière-1.0-installer.rpm ou Bière-1.0-installer.deb.

3- exécutez l’installateur. Une icône du programme sera placée sur le bureau.

4- lancez le programme en cliquant sur l’icône. Le programme démarre dans un terminal. Lorsqu’on vous pose une première question sur le type de base de données a utiliser, répondez **mysql**. Lorsqu’on vous demande le nom de la base répondez **biere1** ou le nom que vous auriez éventuellement choisi. Lorsqu’on vous demande le mot de passe donnez celui que vous avez saisi à  la commande 1-d.

#### Sur Linux
#### Sur Linux
1- téléchargez le fichier biere-1.0.rpm
2- retirez toute installation précédente avec la commande

    sudo dnf remove biere

3- Installez avec la commande

    sudo dnf localinstall biere-1.0.rpm
    
Le programme démarre dans sa fenêtre. 

